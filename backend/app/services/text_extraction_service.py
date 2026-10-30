"""Extract plain text from supported local document files."""

from pathlib import Path

from pypdf import PdfReader


class TextExtractionError(Exception):
    """Raised when a supported document cannot be read as text."""


class TextExtractionService:
    def extract_text(self, file_path: str | Path) -> str:
        path = Path(file_path)
        if not path.is_file():
            raise FileNotFoundError(f"Document file does not exist: {path}")

        extension = path.suffix.casefold()
        if extension == ".txt":
            try:
                return path.read_text(encoding="utf-8")
            except UnicodeDecodeError as exc:
                raise TextExtractionError("TXT file is not valid UTF-8 text") from exc
        if extension == ".pdf":
            try:
                reader = PdfReader(str(path))
                return "\n".join(page.extract_text() or "" for page in reader.pages)
            except Exception as exc:
                raise TextExtractionError("Could not extract text from PDF file") from exc

        raise ValueError(f"Unsupported document extension: {extension or '(none)'}")
