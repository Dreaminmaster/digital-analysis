import unittest

from digital_analysis.orchestrator import DigitalAnalysisOrchestrator
from digital_analysis.product.monitoring import MonitoringService


class MonitoringTests(unittest.TestCase):
    def test_create_watchlist_and_monitor(self) -> None:
        service = MonitoringService(orchestrator=DigitalAnalysisOrchestrator(auto_enrich=False))
        item = service.create_watchlist_item(name='Macro', query='Will there be a recession next year?', tags=('macro',))
        self.assertEqual(item.name, 'Macro')
        self.assertEqual(len(service.list_watchlist_items()), 1)

        monitor = service.create_monitor(topic='Recession risk', query='Will there be a recession next year?')
        self.assertEqual(monitor.topic, 'Recession risk')
        self.assertEqual(len(service.list_monitors()), 1)

    def test_run_monitor(self) -> None:
        service = MonitoringService(orchestrator=DigitalAnalysisOrchestrator(auto_enrich=False))
        monitor = service.create_monitor(topic='Recession risk', query='Will there be a recession next year?')
        result = service.run_monitor(monitor.monitor_id)
        self.assertTrue(result.priceability.priceable)


if __name__ == '__main__':
    unittest.main()
