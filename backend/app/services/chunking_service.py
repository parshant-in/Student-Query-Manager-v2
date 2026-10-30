"""Simple character-based text chunking with overlap."""


class ChunkingService:
    def __init__(self, chunk_size: int = 900, overlap: int = 120) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than zero")
        if overlap < 0 or overlap >= chunk_size:
            raise ValueError("overlap must be non-negative and smaller than chunk_size")
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_text(self, text: str) -> list[str]:
        clean_text = text.strip()
        if not clean_text:
            return []

        chunks: list[str] = []
        start = 0
        while start < len(clean_text):
            chunk = clean_text[start : start + self.chunk_size].strip()
            if chunk:
                chunks.append(chunk)
            if start + self.chunk_size >= len(clean_text):
                break
            start += self.chunk_size - self.overlap
        return chunks
