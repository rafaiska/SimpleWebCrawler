from typing import Optional


class WebLink:
    def __init__(self, url: str, parent: Optional[str], visited: bool = False, error: bool = False):
        self.url = url
        self.parent = parent
        self.visited = visited
        self.error = error

    def __str__(self):
        return self.url
