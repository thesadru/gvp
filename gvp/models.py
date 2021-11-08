from __future__ import annotations

import re
from datetime import datetime
from typing import TYPE_CHECKING, Any, List, Optional

import gvp
from gvp.utils import get_selected, parse_human_date, parse_preliminary_month

if TYPE_CHECKING:
    import bs4

__all__ = [
    "User",
    "Comment",
    "Article",
    "Contact",
    "StaticFile",
    "SearchResult",
    "News",
    "Event",
    "EventDetails",
]


class User:
    """A possibly anonymous gvp user"""

    def __init__(self, data) -> None:
        self.username: str = data["username"] or ""
        self.name: str = data["name"]

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"<{type(self).__name__} name={self.name!r} username={self.username!r}>"

    @property
    def anonymous(self) -> bool:
        """Check if the user is anonymous"""
        return self.username == ""

    @property
    def mail(self) -> str:
        """The user's school email

        Returns an empty string for anonymous users.
        """
        if self.anonymous:
            return ""

        return f"{self.username}@gvp.cz"

    @property
    def www(self) -> str:
        """Link to the user's school webpage

        May not always work for users who shorten theit name such as Erlebach.
        """
        return f"https://gvp.cz/www/{self.username}/"

    def articles(self, page: int = 1) -> List[Article]:
        """Return articles written by this user"""
        return gvp.articles(page, self.username)


class Comment:
    """An article comment written by any user"""

    def __init__(self, data, article: Article) -> None:
        self.article = article
        self.id = int(data["id"])
        self.text: str = data["text"]
        self.date = datetime.fromisoformat(data["date"])
        self.edited: bool = data["edited"]
        self.author = User(data["author"])

    def __repr__(self) -> str:
        return f"<{type(self).__name__} id={self.id} author={self.author.name!r}>"

    @property
    def link(self):
        """An html link to the comment"""
        return f"{self.article.link}#{self.id}"


class Article:
    """An article written by any gvp user"""

    def __init__(self, data) -> None:
        self.id = int(data["id"])
        self.title: str = data["title"]
        self.preface: str = data["preface"]
        self.content: str = data["content"]
        self.pinned: bool = data["pinned"]
        self.date = datetime.fromisoformat(data["date"])
        self.author = User(data["author"])
        self.comments = [Comment(i, self) for i in data["comments"] if i is not None]
        self._link: str = data["link"]

    def __repr__(self) -> str:
        return f"<{type(self).__name__} id={self.id} author={self.author.username!r} title={self.title!r}>"

    @property
    def link(self) -> str:
        """An html link to the article"""
        return "https://gvp.cz/new/zivot/clanek/" + self._link

    def get_comment(self, id: int) -> Optional[Comment]:
        """Find and get a comment with a given id"""
        for i in self.comments:
            if i.id == id:
                return i
        return None


class Contact(User):
    """A contact for a school employee"""

    def __init__(self, data) -> None:
        self.description: Optional[str] = data["description"]
        self.name: str = data["name"]
        self.phone: str = data["phone"]
        self.username: str = data["mail"]
        self.degree: str = data["degree"].strip()
        self.degree2: str = data["degree2"].strip()
        self.type = int(data["type"])

    def __repr__(self) -> str:
        return f"<{type(self).__name__} name={self.full_name!r} description={self.description!r}>"

    @property
    def full_name(self) -> str:
        """The full name including titles and degrees"""
        name = self.name
        if self.degree:
            name = self.degree + " " + name
        if self.degree2:
            name = name + " " + self.degree2
        return name

    @property
    def homeroom(self) -> Optional[str]:
        """The class which the teacher teaches"""
        match = re.search(r"[123456]\.[ABCDEF]", self.description or "")
        if match is None:
            return None
        return match.group(0)


class StaticFile:
    """A static page file"""

    def __init__(self, data) -> None:
        self.id = int(data["id"])
        self.title: str = data["title"]
        self.content: str = data["content"]

    def __repr__(self) -> str:
        return f"<{type(self).__name__} id={self.id} title={self.title!r}>"


class SearchResult:
    """A result of a search request containing only the title and content"""

    def __init__(self, data, category: str = None) -> None:
        self.title: str = data["title"]
        self.content: str = data["content"]
        self._link: str = data["link"]
        self.category: str = data.get("category", category)

    def __repr__(self) -> str:
        return f"<{type(self).__name__} category={self.category!r} title={self.title!r} link={self._link!r}>"

    def complete(self) -> Any:
        """Complete the search result into a full class

        May return a StaticFile, an Article or a Comment
        """
        if self.category == "static":
            return StaticFile(
                {"id": self._link, "title": self.title, "content": self.content}
            )
        elif self.category == "articles":
            article_id = int(self._link.split("-")[-1])
            return gvp.article(article_id)
        elif self.category == "comments":
            article_id, comment_id = map(int, self._link.split("-")[-1].split("#"))
            return gvp.article(article_id).get_comment(comment_id)
        else:
            raise TypeError(f"Category {self.category} cannot be completed")


