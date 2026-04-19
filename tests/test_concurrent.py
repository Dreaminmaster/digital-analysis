import time
import unittest

from digital_analysis.execution.concurrent import gather


class ConcurrentTests(unittest.TestCase):
    def test_gather_parallel(self) -> None:
        def slow() -> bool:
            time.sleep(0.05)
            return True

        start = time.monotonic()
        result = gather({"a": slow, "b": slow, "c": slow})
        elapsed = time.monotonic() - start

        self.assertTrue(result.ok)
        self.assertLess(elapsed, 0.2)


if __name__ == "__main__":
    unittest.main()
