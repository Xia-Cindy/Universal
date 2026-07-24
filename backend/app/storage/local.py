from pathlib import Path


class LocalObjectStorage:
    name = "local"

    def __init__(self, root: str = "storage/objects") -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def put(self, key: str, content: bytes, *, content_type: str) -> str:
        path = self.root / key
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return key

    def get(self, key: str) -> bytes:
        return (self.root / key).read_bytes()

    def delete(self, key: str) -> None:
        path = self.root / key
        if path.exists():
            path.unlink()
