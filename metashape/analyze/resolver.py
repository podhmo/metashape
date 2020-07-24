from __future__ import annotations
import typing as t
import logging
from metashape import constants
from metashape.langhelpers import reify
from metashape.types import T, MemberOrRef, MetaData
from metashape.marker import is_marked
from metashape._access import get_doc, get_name
from metashape import typeinfo
from .config import Config


logger = logging.getLogger(__name__)


class Resolver:
    def __init__(
        self,
        *,
        config: t.Optional[Config],
        is_member: t.Optional[t.Callable[[t.Type[T]], bool]] = None,
        named: t.Optional[t.Dict[int, str]] = None,
    ) -> None:
        self.config = config or Config()
        self._named = named or {}
        self._is_member = is_member or is_marked

    def is_member(self, ob: t.Type[T]) -> bool:
        return self._is_member(ob)

    @reify
    def metadata(self) -> MetaDataResolver:
        return MetaDataResolver()

    def resolve_typename(self, member: MemberOrRef) -> str:
        try:
            # support unhashable type. using id by naming cache ( t.List[X], .etc)
            return self._named.get(id(member)) or get_name(member)
        except AttributeError as e:
            logger.info("resolve_name: %r", e)
            return ""

    def resolve_typeinfo(self, typ: MemberOrRef) -> typeinfo.TypeInfo:
        # TODO: support _ForwardRef
        default = self.config.typeinfo_unexpected_handler
        try:
            return typeinfo.typeinfo(typ, default=default)
        except TypeError:
            return typeinfo.typeinfo(typ.__class__, default=default)

    def resolve_typeformat(self, info: typeinfo.TypeInfo) -> str:
        return info.supertypes[0].__name__.replace("_", "-")


class MetaDataResolver:
    def resolve_name(self, metadata: MetaData, *, default: str) -> str:
        name = metadata.get(constants.ORIGINAL_NAME)
        if name is not None:
            return str(name)
        if default.endswith("_") and not default.startswith("_"):
            return default[:-1]
        return default

    def resolve_doc(
        self, ob: object, *, verbose: bool = False, value: t.Optional[str] = None
    ) -> str:
        if value is not None:
            return value
        return get_doc(ob, verbose=verbose)

    def has_default(
        self,
        metadata: MetaData,
        *,
        name: str = constants.DEFAULT,
        missing: object = constants.MISSING,  # type:ignore
    ) -> bool:
        return metadata is not None and metadata.get(name, missing) is not missing

    def resolve_default(
        self, metadata: MetaData, *, name: str = constants.DEFAULT
    ) -> object:
        return metadata and metadata[name]

    def fill_extra_metadata(
        self, prop: t.Dict[str, t.Any], metadata: MetaData, *, name: str
    ) -> t.Dict[str, t.Any]:
        if metadata is not None and name in metadata:
            prop.update(metadata[name])
        return prop
