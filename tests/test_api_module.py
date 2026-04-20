import unittest


class ApiImportTests(unittest.TestCase):
    def test_api_module_importable(self) -> None:
        import digital_analysis.product.api as api  # noqa: F401
        self.assertTrue(hasattr(api, "create_app"))


if __name__ == "__main__":
    unittest.main()
