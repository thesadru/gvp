from typing import List, Literal
from urllib.parse import urljoin

import requests

from gvp.models import *

__all__ = [
    "article",
    "articles",
    "contacts",
    "static_file",
    "static_files",
    "search",
    "news",
    "events",
    "event",
]


def request(endpoint: str, method: str = "GET", **kwargs):
    """Request a gvp endpoint"""
    url = urljoin("https://www.gvp.cz/new/api/", endpoint)
    r = requests.request(method, url, **kwargs)
    data = r.json()
    if data["error"]:
        raise Exception(data["error"])

    return data["data"]


def article(id: int) -> Article:
    """An article with a given id"""
    data = request("articles", params=dict(id=id, action="by_id"))
    return Article(data)


def articles(page: int = 1, author: str = None) -> List[Article]:
    """A list of articles

    If an author username is provided then get all articles by that author
    """
    params = {}

    if author:
        params["author"] = author
        params["action"] = "by_author"

    params["page"] = page

    data = request("articles", params=params)
    return [Article(i) for i in data["articles"]]


def contacts(type: Literal[1, 2, 3] = 1) -> List[Contact]:
    """A list of contacts

    type 1: teachers, type 2: school canteen, type 3: other
    """
    data = request("contacts", params=dict(type=type))
    return [Contact(i) for i in data]


def static_file(id: int) -> StaticFile:
    """A static file with a given id"""
    data = request("static", params=dict(id=id, action="by_id"))
    return StaticFile(data)


def static_files() -> List[StaticFile]:
    """A list of all static files"""
    data = request("static")
    return [StaticFile(i) for i in data]


def search(term: str, page: int = 1, category: str = "all") -> List[SearchResult]:
    """Search for a term accross the website

    May return a static file, and article or a comment. Contacts are not supported.
    You may filter the results by providing the category.
    """
    data = request("search", params=dict(term=term, page=page, category=category))
    return [SearchResult(i, category) for i in data["results"] if "title" in i]


def news() -> List[News]:
    """A list of all lagacy news"""
    data = request("news")
    return [News(i) for i in data]


def events() -> List[Event]:
    """A list of all current events"""
    import bs4

    form = dict(
        mesic1=1,
        mesic2=12,
    )
    r = requests.post("https://www.gvp.cz/prehled_akci/index.php", data=form)
    soup = bs4.BeautifulSoup(r.content, "html.parser")
    events = soup.find_all("tr", {"class": ["schvaleno", "navrh"]})
    return [Event(i) for i in events if i.find("td").text]


def event(id: int) -> EventDetails:
    """Details of a specific event"""
    import bs4

    r = requests.get("https://www.gvp.cz/prehled_akci/edit.php", params=dict(id=id))
    soup = bs4.BeautifulSoup(r.content, "html.parser")
    return EventDetails(soup, id=id)
