"""Capture Android framebuffers over ADB and encode them as PNG.

``screencap -p`` makes the device CPU encode the PNG. Two binary alternatives
avoid that: plain ``screencap`` (raw pixels, decoded on the host) and
``screencap | gzip -1`` (raw pixels gzipped on the device). Neither path is
always faster: on one Hi3751V350 projector the medians were 7.4 s for
``screencap -p``, about 2.5 s for raw ``screencap`` read binary (0.7 s grab
plus transfer of 8.3 MB), and about 4.1 s for the gzip path. Callers time each
path back to back on first use and keep the fastest valid one for that
device. The host parses the Android framebuffer header and encodes the PNG
itself using only the standard library.
"""

import gzip
import struct
import sys
import zlib
from array import array

RAW_SCREENCAP_COMMAND = "screencap"

GZIP_SCREENCAP_COMMAND = "screencap | gzip -1"

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"

# Android ``PixelFormat`` values we can decode: format -> bytes per pixel.
_BYTES_PER_PIXEL = {1: 4, 2: 4, 3: 3, 4: 2, 5: 4}

_EXPAND_5 = bytes((c << 3) | (c >> 2) for c in range(32))
_EXPAND_6 = bytes((c << 2) | (c >> 4) for c in range(64))


class ScreencapError(Exception):
    """A compressed screencap could not be transferred or decoded."""


class UnsupportedScreencapFormatError(ScreencapError):
    """The framebuffer uses a pixel format this decoder does not handle."""


def decode_gzip_screencap(data):
    """Decode the raw gzip output of :data:`GZIP_SCREENCAP_COMMAND`.

    Parameters
    ----------
    data : bytes
        The raw bytes printed by the device shell

    Returns
    -------
    bytes
        The screencap as a binary .png image

    Raises
    ------
    ScreencapError
        If the data is not valid gzip or the framebuffer is truncated
    UnsupportedScreencapFormatError
        If the framebuffer pixel format is not supported

    """
    try:
        raw = gzip.decompress(data)
    except (ValueError, OSError, EOFError, zlib.error) as err:
        raise ScreencapError(f"Corrupt gzip screencap: {err}") from err
    return decode_framebuffer(raw)


def decode_framebuffer(raw):
    """Convert a raw Android framebuffer dump (``screencap`` without ``-p``) to PNG.

    The dump starts with little-endian ``width``, ``height`` and ``format``
    fields. Android 10+ adds a ``dataspace`` field, so the header is either 12
    or 16 bytes long; the header length is inferred from the total length.

    Parameters
    ----------
    raw : bytes
        The raw framebuffer dump

    Returns
    -------
    bytes
        The screencap as a binary .png image

    """
    if len(raw) < 12:
        raise ScreencapError("Truncated screencap header")
    width, height, pixel_format = struct.unpack_from("<III", raw)
    if pixel_format not in _BYTES_PER_PIXEL:
        raise UnsupportedScreencapFormatError(f"Unsupported framebuffer pixel format {pixel_format}")
    if width == 0 or height == 0:
        raise ScreencapError(f"Invalid screencap dimensions {width}x{height}")

    pixel_bytes = width * height * _BYTES_PER_PIXEL[pixel_format]
    header_bytes = len(raw) - pixel_bytes
    if header_bytes < 12:
        raise ScreencapError("Truncated screencap pixel data")
    if header_bytes not in (12, 16):
        raise ScreencapError("Unexpected screencap header length")
    return _encode_png(width, height, pixel_format, raw[header_bytes:])


def _encode_png(width, height, pixel_format, pixels):
    """Encode framebuffer pixels as PNG, keeping alpha only when the source has it."""
    count = width * height
    if pixel_format == 1:
        color_type, rgb = 6, pixels
    elif pixel_format == 5:
        color_type, rgb = 6, _bgra_to_rgba(pixels)
    elif pixel_format == 2:
        color_type = 2
        rgb = bytearray(count * 3)
        rgb[0::3] = pixels[0::4]
        rgb[1::3] = pixels[1::4]
        rgb[2::3] = pixels[2::4]
    elif pixel_format == 3:
        color_type, rgb = 2, pixels
    else:
        color_type, rgb = 2, _rgb565_to_rgb(pixels, count)

    channels = 4 if color_type == 6 else 3
    stride = width * channels
    # Each scanline is prefixed with filter type 0 (None), which bytearray zero-fills.
    scanlines = bytearray((stride + 1) * height)
    view = memoryview(rgb)
    for row in range(height):
        start = row * stride
        scanlines[row * (stride + 1) + 1 : (row + 1) * (stride + 1)] = view[start : start + stride]

    ihdr = struct.pack(">IIBBBBB", width, height, 8, color_type, 0, 0, 0)
    return b"".join(
        (
            PNG_SIGNATURE,
            _png_chunk(b"IHDR", ihdr),
            _png_chunk(b"IDAT", zlib.compress(scanlines, 1)),
            _png_chunk(b"IEND", b""),
        )
    )


def _png_chunk(tag, data):
    crc = zlib.crc32(data, zlib.crc32(tag)) & 0xFFFFFFFF
    return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", crc)


def _bgra_to_rgba(pixels):
    out = bytearray(len(pixels))
    out[0::4] = pixels[2::4]
    out[1::4] = pixels[1::4]
    out[2::4] = pixels[0::4]
    out[3::4] = pixels[3::4]
    return out


def _rgb565_to_rgb(pixels, count):
    """Expand little-endian RGB_565 (red in the top five bits) to 8-bit RGB."""
    values = array("H")
    values.frombytes(pixels)
    if sys.byteorder == "big":
        values.byteswap()
    out = bytearray(count * 3)
    out[0::3] = bytes(_EXPAND_5[v >> 11] for v in values)
    out[1::3] = bytes(_EXPAND_6[(v >> 5) & 0x3F] for v in values)
    out[2::3] = bytes(_EXPAND_5[v & 0x1F] for v in values)
    return out
