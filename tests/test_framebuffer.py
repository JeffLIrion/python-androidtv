import base64
import gzip
import struct
import unittest
import zlib
from unittest.mock import Mock, patch

from androidtv import framebuffer
from androidtv.basetv.basetv_sync import BaseTVSync
from androidtv.basetv.basetv_async import BaseTVAsync
from .async_patchers import AsyncMock
from .async_wrapper import awaiter


PNG_IMAGE = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\n\x00\x00\x00\n\x08\x06\x00\x00\x00\x8d2\xcf\xbd\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\x00\x00\tpHYs\x00\x00\x0fa\x00\x00\x0fa\x01\xa8?\xa7i\x00\x00\x00\x0eIDAT\x18\x95c`\x18\x05\x83\x13\x00\x00\x01\x9a\x00\x01\x16\xca\xd3i\x00\x00\x00\x00IEND\xaeB`\x82"


def _header(width, height, pixel_format, dataspace=None):
    if dataspace is None:
        return struct.pack("<III", width, height, pixel_format)
    return struct.pack("<IIII", width, height, pixel_format, dataspace)


def _parse_png(png):
    """Return (width, height, color_type, scanlines) for a PNG written by framebuffer."""
    assert png.startswith(framebuffer.PNG_SIGNATURE)
    offset = len(framebuffer.PNG_SIGNATURE)
    chunks = {}
    while offset < len(png):
        (length,) = struct.unpack_from(">I", png, offset)
        tag = png[offset + 4 : offset + 8]
        data = png[offset + 8 : offset + 8 + length]
        (crc,) = struct.unpack_from(">I", png, offset + 8 + length)
        assert crc == zlib.crc32(tag + data) & 0xFFFFFFFF
        chunks[tag] = data
        offset += 12 + length
    width, height, depth, color_type, _, _, _ = struct.unpack(">IIBBBBB", chunks[b"IHDR"])
    assert depth == 8
    return width, height, color_type, zlib.decompress(chunks[b"IDAT"])


def _rows(scanlines, height, stride):
    """Strip the per-row filter byte and return the pixel bytes of each row."""
    row_len = stride + 1
    rows = []
    for row in range(height):
        line = scanlines[row * row_len : (row + 1) * row_len]
        assert line[0] == 0
        rows.append(line[1:])
    return rows


class TestDecodeFramebuffer(unittest.TestCase):
    def test_rgba_header_12(self):
        raw = _header(2, 1, 1) + bytes([1, 2, 3, 4, 5, 6, 7, 8])
        width, height, color_type, scanlines = _parse_png(framebuffer.decode_framebuffer(raw))
        self.assertEqual((width, height, color_type), (2, 1, 6))
        self.assertEqual(_rows(scanlines, 1, 8), [bytes([1, 2, 3, 4, 5, 6, 7, 8])])

    def test_rgba_header_16_with_dataspace(self):
        raw = _header(1, 2, 1, dataspace=0) + bytes(range(8))
        width, height, color_type, scanlines = _parse_png(framebuffer.decode_framebuffer(raw))
        self.assertEqual((width, height, color_type), (1, 2, 6))
        self.assertEqual(_rows(scanlines, 2, 4), [bytes(range(4)), bytes(range(4, 8))])

    def test_bgra_is_swapped_to_rgba(self):
        raw = _header(1, 1, 5) + bytes([10, 20, 30, 40])
        _, _, color_type, scanlines = _parse_png(framebuffer.decode_framebuffer(raw))
        self.assertEqual(color_type, 6)
        self.assertEqual(_rows(scanlines, 1, 4), [bytes([30, 20, 10, 40])])

    def test_rgbx_drops_padding_byte(self):
        raw = _header(2, 1, 2) + bytes([1, 2, 3, 0, 4, 5, 6, 0])
        _, _, color_type, scanlines = _parse_png(framebuffer.decode_framebuffer(raw))
        self.assertEqual(color_type, 2)
        self.assertEqual(_rows(scanlines, 1, 6), [bytes([1, 2, 3, 4, 5, 6])])

    def test_rgb888(self):
        raw = _header(1, 2, 3) + bytes([1, 2, 3, 4, 5, 6])
        _, _, color_type, scanlines = _parse_png(framebuffer.decode_framebuffer(raw))
        self.assertEqual(color_type, 2)
        self.assertEqual(_rows(scanlines, 2, 3), [bytes([1, 2, 3]), bytes([4, 5, 6])])

    def test_rgb565_expands_to_8_bit(self):
        white = struct.pack("<H", 0xFFFF)
        red = struct.pack("<H", 0xF800)
        raw = _header(2, 1, 4) + white + red
        _, _, color_type, scanlines = _parse_png(framebuffer.decode_framebuffer(raw))
        self.assertEqual(color_type, 2)
        self.assertEqual(_rows(scanlines, 1, 6), [bytes([255, 255, 255, 255, 0, 0])])

    def test_unsupported_format_raises(self):
        raw = _header(1, 1, 43) + bytes(4)
        with self.assertRaises(framebuffer.UnsupportedScreencapFormatError):
            framebuffer.decode_framebuffer(raw)

    def test_truncated_header_raises(self):
        with self.assertRaises(framebuffer.ScreencapError):
            framebuffer.decode_framebuffer(bytes(11))

    def test_truncated_pixels_raise(self):
        raw = _header(2, 2, 1) + bytes(4)
        with self.assertRaises(framebuffer.ScreencapError):
            framebuffer.decode_framebuffer(raw)

    def test_zero_dimensions_raise(self):
        with self.assertRaises(framebuffer.ScreencapError):
            framebuffer.decode_framebuffer(_header(0, 1, 1) + bytes(4))


