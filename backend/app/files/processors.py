from textwrap import wrap


SUPPORTED_TEXT_TYPES = {"txt", "markdown"}
SUPPORTED_FILE_TYPES = {*SUPPORTED_TEXT_TYPES, "pdf"}


class UnsupportedFileTypeError(ValueError):
    pass


class FileProcessor:
    def validate_type(self, file_type: str) -> None:
        if file_type not in SUPPORTED_FILE_TYPES:
            raise UnsupportedFileTypeError(f"Unsupported file type: {file_type}")

    def extract_text(self, *, file_type: str, content: str) -> str:
        self.validate_type(file_type)
        if file_type == "pdf":
            raise ValueError("PDF metadata is accepted, but PDF parsing is not available yet")
        return content.strip()

    def chunk_text(self, text: str, *, chunk_size: int = 700) -> list[str]:
        normalized = "\n".join(line.strip() for line in text.splitlines() if line.strip())
        if not normalized:
            return []
        return wrap(
            normalized,
            width=chunk_size,
            break_long_words=False,
            replace_whitespace=False,
        )

