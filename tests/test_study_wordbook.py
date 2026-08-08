import tempfile
import unittest
import sqlite3
from pathlib import Path

from backend.app.api.contracts import list_contracts
from backend.app.api.routes import ApiFacade
from backend.app.knowledge.dictionary import DictionaryLookup
from backend.app.persistence.codec import loads
from backend.app.persistence.sqlite import SQLitePersistence


class StubEnglishDictionaryProvider:
    def lookup(self, word: str) -> DictionaryLookup:
        return DictionaryLookup(
            status="available",
            word=word,
            pronunciations=("/wɜːd/",),
            usages=(
                {
                    "partOfSpeech": "noun",
                    "definition": "a unit of language with a particular meaning",
                    "example": "This word has a personal example.",
                },
            ),
            source_name="Test English Dictionary",
            source_url="https://example.test/dictionary",
        )


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

    def test_wordbook_entry_can_be_deleted_by_its_owner(self):
        entry = self.api.create_wordbook_entry({"word": "ephemeral"})

        deleted = self.api.delete_wordbook_entry(entry["id"])

        self.assertEqual(deleted, {"id": entry["id"], "deleted": True})
        self.assertEqual(self.api.list_wordbook_entries(), [])

    def test_entries_survive_shared_sqlite_restart(self):
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "wordbook.sqlite3")
            first = ApiFacade(database_path=path)
            entry = first.create_wordbook_entry({"word": "context", "meaning": "上下文"})

            second = ApiFacade(database_path=path)
            restored = second.get_wordbook_entry(entry["id"])

        self.assertEqual(restored["word"], "context")
        self.assertEqual(restored["meaning"], "上下文")

    def test_sqlite_backfills_language_for_database_with_original_wordbook_schema(self):
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "wordbook.sqlite3")
            connection = sqlite3.connect(path)
            connection.executescript(
                """
                CREATE TABLE schema_migrations (version TEXT PRIMARY KEY);
                INSERT INTO schema_migrations(version) VALUES ('004_study_wordbook.sql');
                CREATE TABLE study_word_entries (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    goal_id TEXT,
                    normalized_word TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                """
            )
            connection.close()

            persistence = SQLitePersistence(path)
            columns = {
                row["name"]
                for row in persistence.connection.execute("PRAGMA table_info(study_word_entries)")
            }
            applied = {
                row["version"]
                for row in persistence.connection.execute("SELECT version FROM schema_migrations")
            }
            persistence.close()

        self.assertIn("language", columns)
        self.assertIn("005_study_wordbook_language_backfill.sql", applied)

    def test_json_codec_preserves_postgres_native_jsonb_values(self):
        payload = {"word": "resilient", "tags": ["academic"]}

        self.assertEqual(loads(payload), payload)

    def test_wordbook_contracts_are_declared(self):
        names = {item["name"] for item in list_contracts()}
        self.assertTrue(
            {
                "list_wordbook_entries",
                "create_wordbook_entry",
                "update_wordbook_entry",
                "delete_wordbook_entry",
                "import_wordbook_entries",
                "refresh_wordbook_dictionary",
            }
            <= names
        )

    def test_english_dictionary_is_linked_without_overwriting_personal_examples(self):
        api = ApiFacade(english_dictionary_provider=StubEnglishDictionaryProvider())
        entry = api.create_wordbook_entry(
            {
                "word": "word",
                "meaning": "我自己的释义",
                "examples": ["My custom sentence."],
            }
        )

        self.assertEqual(entry["pronunciation"], "/wɜːd/")
        self.assertEqual(entry["meaning"], "我自己的释义")
        self.assertEqual(entry["examples"], ["My custom sentence."])
        self.assertEqual(entry["dictionary"]["status"], "available")
        self.assertEqual(entry["dictionary"]["sourceName"], "Test English Dictionary")
        self.assertEqual(entry["dictionary"]["usages"][0]["partOfSpeech"], "noun")

        updated = api.update_wordbook_entry(
            entry["id"],
            {"examples": ["A revised personal sentence."], "phrases": ["a useful word"]},
        )
        self.assertEqual(updated["examples"], ["A revised personal sentence."])
        self.assertEqual(updated["phrases"], ["a useful word"])
        self.assertEqual(updated["dictionary"]["usages"][0]["definition"], "a unit of language with a particular meaning")

    def test_dictionary_reference_appears_in_knowledge_and_import_syncs_each_english_word(self):
        api = ApiFacade(english_dictionary_provider=StubEnglishDictionaryProvider())
        result = api.import_wordbook_entries(
            {
                "fileName": "dictionary-words.txt",
                "content": "alpha\tfirst\nbeta\tsecond",
                "language": "English",
            }
        )
        self.assertEqual(result["importedCount"], 2)
        self.assertTrue(all(entry["dictionary"]["status"] == "available" for entry in result["imported"]))

        documents = api.list_study_knowledge_documents()
        reference = next(document for document in documents if document["fileName"] == "English-English Dictionary")
        detail = api.get_knowledge_document(reference["id"])
        self.assertEqual(detail["document"]["provider"], "english_dictionary")
        self.assertEqual(len(detail["chunks"]), 2)
        self.assertEqual({chunk["metadata"]["normalizedWord"] for chunk in detail["chunks"]}, {"alpha", "beta"})

    def test_custom_pronunciation_is_never_replaced_by_dictionary_sync(self):
        api = ApiFacade(english_dictionary_provider=StubEnglishDictionaryProvider())
        entry = api.create_wordbook_entry({"word": "word", "pronunciation": "/custom/"})
        refreshed = api.refresh_wordbook_dictionary(entry["id"])

        self.assertEqual(refreshed["pronunciation"], "/custom/")
        self.assertEqual(refreshed["dictionary"]["pronunciations"], ["/wɜːd/"])


if __name__ == "__main__":
    unittest.main()
