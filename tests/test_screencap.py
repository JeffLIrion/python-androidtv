import sys
import unittest

sys.path.insert(0, "..")

from androidtv.adb_manager.screencap import MAX_SCREENCAP_PREFIX_LENGTH, process_screencap_output


PNG_IMAGE = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\n\x00\x00\x00\n\x08\x06\x00\x00\x00\x8d2\xcf\xbd\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\x00\x00\tpHYs\x00\x00\x0fa\x00\x00\x0fa\x01\xa8?\xa7i\x00\x00\x00\x0eIDAT\x18\x95c`\x18\x05\x83\x13\x00\x00\x01\x9a\x00\x01\x16\xca\xd3i\x00\x00\x00\x00IEND\xaeB`\x82"

PNG_IMAGE_NEEDS_REPLACING = PNG_IMAGE[:5] + b"\r" + PNG_IMAGE[5:]

# Fire OS writes a text line to stdout before the PNG data (python-androidtv#377)
SCREENCAP_PREFIX = b"Init wrapper sys mutex successful. Pid:9508\n"


class TestProcessScreencapOutput(unittest.TestCase):
    def test_empty(self):
        """Test that ``None`` and empty output are returned unchanged."""
        self.assertIsNone(process_screencap_output(None))
        self.assertEqual(process_screencap_output(b""), b"")

    def test_png(self):
        """Test that a PNG image without a prefix is returned unchanged."""
        self.assertEqual(process_screencap_output(PNG_IMAGE), PNG_IMAGE)

    def test_png_needs_replacing(self):
        """Test that ``\\r\\n`` is replaced with ``\\n`` (existing behavior)."""
        self.assertEqual(process_screencap_output(PNG_IMAGE_NEEDS_REPLACING), PNG_IMAGE)

    def test_prefix(self):
        """Test that a text line before the PNG data is removed."""
        self.assertEqual(process_screencap_output(SCREENCAP_PREFIX + PNG_IMAGE), PNG_IMAGE)

    def test_prefix_needs_replacing(self):
        """Test that the prefix is removed before the ``\\r\\n`` check."""
        self.assertEqual(process_screencap_output(SCREENCAP_PREFIX + PNG_IMAGE_NEEDS_REPLACING), PNG_IMAGE)

        # The prefix itself may also end with "\r\n"
        self.assertEqual(
            process_screencap_output(SCREENCAP_PREFIX.replace(b"\n", b"\r\n") + PNG_IMAGE_NEEDS_REPLACING), PNG_IMAGE
        )

    def test_multiple_lines_before_png(self):
        """Test that several text lines before the PNG data are removed (e.g., Xiaomi: "open mma dev failed")."""
        prefix = SCREENCAP_PREFIX + b"open mma dev failed\n"
        self.assertEqual(process_screencap_output(prefix + PNG_IMAGE), PNG_IMAGE)

    def test_no_png(self):
        """Test that output without a PNG signature is returned unchanged."""
        self.assertEqual(
            process_screencap_output(b"/system/bin/sh: screencap: not found\n"),
            b"/system/bin/sh: screencap: not found\n",
        )

    def test_png_signature_too_far(self):
        """Test that a PNG signature beyond ``MAX_SCREENCAP_PREFIX_LENGTH`` bytes is not used."""
        output = b"x" * MAX_SCREENCAP_PREFIX_LENGTH + PNG_IMAGE
        self.assertEqual(process_screencap_output(output), output)


if __name__ == "__main__":
    unittest.main()