class News:
    """A legacy news, currently replaced by articles"""

    def __init__(self, data) -> None:
        self.id = int(data["id"])
        self.title: str = data["title"]
        self.content: str = data["content"]
        self.date = datetime.fromisoformat(data["date"])
        self.author = User(data["author"])

    def __repr__(self) -> str:
        return f"<{type(self).__name__} id={self.id} author={self.author.username!r} title={self.title!r}>"


class Event:
    """An event happening at the school"""

    id: int
    name: str
    organizator: str
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    all_classes: bool
    classes: List[str]
    has_chosen_students: bool
    teachers: List[str]
    total_teachers: int
    approved: bool

    def __init__(self, data: bs4.BeautifulSoup) -> None:
        entries = data.find_all("td")

        self.approved = "schvaleno" in data["class"]
        self.id = int(entries[0].a["href"].split("=")[1])
        self.name = entries[0].text.strip()
        self.organizator = entries[1].text.strip()
        self.start_time = parse_human_date(entries[2].text)
        self.end_time = parse_human_date(entries[3].text)

        classes = entries[4].text
        self.all_classes = False
        self.has_chosen_students = False
        self.classes = []
        if "výběr studentů" in classes:
            self.has_chosen_students = True
        elif "všechny třídy" in classes:
            self.all_classes = True
        elif "třídy:" in classes:
            self.classes = classes.split(":")[1].strip().split(", ")

        teachers = entries[5].text.split(":")[1].strip()
        self.teachers = teachers.split(", ") if teachers else []
        self.total_teachers = int(entries[5].text.split(")")[0].split("(")[1])

    def __repr__(self) -> str:
        return f"<{type(self).__name__} id={self.id!r} name={self.name!r} organizator={self.organizator!r}>"

    def details(self) -> EventDetails:
        """Gets the details of this event"""
        return gvp.event(self.id)


class EventDetails:
    """Details of an event happening at the school"""

    id: int
    name: str
    description: str
    organizator: str
    location: str

    preliminary_month: datetime
    duration_type: int
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    start_location: Optional[str]
    end_location: Optional[str]

    all_classes: bool
    classes: List[str]
    students: List[str]
    teachers: List[str]
    total_teachers: int

    price: int
    approved: bool
    notes: str

    def __init__(self, data: bs4.BeautifulSoup, id: int = 0) -> None:
        rows = data.find_all("tr")

        self.id = id

        self.name = rows[0].input["value"]
        self.description = rows[1].textarea.text.strip()
        self.organizator = rows[2].input["value"]
        self.location = rows[3].input["value"]

        month = get_selected(rows[4].find_all("option"), "selected")["value"]
        self.preliminary_month = parse_preliminary_month(int(month))
        duration = get_selected(rows[5].find_all("input"), "checked")["value"]
        self.duration_type = int(duration)

        if rows[6].input["value"]:
            start = rows[6].input["value"] + "T" + rows[7].input["value"]
            end_date = rows[9].input["value"] or rows[6].input["value"]
            end = end_date + "T" + rows[10].input["value"]

            self.start_time = datetime.fromisoformat(start)
            self.end_time = datetime.fromisoformat(end)
            self.start_location = rows[8].input["value"]
            self.end_location = rows[11].input["value"]
        else:
            self.start_time = None
            self.end_time = None
            self.start_location = None
            self.end_location = None

        st = rows[12].find_all(["input", "textarea"])
        self.all_classes = st[0].has_attr("checked")
        self.classes = st[2].get("value").split(", ") if st[2].get("value") else []
        self.students = st[4].text.split(", ") if st[4].text.strip() else []

        self.teachers = rows[13].textarea.text.split(", ")
        self.total_teachers = int(rows[13].input["value"])

        self.price = int(rows[14].input["value"])
        status = get_selected(rows[15].find_all("input"), "checked")
        self.approved = status["value"] == "1"
        self.notes = rows[16].textarea.text.strip()

    def __repr__(self) -> str:
        return f"<{type(self).__name__} id={self.id!r} name={self.name!r} organizator={self.organizator!r} start_time={repr(str(self.start_time))}>"
