from __future__ import annotations
from typing import List, Union
import dataclasses


@dataclasses.dataclass
class Toplevel:
    site_name: str
    site_description: str
    site_author: str
    site_url: str

    # repository
    repo_name: str
    repo_url: str

    # Copyright
    copyright: str
    theme: Theme
    extra: Extra

    # extensions
    google_analytics: List[str]
    markdown_extensions: List[Union[str, CodehiliteExtension, TocExtension]]


@dataclasses.dataclass
class Extra:
    manifest: str
    social: List[Social]


@dataclasses.dataclass
class Social:
    type_: str  # TODO: support treated as "type" on dumping yaml
    link: str


@dataclasses.dataclass
class Theme:
    name: str
    language: str
    palette: Palette
    font: Font


@dataclasses.dataclass
class Palette:
    primary: str
    accent: str


@dataclasses.dataclass
class Font:
    text: str
    code: str


@dataclasses.dataclass
class CodehiliteExtension:
    @dataclasses.dataclass
    class Data:
        guess_lang: bool

    codehilite: "CodehiliteExtension.Data"


@dataclasses.dataclass
class TocExtension:
    @dataclasses.dataclass
    class Data:
        permalink: bool

    toc: "TocExtension.Data"
