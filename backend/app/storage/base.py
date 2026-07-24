from typing import Protocol


class ObjectStorage(Protocol):
    name: str

    def put(self, key: str, content: bytes, *, content_type: str) -> str:
        ...

    def get(self, key: str) -> bytes:
        ...

    def delete(self, key: str) -> None:
        ...