class TestDecodeGzipScreencap(unittest.TestCase):
    def test_round_trip(self):
        raw = _header(1, 1, 1) + bytes([9, 8, 7, 6])
        png = framebuffer.decode_gzip_screencap(gzip.compress(raw))
        self.assertEqual(_parse_png(png)[3], b"\x00" + bytes([9, 8, 7, 6]))

    def test_corrupt_gzip_raises_screencap_error(self):
        with self.assertRaises(framebuffer.ScreencapError):
            framebuffer.decode_gzip_screencap(gzip.compress(_header(1, 1, 1) + bytes(4))[:-6])

    def test_non_gzip_raises_screencap_error(self):
        with self.assertRaises(framebuffer.ScreencapError):
            framebuffer.decode_gzip_screencap(b"not gzip at all")

    def test_truncated_compressed_frame_raises(self):
        with self.assertRaises(framebuffer.ScreencapError):
            framebuffer.decode_gzip_screencap(gzip.compress(bytes(11)))

    def test_corrupted_gzip_bytes_fail_crc(self):
        raw = _header(1, 1, 1) + bytes([9, 8, 7, 6])
        mangled = bytearray(gzip.compress(raw))
        mangled[10] ^= 0xFF
        with self.assertRaises(framebuffer.ScreencapError):
            framebuffer.decode_gzip_screencap(bytes(mangled))


