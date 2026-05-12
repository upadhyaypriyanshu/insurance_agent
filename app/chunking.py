import re
from typing import List


def normalize_text(text: str, preserve_newlines: bool = False) -> str:
    text = text or ""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    if preserve_newlines:
        text = re.sub(r"[ \t]+", " ", text)
    else:
        text = re.sub(r"\s+", " ", text)
    return text.strip()


def split_into_chunks(text: str, chunk_size: int = 1000) -> List[str]:
    text = normalize_text(text)
    return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]
