from backend.app.files.processors import FileProcessor, UnsupportedFileTypeError


class FileService:
    def __init__(self, processor: FileProcessor | None = None) -> None:
        self._processor = processor or FileProcessor()

    def validate(self, file_type: str) -> None:
        self._processor.validate_type(file_type)

    def extract_text(self, *, file_type: str, content: str) -> str:
        return self._processor.extract_text(file_type=file_type, content=content)

    def chunk_text(self, text: str) -> list[str]:
        return self._processor.chunk_text(text)


__all__ = ["FileService", "UnsupportedFileTypeError"]