class TestAdbScreencap(unittest.TestCase):
    def setUp(self):
        self.btv = BaseTVSync.__new__(BaseTVSync)
        self.btv._adb = Mock()
        self.btv._adb.screencap.return_value = PNG_IMAGE
        self.raw = _header(1, 1, 1) + bytes([1, 2, 3, 4])
        self.gzipped = gzip.compress(self.raw)
        self.btv._adb.shell_binary.side_effect = lambda cmd: (
            self.raw if cmd == framebuffer.RAW_SCREENCAP_COMMAND else self.gzipped
        )

    def test_calibration_picks_fastest_raw(self):
        with patch("androidtv.basetv.basetv_sync.monotonic", side_effect=[0, 1, 1, 5, 5, 6]):
            png = self.btv.adb_screencap()
        self.assertEqual(_parse_png(png)[0:2], (1, 1))
        self.assertEqual(self.btv._screencap_method, "raw")
        self.btv._adb.shell_binary.reset_mock()
        self.btv._adb.screencap.reset_mock()
        png = self.btv.adb_screencap()
        self.assertEqual(_parse_png(png)[0:2], (1, 1))
        self.btv._adb.shell_binary.assert_called_once_with(framebuffer.RAW_SCREENCAP_COMMAND)
        self.btv._adb.screencap.assert_not_called()

    def test_calibration_picks_fastest_gzip(self):
        with patch("androidtv.basetv.basetv_sync.monotonic", side_effect=[0, 5, 5, 6, 6, 10]):
            png = self.btv.adb_screencap()
        self.assertEqual(_parse_png(png)[0:2], (1, 1))
        self.assertEqual(self.btv._screencap_method, "gzip")
        self.btv._adb.shell_binary.reset_mock()
        self.btv._adb.screencap.reset_mock()
        png = self.btv.adb_screencap()
        self.assertEqual(_parse_png(png)[0:2], (1, 1))
        self.btv._adb.shell_binary.assert_called_once_with(framebuffer.GZIP_SCREENCAP_COMMAND)
        self.btv._adb.screencap.assert_not_called()

    def test_calibration_picks_fastest_native(self):
        with patch("androidtv.basetv.basetv_sync.monotonic", side_effect=[0, 5, 5, 9, 9, 10]):
            self.assertEqual(self.btv.adb_screencap(), PNG_IMAGE)
        self.assertEqual(self.btv._screencap_method, "native")
        self.btv._adb.shell_binary.reset_mock()
        self.btv._adb.screencap.reset_mock()
        self.assertEqual(self.btv.adb_screencap(), PNG_IMAGE)
        self.btv._adb.shell_binary.assert_not_called()
        self.btv._adb.screencap.assert_called_once_with()

    def test_invalid_candidates_are_discarded(self):
        mangled_raw = self.raw.replace(b"\n", b"\r\n")
        if len(mangled_raw) == len(self.raw):
            mangled_raw = self.raw + b"\r"
        self.btv._adb.shell_binary.side_effect = lambda cmd: (
            mangled_raw if cmd == framebuffer.RAW_SCREENCAP_COMMAND else b"not gzip"
        )
        with patch("androidtv.basetv.basetv_sync.monotonic", side_effect=[0, 1, 1, 2, 2, 3]):
            self.assertEqual(self.btv.adb_screencap(), PNG_IMAGE)
        self.assertEqual(self.btv._screencap_method, "native")

    def test_pinned_failure_falls_back_to_native(self):
        with patch("androidtv.basetv.basetv_sync.monotonic", side_effect=[0, 1, 1, 5, 5, 6]):
            self.btv.adb_screencap()
        self.assertEqual(self.btv._screencap_method, "raw")
        self.btv._adb.shell_binary.side_effect = lambda cmd: b"garbage"
        self.assertEqual(self.btv.adb_screencap(), PNG_IMAGE)
        self.assertEqual(self.btv._screencap_method, "native")

    def test_server_path_without_binary_shell_uses_native(self):
        del self.btv._adb.shell_binary
        self.assertEqual(self.btv.adb_screencap(), PNG_IMAGE)
        self.assertEqual(self.btv._screencap_method, "native")

    def test_reconnect_recalibrates(self):
        with patch("androidtv.basetv.basetv_sync.monotonic", side_effect=[0, 5, 5, 9, 9, 10]):
            self.assertEqual(self.btv.adb_screencap(), PNG_IMAGE)
        self.assertEqual(self.btv._screencap_method, "native")
        self.btv.adb_connect()
        self.assertIsNone(self.btv._screencap_method)
        with patch("androidtv.basetv.basetv_sync.monotonic", side_effect=[0, 1, 1, 5, 5, 6]):
            png = self.btv.adb_screencap()
        self.assertEqual(_parse_png(png)[0:2], (1, 1))
        self.assertEqual(self.btv._screencap_method, "raw")


