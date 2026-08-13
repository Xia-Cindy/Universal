import unittest

from backend.app.api.contracts import list_contracts
from backend.app.api.routes import ApiFacade


class RAGFlowRuntimeVerificationContractTests(unittest.TestCase):
    def test_runtime_verification_contract_is_publicly_registered(self):
        contracts = {(item["method"], item["path"]) for item in list_contracts()}

        self.assertIn(
            ("POST", "/api/knowledge/provider/runtime-verification"),
            contracts,
        )

    def test_local_provider_reports_failed_without_creating_knowledge(self):
        result = ApiFacade().verify_knowledge_provider_runtime()

        self.assertEqual(result["provider"], "local")
        self.assertEqual(result["status"], "failed")
        self.assertFalse(result["verified"])
        self.assertEqual(result["errorCode"], "RAGFLOW_NOT_CONFIGURED")


if __name__ == "__main__":
    unittest.main()
