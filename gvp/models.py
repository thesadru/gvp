from __future__ import annotations

import re
from datetime import datetime
from typing import Any, List, Optional

import gvp

__all__ = ["User", "Comment", "Article", "Contact", "StaticFile", "SearchResult", "News"]


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


class Contact:
    """A contact for a school employee"""

    def __init__(self, data) -> None:
        self.description: Optional[str] = data["description"]
        self.name: str = data["name"]
        self.phone: str = data["phone"]
        self._mail: str = data["mail"]
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
        return match.string

    @property
    def mail(self) -> str:
        """The full mail"""
        return self._mail + "@gvp.cz"


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
        return f"<{type(self).__name__} category={self.category!r} title={self.title!r}>"

    def complete(self) -> Any:
        """Complete the search result into a full class

        May return a StaticFile, an Article or a Comment
        """
        if self.category == "static":
            return StaticFile({"id": self._link, "title": self.title, "content": self.content})
        elif self.category == "articles":
            return gvp.article(self._link.split("-")[-1])
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