class TestAdbScreencapFallbacks(unittest.TestCase):
    def setUp(self):
        self.btv = BaseTVSync.__new__(BaseTVSync)
        self.btv._adb = Mock()
        self.btv._adb.screencap.return_value = PNG_IMAGE
        self.raw = _header(1, 1, 1) + bytes([1, 2, 3, 4])
        self.gzipped = gzip.compress(self.raw)

    def test_pinned_raw_empty_output_uses_native(self):
        self.btv._screencap_method = "raw"
        self.btv._adb.shell_binary.return_value = b""
        self.assertEqual(self.btv.adb_screencap(), PNG_IMAGE)
        self.assertEqual(self.btv._screencap_method, "native")

    def test_pinned_raw_none_output_uses_native(self):
        self.btv._screencap_method = "raw"
        self.btv._adb.shell_binary.return_value = None
        self.assertEqual(self.btv.adb_screencap(), PNG_IMAGE)
        self.assertEqual(self.btv._screencap_method, "native")

    def test_pinned_gzip_empty_output_uses_native(self):
        self.btv._screencap_method = "gzip"
        self.btv._adb.shell_binary.return_value = b""
        self.assertEqual(self.btv.adb_screencap(), PNG_IMAGE)
        self.assertEqual(self.btv._screencap_method, "native")

    def test_pinned_gzip_decode_failure_uses_native(self):
        self.btv._screencap_method = "gzip"
        self.btv._adb.shell_binary.return_value = b"not gzip"
        self.assertEqual(self.btv.adb_screencap(), PNG_IMAGE)
        self.assertEqual(self.btv._screencap_method, "native")

    def test_pinned_gzip_without_binary_shell_uses_native(self):
        self.btv._screencap_method = "gzip"
        del self.btv._adb.shell_binary
        self.assertEqual(self.btv.adb_screencap(), PNG_IMAGE)
        self.assertEqual(self.btv._screencap_method, "native")

    def test_calibration_without_binary_shell_uses_native(self):
        del self.btv._adb.shell_binary
        self.assertEqual(self.btv.adb_screencap(), PNG_IMAGE)
        self.assertEqual(self.btv._screencap_method, "native")

    def test_calibration_without_any_valid_candidate_returns_none(self):
        self.btv._adb.shell_binary.return_value = b""
        self.btv._adb.screencap.return_value = None
        with patch("androidtv.basetv.basetv_sync.monotonic", side_effect=range(10)):
            self.assertIsNone(self.btv.adb_screencap())
        self.assertEqual(self.btv._screencap_method, "native")

    def test_calibration_skips_undecodable_candidate(self):
        self.btv._adb.shell_binary.side_effect = lambda cmd: (
            b"garbage" if cmd == framebuffer.RAW_SCREENCAP_COMMAND else self.gzipped
        )
        with patch("androidtv.basetv.basetv_sync.monotonic", side_effect=[0, 1, 5, 5, 6]):
            self.assertEqual(self.btv.adb_screencap(), PNG_IMAGE)
        self.assertEqual(self.btv._screencap_method, "native")


