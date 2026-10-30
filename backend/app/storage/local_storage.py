"""Local file storage for uploaded documents."""

from pathlib import Path
from uuid import uuid4


class LocalDocumentStorage:
    def __init__(self, base_path: Path) -> None:
        self.base_path = base_path
        self.base_path.mkdir(parents=True, exist_ok=True)

    def save(self, filename: str, content: bytes) -> Path:
        extension = Path(filename).suffix.lower()

        stored_filename = f"{uuid4()}{extension}"
        file_path = self.base_path / stored_filename

        file_path.write_bytes(content)

        return file_path
        
    def delete(self, file_path: Path) -> None:
        if file_path.exists():
            file_path.unlink()