import shutil
import tempfile
import unittest
from pathlib import Path

from digital_analysis.orchestrator import DigitalAnalysisOrchestrator
from digital_analysis.product.monitoring import MonitoringService
from digital_analysis.product.store import FileStore


class FileStoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = Path(tempfile.mkdtemp(prefix='digital_analysis_store_'))

    def tearDown(self) -> None:
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_file_store_persists_objects(self) -> None:
        store = FileStore(self.tmpdir)
        service = MonitoringService(orchestrator=DigitalAnalysisOrchestrator(auto_enrich=False), store=store)
        item = service.create_watchlist_item(name='Macro', query='Will there be a recession next year?', tags=('macro',))
        monitor = service.create_monitor(topic='Recession risk', query='Will there be a recession next year?')
        service.run_monitor(monitor.monitor_id)

        reloaded = FileStore(self.tmpdir)
        self.assertEqual(len(reloaded.list_watchlist_items()), 1)
        self.assertEqual(len(reloaded.list_monitors()), 1)
        self.assertGreaterEqual(len(reloaded.list_monitor_runs()), 1)


if __name__ == '__main__':
    unittest.main()
