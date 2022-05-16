from unittest import TestCase
from unittest.mock import Mock

from src.simple_webcrawler import SimpleWebCrawler
from src.web_link import WebLink


class TestSimpleWebCrawler(TestCase):
    def setUp(self) -> None:
        self.crawler = SimpleWebCrawler()
        self._configure_crawler_mocks()

    def tearDown(self) -> None:
        pass

    def _configure_crawler_mocks(self):
        self.crawler.global_timeout = 30
        self.crawler.remaining_links = 1
        self.crawler.queues = (_QueueMock(), _QueueMock(), _QueueMock())
        self.crawler.processes = [_ProcessMock(), _ProcessMock()]
        self.crawler.dao = _DAOMock()
        self.crawler.queued_for_visit = set()

    def test_crawl_without_any_links(self):
        self.crawler.get_master_queue().get.return_value = None
        self.crawler.crawl()
        self._assert_processes_joined()

    def test_crawl_with_one_link_without_further_links(self):
        self.crawler.get_master_queue().get.return_value = WebLink('http://test.com', None, visited=True)
        self.crawler.crawl()
        self.crawler.dao.save_link.assert_called()
        self._assert_processes_joined()

    def test_crawl_enqueuing_unvisited_link(self):
        self.crawler.get_master_queue().get.side_effect = [WebLink('http://test.com', None, visited=False),
                                                           WebLink('http://test.com', None, visited=True)]
        self.crawler.crawl()
        self.crawler.dao.save_link.assert_called()
        self.crawler.get_slave_queue().put.assert_called()
        self._assert_processes_joined()

    def _assert_processes_joined(self):
        for p in self.crawler.processes:
            p.join.assert_called()


class _QueueMock:
    def __init__(self):
        self.put = Mock()
        self.get = Mock()
        self._configure_get()

    def _configure_get(self):
        self.get.return_value = WebLink('http://test.com', None)


class _ProcessMock:
    def __init__(self):
        self.join = Mock()
        self.start = Mock()


class _DAOMock:
    def __init__(self):
        self.has_link_with_url = Mock()
        self.get_unvisited_links = Mock()
        self.save_link = Mock()
        self.update_link = Mock()

        self._configure_has_link()
        self._configure_get_unvisited()

    def _configure_get_unvisited(self):
        self.get_unvisited_links.return_value = [WebLink('http://test.com', None)]

    def _configure_has_link(self):
        self.has_link_with_url.return_value = False