class TestAdbScreencapFallbacksAsync(unittest.TestCase):
    def setUp(self):
        self.btv = BaseTVAsync.__new__(BaseTVAsync)
        self.btv._adb = Mock()
        self.btv._adb.screencap = AsyncMock(return_value=PNG_IMAGE)
        self.raw = _header(1, 1, 1) + bytes([1, 2, 3, 4])
        self.gzipped = gzip.compress(self.raw)

    @awaiter
    async def test_pinned_raw_empty_output_uses_native(self):
        self.btv._screencap_method = "raw"
        self.btv._adb.shell_binary = AsyncMock(return_value=b"")
        self.assertEqual(await self.btv.adb_screencap(), PNG_IMAGE)
        self.assertEqual(self.btv._screencap_method, "native")

    @awaiter
    async def test_pinned_raw_none_output_uses_native(self):
        self.btv._screencap_method = "raw"
        self.btv._adb.shell_binary = AsyncMock(return_value=None)
        self.assertEqual(await self.btv.adb_screencap(), PNG_IMAGE)
        self.assertEqual(self.btv._screencap_method, "native")

    @awaiter
    async def test_pinned_gzip_empty_output_uses_native(self):
        self.btv._screencap_method = "gzip"
        self.btv._adb.shell_binary = AsyncMock(return_value=b"")
        self.assertEqual(await self.btv.adb_screencap(), PNG_IMAGE)
        self.assertEqual(self.btv._screencap_method, "native")

    @awaiter
    async def test_pinned_gzip_decode_failure_uses_native(self):
        self.btv._screencap_method = "gzip"
        self.btv._adb.shell_binary = AsyncMock(return_value=b"not gzip")
        self.assertEqual(await self.btv.adb_screencap(), PNG_IMAGE)
        self.assertEqual(self.btv._screencap_method, "native")

    @awaiter
    async def test_pinned_gzip_without_binary_shell_uses_native(self):
        self.btv._screencap_method = "gzip"
        del self.btv._adb.shell_binary
        self.assertEqual(await self.btv.adb_screencap(), PNG_IMAGE)
        self.assertEqual(self.btv._screencap_method, "native")

    @awaiter
    async def test_calibration_without_binary_shell_uses_native(self):
        del self.btv._adb.shell_binary
        self.assertEqual(await self.btv.adb_screencap(), PNG_IMAGE)
        self.assertEqual(self.btv._screencap_method, "native")

    @awaiter
    async def test_calibration_without_any_valid_candidate_returns_none(self):
        self.btv._adb.shell_binary = AsyncMock(return_value=b"")
        self.btv._adb.screencap = AsyncMock(return_value=None)
        with patch("androidtv.basetv.basetv_async.monotonic", side_effect=range(10)):
            self.assertIsNone(await self.btv.adb_screencap())
        self.assertEqual(self.btv._screencap_method, "native")

    @awaiter
    async def test_calibration_skips_undecodable_candidate(self):
        async def mixed_shell(cmd):
            return b"garbage" if cmd == framebuffer.RAW_SCREENCAP_COMMAND else self.gzipped

        self.btv._adb.shell_binary = AsyncMock(side_effect=mixed_shell)
        with patch("androidtv.basetv.basetv_async.monotonic", side_effect=[0, 1, 5, 5, 6]):
            self.assertEqual(await self.btv.adb_screencap(), PNG_IMAGE)
        self.assertEqual(self.btv._screencap_method, "native")


class TestRgb565ByteOrder(unittest.TestCase):
    def test_big_endian_host_byteswaps_pixels(self):
        with patch.object(framebuffer.sys, "byteorder", "big"):
            self.assertEqual(framebuffer._rgb565_to_rgb(b"\xf8\x00", 1), bytes([255, 0, 0]))


