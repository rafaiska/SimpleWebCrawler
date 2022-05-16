from multiprocessing import Queue, Process

from src.fetch_links import fetch_links
from src.utils import pop_queue
from src.web_link import WebLink
from src.web_link_dao_sqlite import WebLinkDAOSQLite


class SimpleWebCrawler:
    def __init__(self):
        self.remaining_links = None
        self.processes = None
        self.global_timeout = None
        self.queues = None
        self.queued_for_visit = None
        self.dao = None

    def configure(self, args):
        self.global_timeout = args.global_timeout
        self.remaining_links = args.max_links
        self.queues = (Queue(), Queue(), Queue())
        self.processes = [Process(target=fetch_links, args=(self.queues, args.http_get_timeout)) for _ in
                          range(args.max_subp)]
        self.dao = WebLinkDAOSQLite()
        self.dao.set_up()
        self.queued_for_visit = set()

    def get_master_queue(self):
        return self.queues[0]

    def get_slave_queue(self):
        return self.queues[1]

    def get_command_queue(self):
        return self.queues[2]

    def add_link(self, link: WebLink):
        if not self.dao.has_link_with_url(link.url):
            self.dao.save_link(link)

    def queue_all_unvisited(self):
        slave_queue = self.get_slave_queue()
        for ln in self.dao.get_unvisited_links():
            slave_queue.put(ln)

    def crawl(self):
        self._start_all_slave_processes()

        try:
            self._main_loop()
        except KeyboardInterrupt:
            print('Aborting')

        self._stop_all_slave_processes()

    def _main_loop(self):
        master_queue = self.get_master_queue()
        while self.remaining_links > 0:
            weblink = pop_queue(master_queue, timeout=self.global_timeout)
            if not weblink:
                print('Exiting due to global timeout')
                break
            else:
                self._handle_weblink(weblink)

    def _handle_weblink(self, weblink: WebLink):
        exists_in_db = self.dao.has_link_with_url(weblink.url)
        if weblink.visited and not exists_in_db:
            self.dao.save_link(weblink)
            self.remaining_links -= 1
        elif not weblink.visited and weblink.url not in self.queued_for_visit:
            self._queue_for_visit(weblink)

    def _queue_for_visit(self, weblink: WebLink):
        slave_queue = self.get_slave_queue()
        slave_queue.put(weblink)
        self.queued_for_visit.add(weblink.url)

    def _start_all_slave_processes(self):
        for p in self.processes:
            p.start()

    def _stop_all_slave_processes(self):
        command_queue = self.get_command_queue()
        for i in range(len(self.processes)):
            command_queue.put(0)
        for i in range(len(self.processes)):
            self.processes[i].join()