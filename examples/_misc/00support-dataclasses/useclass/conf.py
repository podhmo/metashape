from __future__ import annotations
from typing import List, Union, Dict, Any
import dataclasses
from metashape.constants import ORIGINAL_NAME


@dataclasses.dataclass
class Extra:
    manifest: str
    social: List[Social]


@dataclasses.dataclass
class Social:
    type_: str = dataclasses.field(metadata={ORIGINAL_NAME: "type"})
    link: str


class Toplevel:
    site_name: str = "Material for MkDocs"
    site_description: str = "A Material Design theme for MkDocs"
    site_author: str = "Martin Donath"
    site_url: str = "https://squidfunk.github.io/mkdocs-material/"

    # repository
    repo_name: str = "squidfunk/mkdocs-material"
    repo_url: str = "https://github.com/squidfunk/mkdocs-material"

    # Copyright
    copyright: str = "Copyright &copy; 2016 - 2017 Martin Donath"

    theme: Theme
    extra: Extra = Extra(
        manifest="manifest.webmanifest",
        social=[
            Social(type_="github", link="https://github.com/squidfunk"),
            Social(type_="twitter", link="https://twitter.com/squidfunk"),
            Social(type_="linkedin", link="https://linkedin.com/in/squidfunk"),
        ],
    )

    google_analytics: List[str] = ["UA-XXXXXXXX-X", "auto"]
    markdown_extensions: List[Union[str, Dict[str, Any]]] = [
        "admonition",
        {"codehilite": {"guess_lang": False}},
        {"toc": {"permalink": True}},
    ]

    class Theme:
        name: str = "material"
        language: str = "en"
        palette: Palette
        font: Font

        class Palette:
            primary: str = "indigo"
            accent: str = "indigo"

        class Font:
            text: str = "Roboto"
            code: str = "Roboto Mono"
