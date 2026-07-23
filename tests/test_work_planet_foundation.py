import unittest
from pathlib import Path

from backend.app.api.contracts import list_contracts
from backend.app.api.routes import ApiFacade
from backend.app.planets.work.community import CSDNCommunityService


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class WorkPlanetFoundationTests(unittest.TestCase):
    def setUp(self):
        self.api = ApiFacade()

    def test_work_planet_is_enterable(self):
        planets = self.api.list_planets()["planets"]
        work = next(planet for planet in planets if planet["name"] == "work")

        self.assertTrue(work["enterable"])
        self.assertEqual(work["status"], "active")
        self.assertEqual(work["primaryAction"], "Enter Work Planet")

    def test_work_home_primary_action_starts_with_tech_stack(self):
        home = self.api.get_work_home()

        self.assertEqual(home["primaryAction"]["type"], "create_tech_stack")
        self.assertEqual(home["summary"]["techStackCount"], 0)

    def test_tech_stack_detail_and_dynamic_resume_use_confirmed_evidence(self):
        stack = self.api.create_work_tech_stack(
            {
                "name": "RAG",
                "category": "AI Engineering",
                "proficiency": "practicing",
                "description": "Retrieval augmented generation systems.",
                "tags": ["retrieval", "knowledge"],
            }
        )
        project = self.api.create_work_project(
            {
                "title": "Universe Knowledge Provider",
                "description": "Connected Knowledge Service to RAGFlow through a provider adapter.",
                "techStackIds": [stack["id"]],
            }
        )
        resume = self.api.create_work_resume_draft({"roleTarget": "AI Engineer"})
        detail = self.api.get_work_tech_stack(stack["id"])
        home = self.api.get_work_home()

        self.assertEqual(detail["techStack"]["id"], stack["id"])
        self.assertEqual(detail["projects"][0]["id"], project["id"])
        self.assertIn("RAG", resume["content"])
        self.assertIn(f"tech_stack:{stack['id']}", resume["evidenceRefs"])
        self.assertIn(f"project:{project['id']}", resume["evidenceRefs"])
        self.assertEqual(home["primaryAction"]["type"], "review_resume")

    def test_tech_stack_supports_articles_and_learning_records(self):
        stack = self.api.create_work_tech_stack(
            {
                "name": "FastAPI",
                "category": "Backend",
                "proficiency": "practicing",
                "tags": ["python", "api"],
            }
        )
        article = self.api.create_work_article(
            stack["id"],
            {
                "title": "FastAPI Dependency Notes",
                "articleType": "note",
                "summary": "Dependency injection patterns.",
                "content": "Use dependencies to express request-scoped capabilities.",
                "tags": ["backend", "auth"],
            },
        )
        record = self.api.create_work_learning_record(
            stack["id"],
            {
                "title": "Read dependency docs",
                "notes": "Mapped dependency injection to auth middleware.",
                "minutes": 45,
                "tags": ["reading"],
            },
        )
        detail = self.api.get_work_tech_stack(stack["id"])
        home = self.api.get_work_home()
        resume = self.api.create_work_resume_draft({"roleTarget": "Backend Engineer"})

        self.assertEqual(detail["articles"][0]["id"], article["id"])
        self.assertEqual(detail["articles"][0]["articleType"], "note")
        self.assertEqual(detail["learningRecords"][0]["id"], record["id"])
        self.assertEqual(home["summary"]["articleCount"], 1)
        self.assertEqual(home["summary"]["learningRecordCount"], 1)
        self.assertIn(f"article:{article['id']}", resume["evidenceRefs"])
        self.assertIn(f"learning_record:{record['id']}", resume["evidenceRefs"])

    def test_tech_stacks_keep_creation_order(self):
        java = self.api.create_work_tech_stack(
            {"name": "Java", "category": "Backend", "proficiency": "learning"}
        )
        vue = self.api.create_work_tech_stack(
            {"name": "Vue", "category": "Frontend", "proficiency": "learning"}
        )

        stacks = self.api.list_work_tech_stacks()

        self.assertEqual([stack["id"] for stack in stacks], [java["id"], vue["id"]])

    def test_tech_stack_can_be_updated_and_archived(self):
        stack = self.api.create_work_tech_stack(
            {"name": "Java", "category": "Backend", "proficiency": "learning"}
        )

        updated = self.api.update_work_tech_stack(
            stack["id"],
            {
                "name": "Java Platform",
                "category": "Backend Engineering",
                "proficiency": "practicing",
                "description": "JVM, Spring and production backend systems.",
                "tags": ["jvm", "spring"],
            },
        )
        archived = self.api.delete_work_tech_stack(stack["id"])
        stacks = self.api.list_work_tech_stacks()

        self.assertEqual(updated["name"], "Java Platform")
        self.assertEqual(updated["category"], "Backend Engineering")
        self.assertEqual(updated["tags"], ["jvm", "spring"])
        self.assertEqual(archived["status"], "archived")
        self.assertEqual(stacks, [])

    def test_work_article_supports_outline_chapters_and_markdown_blocks(self):
        stack = self.api.create_work_tech_stack(
            {"name": "Java", "category": "Backend", "proficiency": "learning"}
        )

        article = self.api.create_work_article(
            stack["id"],
            {
                "title": "Java Collection Notes",
                "articleType": "knowledge",
                "summary": "Collection usage notes.",
                "outline": "- ArrayList\n- HashMap",
                "chapters": [
                    {
                        "title": "List",
                        "body": "| Type | Use |\n| --- | --- |\n| ArrayList | Read-heavy |\n\n```java\nList<String> names = new ArrayList<>();\n```",
                    },
                    {
                        "title": "Map",
                        "body": "![HashMap structure](https://example.com/hashmap.png)",
                    },
                ],
                "tags": ["collection"],
            },
        )

        self.assertIn("## 大纲", article["content"])
        self.assertIn("## List", article["content"])
        self.assertIn("| Type | Use |", article["content"])
        self.assertIn("```java", article["content"])
        self.assertIn("![HashMap structure]", article["content"])

    def test_csdn_community_parser_limits_to_30_articles(self):
        service = CSDNCommunityService()
        html = "".join(
            f'<a href="https://blog.csdn.net/example/article/details/{index}">Java article title {index}</a>'
            for index in range(35)
        )

        articles = service.parse_articles(html, limit=30)

        self.assertEqual(len(articles), 30)
        self.assertEqual(articles[0].title, "Java article title 0")

    def test_csdn_community_fallback_returns_displayable_articles(self):
        class FailingCSDNCommunityService(CSDNCommunityService):
            def _fetch_articles(self, url, *, limit):
                raise OSError("network blocked")

        result = FailingCSDNCommunityService().hot_articles("java", limit=30)

        self.assertEqual(result["error"], "")
        self.assertEqual(len(result["articles"]), 30)
        self.assertEqual(result["articles"][0]["source"], "CSDN")
        self.assertIn("content", result["articles"][0])

    def test_csdn_community_article_detail_parses_inline_content(self):
        service = CSDNCommunityService()
        html = """
        <html>
          <head><title>Java Inline Reader-CSDN博客</title></head>
          <body>
            <article>
              <h1>Java Inline Reader</h1>
              <p>Use Java records to model immutable response payloads.</p>
              <p>Keep infrastructure reading outside Work business logic.</p>
            </article>
          </body>
        </html>
        """

        detail = service.parse_article_detail(html, url="https://blog.csdn.net/demo/article/details/1")

        self.assertEqual(detail["title"], "Java Inline Reader")
        self.assertIn("immutable response payloads", detail["content"])
        self.assertIn("outside Work business logic", detail["content"])

    def test_work_contracts_are_declared(self):
        contracts = {(contract["method"], contract["path"]) for contract in list_contracts()}

        self.assertIn(("GET", "/api/work/home"), contracts)
        self.assertIn(("GET", "/api/work/knowledge/documents"), contracts)
        self.assertIn(("POST", "/api/work/knowledge/documents"), contracts)
        self.assertIn(("POST", "/api/work/tech-stacks"), contracts)
        self.assertIn(("PATCH", "/api/work/tech-stacks/{tech_stack_id}"), contracts)
        self.assertIn(("DELETE", "/api/work/tech-stacks/{tech_stack_id}"), contracts)
        self.assertIn(("GET", "/api/work/tech-stacks/{tech_stack_id}"), contracts)
        self.assertIn(("POST", "/api/work/tech-stacks/{tech_stack_id}/articles"), contracts)
        self.assertIn(("POST", "/api/work/tech-stacks/{tech_stack_id}/learning-records"), contracts)
        self.assertIn(("GET", "/api/work/community/csdn"), contracts)
        self.assertIn(("GET", "/api/work/community/csdn/article"), contracts)
        self.assertIn(("POST", "/api/work/resumes/draft"), contracts)

    def test_work_frontend_routes_exist(self):
        router = (PROJECT_ROOT / "frontend/src/router/index.ts").read_text()
        portal = (PROJECT_ROOT / "frontend/src/universe/portal/UniversePortal.vue").read_text()

        self.assertIn("path: '/work'", router)
        self.assertIn("TechStackDirectory", router)
        self.assertIn("WorkKnowledge", router)
        self.assertIn("DynamicResume", router)
        self.assertIn("Enter Work Planet", portal)
        self.assertNotIn("/:futurePlanet(work|novel|life|creator)", router)

    def test_work_tech_stack_directory_uses_two_level_tabs_and_modal_create(self):
        directory = (PROJECT_ROOT / "frontend/src/planets/work/tech-stack/TechStackDirectory.vue").read_text()

        self.assertIn("selectedCategory", directory)
        self.assertIn("stackTabs", directory)
        self.assertIn("modal-backdrop", directory)
        self.assertIn("CSDN 社区热文", directory)
        self.assertIn("查看内容", directory)
        self.assertIn("fetchCSDNCommunityArticleDetail", directory)

    def test_work_tech_stack_detail_has_management_and_article_builder(self):
        detail = (PROJECT_ROOT / "frontend/src/planets/work/tech-stack/TechStackDetail.vue").read_text()

        self.assertIn("Edit Stack", detail)
        self.assertIn("Archive Stack", detail)
        self.assertIn("article-writing-room", detail)
        self.assertIn("article-outline-panel", detail)
        self.assertIn("article-editor-canvas", detail)
        self.assertIn("article-inline-toolbar", detail)
        self.assertIn("article-rich-editor", detail)
        self.assertIn("articleOutline", detail)
        self.assertIn("article-table-fragment", detail)
        self.assertIn("article-code-fragment", detail)
        self.assertIn("article-image-fragment", detail)
        self.assertIn("compact-tool-button", detail)
        self.assertIn("handleEditorPaste", detail)
        self.assertIn("parsePastedTable", detail)
        self.assertIn("alignSelection", detail)
        self.assertIn("formatBold", detail)
        self.assertIn("applyTextColor", detail)
        self.assertIn("addTableRowAfter", detail)
        self.assertIn("deleteTableRow", detail)
        self.assertIn("addTableColumnAfter", detail)
        self.assertIn("deleteTableColumn", detail)
        self.assertIn("mergeTableCellRight", detail)
        self.assertIn("toolbar-group", detail)
        self.assertIn("color-tool", detail)
        self.assertNotIn("article-block-stack", detail)
        self.assertNotIn("article-table-block", detail)
        self.assertNotIn("article-code-block", detail)
        self.assertNotIn("article-image-block", detail)
        self.assertNotIn("article-tool-panel", detail)
        self.assertNotIn("学习记录", detail)
        self.assertNotIn("文章与学习记录", detail)
        self.assertNotIn("Work Knowledge</h3>", detail)


if __name__ == "__main__":
    unittest.main()
