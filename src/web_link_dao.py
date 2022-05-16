from abc import abstractmethod
from typing import List

from src.web_link import WebLink


class WebLinkDAO:
    @abstractmethod
    def set_up(self):
        raise NotImplementedError

    @abstractmethod
    def get_unvisited_links(self, n: int) -> List[WebLink]:
        raise NotImplementedError

    @abstractmethod
    def save_link(self, link: WebLink):
        raise NotImplementedError

    @abstractmethod
    def update_link(self, link: WebLink):
        raise NotImplementedError

    @abstractmethod
    def save_update_links(self, links: List[WebLink]):
        raise NotImplementedError

    @abstractmethod
    def has_link_with_url(self, url: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def set_visited(self, url: str, value: bool):
        raise NotImplementedError

    @abstractmethod
    def set_error(self, url: str, value: bool):
        raise NotImplementedError
