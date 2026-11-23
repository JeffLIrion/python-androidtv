"""Helpers for processing the output of the ``screencap -p`` command.

"""

#: The first bytes of the PNG file signature
PNG_SIGNATURE_START = b"\x89PNG"

#: Only look for the PNG signature this far into the output.  Some devices write a short text line to stdout before
#: the image (e.g., Fire OS: "Init wrapper sys mutex successful. Pid:1234\n").
MAX_SCREENCAP_PREFIX_LENGTH = 1024


def process_screencap_output(result):
    """Turn the raw output of ``screencap -p`` into a valid PNG image.

    1. Some devices write a text line before the PNG data when the output of ``screencap -p`` is read directly from
       the ADB stream, e.g. Fire OS on MediaTek-based TVs::

           Init wrapper sys mutex successful. Pid:1234\\n\\x89PNG\\r\\n\\x1a\\n...

       Everything before the PNG signature is removed.

    2. If the ADB shell translated ``\\n`` to ``\\r\\n``, this is undone.  This check has to be done after step 1,
       because it looks at the bytes right after the PNG signature.

    Parameters
    ----------
    result : bytes, None
        The output of the ``screencap -p`` command

    Returns
    -------
    bytes, None
        The screencap as a binary .png image (or ``result`` unchanged if it does not contain a PNG signature near the
        start)

    """
    if not result:
        return result

    start = result.find(PNG_SIGNATURE_START, 0, MAX_SCREENCAP_PREFIX_LENGTH)
    if start > 0:
        result = result[start:]

    if result[5:6] == b"\r":
        return result.replace(b"\r\n", b"\n")

    return result
