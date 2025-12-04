# src/ultimate_crawler/crawl/robots.py

from typing import Dict
from urllib.parse import urlparse
from urllib import robotparser


class RobotsManager:
    """
    Gestion de robots.txt par domaine.
    Pour l'instant, cache en mémoire seulement.
    """

    def __init__(self, user_agent: str):
        self.user_agent = user_agent
        self.parsers: Dict[str, robotparser.RobotFileParser] = {}

    def _get_parser(self, url: str) -> robotparser.RobotFileParser:
        parsed = urlparse(url)
        base = f"{parsed.scheme}://{parsed.netloc}"
        if base in self.parsers:
            return self.parsers[base]

        robots_url = f"{base}/robots.txt"
        rp = robotparser.RobotFileParser()
        try:
            rp.set_url(robots_url)
            rp.read()
        except Exception:
            # si impossible de lire, on crée un parser qui autorise tout
            rp = robotparser.RobotFileParser()
            rp.parse(["User-agent: *", "Allow: /"])

        self.parsers[base] = rp
        return rp

    def allowed(self, url: str) -> bool:
        parser = self._get_parser(url)
        return parser.can_fetch(self.user_agent, url)
