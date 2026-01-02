import re


class XMLParser:
    """XML parsing utilities."""

    @staticmethod
    def extract_tag(text: str, tag: str) -> str | None:
        """
        Extract content from XML tag using regex.
        """
        pattern = f"<{tag}>(.*?)</{tag}>"
        match = re.search(pattern, text, re.DOTALL)
        return match.group(1).strip() if match else None
