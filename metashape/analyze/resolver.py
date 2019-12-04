from __future__ import annotations
import typing as t
import logging
from metashape import constants
from metashape.langhelpers import reify
from metashape.types import T, Member, _ForwardRef, MetaData
from metashape.marker import is_marked
from metashape._access import get_doc, get_name
from . import typeinfo

logger = logging.getLogger(__name__)


class Resolver:  # ModuleResolver
    def __init__(
        self, *, is_member: t.Optional[t.Callable[[t.Type[T]], bool]] = None
    ) -> None:

        self._is_member = is_member or is_marked

    def is_member(self, ob: t.Type[T]) -> bool:
        return self._is_member(ob)

    def resolve_typename(self, member: t.Union[Member, _ForwardRef]) -> str:
        try:
            return get_name(member)
        except AttributeError as e:
            logger.info("resolve_name: %r", e)
            return ""

    @reify
    def typeinfo(self) -> TypeInfoResolver:
        return TypeInfoResolver()

    @reify
    def metadata(self) -> MetaDataResolver:
        return MetaDataResolver()


class TypeInfoResolver:
    def resolve(self, typ: t.Type[t.Any]) -> typeinfo.TypeInfo:
        return typeinfo.typeinfo(typ)

    def get_args(self, info: typeinfo.TypeInfo) -> t.List[typeinfo.TypeInfo]:
        return typeinfo.get_args(info)

    def get_custom(self, info: typeinfo.TypeInfo) -> t.Optional[t.Type[t.Any]]:
        return typeinfo.get_custom(info)

    def is_composite(self, info: typeinfo.TypeInfo) -> bool:
        return typeinfo.is_composite(info)


class MetaDataResolver:
    def resolve_name(self, metadata: MetaData, *, default: str):
        if metadata:
            return metadata.get(constants.ORIGINAL_NAME, default)
        return default

    def resolve_doc(self, ob: object, *, verbose: bool = False) -> str:
        return get_doc(ob, verbose=verbose)

    def has_default(
        self,
        metadata: MetaData,
        *,
        name: str = constants.DEFAULT,
        missing: object = constants.MISSING  # type:ignore
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
