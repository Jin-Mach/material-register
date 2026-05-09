import unicodedata

def normalize_text(text: str | None) -> str | None:
    if text is None:
        return None
    text = str(text).strip()
    text = unicodedata.normalize("NFKD", text)
    result_chars = []
    for char in text:
        if not unicodedata.combining(char):
            result_chars.append(char)
    result = "".join(result_chars)
    result = result.casefold()
    result = result.replace("’", "'")
    result = " ".join(result.split())
    return result

def normalize_whitespace(text: str | None) -> str | None:
    if text is None:
        return None
    return " ".join(str(text).split())