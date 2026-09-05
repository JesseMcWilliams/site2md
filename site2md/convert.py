from __future__ import annotations

import io

from markitdown import MarkItDown, StreamInfo

_converter = MarkItDown()


def html_to_markdown(html: str, url: str) -> str:
    stream_info = StreamInfo(mimetype="text/html", url=url)
    result = _converter.convert_stream(io.BytesIO(html.encode("utf-8")), stream_info=stream_info)
    return result.markdown
