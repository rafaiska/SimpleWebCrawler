import time
from multiprocessing import Queue
from re import findall
from typing import List
from urllib import request

from src.utils import pop_queue
from src.web_link import WebLink

THROTTLE_DOWN_FACTOR = 1
IDLE_PROCESS_DELAY = 1


def fetch_links(queues: List[Queue], timeout: float):
    fetcher = LinkFetcher()
    fetcher.configure(queues, timeout)
    fetcher.run()


class LinkFetcher:
    def __init__(self):
        self.slave_queue = None
        self.master_queue = None
        self.command_queue = None
        self.http_timeout = None
        self.last_latency = None

    def configure(self, queues: List[Queue], http_timeout: float):
        self.master_queue, self.slave_queue, self.command_queue = queues
        self.http_timeout = http_timeout
        self.last_latency = 0

    def run(self):
        while True:
            if self._was_terminate_signal_issued():
                break
            else:
                weblink = pop_queue(self.slave_queue)
                if not weblink:
                    time.sleep(IDLE_PROCESS_DELAY)
                    continue
                else:
                    self._process_weblink(weblink)

    def _was_terminate_signal_issued(self) -> bool:
        return pop_queue(self.command_queue) == 0

    def _process_weblink(self, weblink: WebLink):
        print(weblink.url)
        body = self._fetch_body(weblink)
        body = self._decode_body(body)
        self._prepare_and_send_visited_link(weblink, body is None)
        str_links = self._extract_all_links(body)
        self._enqueue_unvisited_links(str_links, weblink.url)
        time.sleep(self.last_latency * THROTTLE_DOWN_FACTOR)

    def _fetch_body(self, weblink: WebLink) -> str:
        start = time.time()
        try:
            body = request.urlopen(weblink.url, timeout=self.http_timeout).read()
        except:
            body = None
        self.last_latency = time.time() - start
        return body

    @staticmethod
    def _decode_body(body):
        try:
            return body.decode('utf-8')
        except:
            return None

    def _prepare_and_send_visited_link(self, weblink: WebLink, error: bool):
        weblink.error = error
        weblink.visited = True
        self.master_queue.put(weblink)

    @staticmethod
    def _extract_all_links(body: str) -> List[str]:
        if body:
            links = set(findall(r'<a.*href=[\'"]?(https?://[^\'" >]+)', body))
        else:
            links = []
        return links

    def _enqueue_unvisited_links(self, str_links: List[str], parent_url: str):
        for wl in [WebLink(ln, parent_url) for ln in str_links]:
            self.master_queue.put(wl)