class TestAdbScreencapAsync(unittest.TestCase):
    def setUp(self):
        self.btv = BaseTVAsync.__new__(BaseTVAsync)
        self.btv._adb = Mock()
        self.btv._adb.screencap = AsyncMock(return_value=PNG_IMAGE)
        self.btv._adb.connect = AsyncMock(return_value=True)
        self.raw = _header(1, 1, 1) + bytes([1, 2, 3, 4])
        self.gzipped = gzip.compress(self.raw)
        self.btv._adb.shell_binary = AsyncMock(side_effect=self._shell_binary)

    async def _shell_binary(self, cmd):
        if cmd == framebuffer.RAW_SCREENCAP_COMMAND:
            return self.raw
        return self.gzipped

    @awaiter
    async def test_calibration_picks_fastest_raw(self):
        with patch("androidtv.basetv.basetv_async.monotonic", side_effect=[0, 1, 1, 5, 5, 6]):
            png = await self.btv.adb_screencap()
        self.assertEqual(_parse_png(png)[3], b"\x00\x01\x02\x03\x04")
        self.assertEqual(self.btv._screencap_method, "raw")
        self.btv._adb.shell_binary.reset_mock()
        self.btv._adb.screencap.reset_mock()
        png = await self.btv.adb_screencap()
        self.assertEqual(_parse_png(png)[3], b"\x00\x01\x02\x03\x04")
        self.btv._adb.shell_binary.assert_called_once_with(framebuffer.RAW_SCREENCAP_COMMAND)
        self.btv._adb.screencap.assert_not_called()

    @awaiter
    async def test_calibration_picks_fastest_gzip(self):
        with patch("androidtv.basetv.basetv_async.monotonic", side_effect=[0, 5, 5, 6, 6, 10]):
            png = await self.btv.adb_screencap()
        self.assertEqual(_parse_png(png)[3], b"\x00\x01\x02\x03\x04")
        self.assertEqual(self.btv._screencap_method, "gzip")
        self.btv._adb.shell_binary.reset_mock()
        self.btv._adb.screencap.reset_mock()
        png = await self.btv.adb_screencap()
        self.assertEqual(_parse_png(png)[3], b"\x00\x01\x02\x03\x04")
        self.btv._adb.shell_binary.assert_called_once_with(framebuffer.GZIP_SCREENCAP_COMMAND)
        self.btv._adb.screencap.assert_not_called()

    @awaiter
    async def test_calibration_picks_fastest_native(self):
        with patch("androidtv.basetv.basetv_async.monotonic", side_effect=[0, 5, 5, 9, 9, 10]):
            self.assertEqual(await self.btv.adb_screencap(), PNG_IMAGE)
        self.assertEqual(self.btv._screencap_method, "native")
        self.btv._adb.shell_binary.reset_mock()
        self.btv._adb.screencap.reset_mock()
        self.assertEqual(await self.btv.adb_screencap(), PNG_IMAGE)
        self.btv._adb.shell_binary.assert_not_called()
        self.btv._adb.screencap.assert_called_once_with()

    @awaiter
    async def test_invalid_candidates_are_discarded(self):
        mangled_raw = self.raw.replace(b"\n", b"\r\n")
        if len(mangled_raw) == len(self.raw):
            mangled_raw = self.raw + b"\r"

        async def bad_shell(cmd):
            return mangled_raw if cmd == framebuffer.RAW_SCREENCAP_COMMAND else b"not gzip"

        self.btv._adb.shell_binary = AsyncMock(side_effect=bad_shell)
        with patch("androidtv.basetv.basetv_async.monotonic", side_effect=[0, 1, 1, 2, 2, 3]):
            self.assertEqual(await self.btv.adb_screencap(), PNG_IMAGE)
        self.assertEqual(self.btv._screencap_method, "native")

    @awaiter
    async def test_pinned_failure_falls_back_to_native(self):
        with patch("androidtv.basetv.basetv_async.monotonic", side_effect=[0, 1, 1, 5, 5, 6]):
            await self.btv.adb_screencap()
        self.assertEqual(self.btv._screencap_method, "raw")
        self.btv._adb.shell_binary = AsyncMock(return_value=b"garbage")
        self.assertEqual(await self.btv.adb_screencap(), PNG_IMAGE)
        self.assertEqual(self.btv._screencap_method, "native")

    @awaiter
    async def test_server_path_without_binary_shell_uses_native(self):
        del self.btv._adb.shell_binary
        self.assertEqual(await self.btv.adb_screencap(), PNG_IMAGE)
        self.assertEqual(self.btv._screencap_method, "native")

    @awaiter
    async def test_reconnect_recalibrates(self):
        with patch("androidtv.basetv.basetv_async.monotonic", side_effect=[0, 5, 5, 9, 9, 10]):
            self.assertEqual(await self.btv.adb_screencap(), PNG_IMAGE)
        self.assertEqual(self.btv._screencap_method, "native")
        await self.btv.adb_connect()
        self.assertIsNone(self.btv._screencap_method)
        with patch("androidtv.basetv.basetv_async.monotonic", side_effect=[0, 1, 1, 5, 5, 6]):
            png = await self.btv.adb_screencap()
        self.assertEqual(_parse_png(png)[3], b"\x00\x01\x02\x03\x04")
        self.assertEqual(self.btv._screencap_method, "raw")

    @awaiter
    async def test_transport_failure_remains_an_error(self):
        self.btv._adb.shell_binary = AsyncMock(side_effect=ConnectionResetError)
        with self.assertRaises(ConnectionResetError):
            await self.btv.adb_screencap()
