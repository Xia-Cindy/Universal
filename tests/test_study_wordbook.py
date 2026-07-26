import tempfile
import unittest
from pathlib import Path

from backend.app.api.contracts import list_contracts
from backend.app.api.routes import ApiFacade


class StudyWordbookTests(unittest.TestCase):
    def setUp(self):
        self.api = ApiFacade()

    def test_manual_entry_can_hold_tags_phrases_examples_and_notes(self):
        entry = self.api.create_wordbook_entry(
            {
                "word": "resilient",
                "meaning": "able to recover quickly",
                "pronunciation": "/rɪˈzɪliənt/",
                "tags": ["academic", "adjective"],
            }
        )
        updated = self.api.update_wordbook_entry(
            entry["id"],
            {
                "phrases": ["a resilient system"],
                "examples": ["The team remained resilient after the setback."],
                "notes": "Useful in systems and writing contexts.",
            },
        )

        self.assertEqual(updated["tags"], ["academic", "adjective"])
        self.assertEqual(updated["phrases"], ["a resilient system"])
        self.assertEqual(updated["examples"], ["The team remained resilient after the setback."])
        self.assertEqual(updated["source"], "manual")

    def test_text_and_csv_import_skip_duplicates_in_the_same_goal_scope(self):
        first = self.api.import_wordbook_entries(
            {
                "fileName": "words.txt",
                "content": "allocate\t分配\nresilient | 有韧性的\nallocate | 已存在",
            }
        )
        second = self.api.import_wordbook_entries(
            {
                "fileName": "words.csv",
                "content": "word,meaning,tags\nallocate,分配,verb;systems\ncache,缓存,noun",
            }
        )

        self.assertEqual(first["importedCount"], 2)
        self.assertEqual(second["importedCount"], 1)
        self.assertEqual(second["skipped"], ["allocate"])
        entries = self.api.list_wordbook_entries()
        self.assertEqual([entry["word"] for entry in entries], ["allocate", "cache", "resilient"])
        self.assertEqual(entries[1]["tags"], ["noun"])

    def test_language_and_tag_filters_are_owned_by_wordbook_api(self):
        self.api.create_wordbook_entry(
            {"word": "bonjour", "language": "French", "tags": ["greeting", "travel"]}
        )
        self.api.create_wordbook_entry(
            {"word": "resilient", "language": "English", "tags": ["academic"]}
        )

        self.assertEqual(
            [entry["word"] for entry in self.api.list_wordbook_entries(language="French")],
            ["bonjour"],
        )
        self.assertEqual(
            [entry["word"] for entry in self.api.list_wordbook_entries(language="French", tag="travel")],
            ["bonjour"],
        )
        self.assertEqual(self.api.list_wordbook_entries(language="French", tag="academic"), [])

    def test_same_spelling_can_exist_in_different_language_partitions(self):
        self.api.create_wordbook_entry({"word": "gift", "language": "English"})
        german = self.api.create_wordbook_entry({"word": "Gift", "language": "German"})

        self.assertEqual(german["language"], "German")
        self.assertEqual(len(self.api.list_wordbook_entries()), 2)

    def test_entries_survive_shared_sqlite_restart(self):
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "wordbook.sqlite3")
            first = ApiFacade(database_path=path)
            entry = first.create_wordbook_entry({"word": "context", "meaning": "上下文"})

            second = ApiFacade(database_path=path)
            restored = second.get_wordbook_entry(entry["id"])

        self.assertEqual(restored["word"], "context")
        self.assertEqual(restored["meaning"], "上下文")

    def test_wordbook_contracts_are_declared(self):
        names = {item["name"] for item in list_contracts()}
        self.assertTrue(
            {"list_wordbook_entries", "create_wordbook_entry", "update_wordbook_entry", "import_wordbook_entries"}
            <= names
        )


if __name__ == "__main__":
    unittest.main()
