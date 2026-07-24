import tempfile
import unittest

from backend.app.storage import LocalObjectStorage


class ObjectStorageTests(unittest.TestCase):
    def test_local_object_storage_lifecycle(self):
        with tempfile.TemporaryDirectory() as directory:
            storage = LocalObjectStorage(directory)
            key = storage.put("study/user/document/file.txt", b"hello", content_type="text/plain")
            self.assertEqual(storage.get(key), b"hello")
            storage.delete(key)
            with self.assertRaises(FileNotFoundError):
                storage.get(key)


if __name__ == "__main__":
    unittest.main()
