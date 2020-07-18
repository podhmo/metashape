from __future__ import annotations
from typing import List, Union
from metashape.constants import ORIGINAL_NAME
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
    type_: str = dataclasses.field(metadata={ORIGINAL_NAME: "type"})
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
    codehilite: Data

    @dataclasses.dataclass
    class Data:
        guess_lang: bool


@dataclasses.dataclass
class TocExtension:
    toc: TocExtension.Data

    @dataclasses.dataclass
    class Data:
        permalink: bool
