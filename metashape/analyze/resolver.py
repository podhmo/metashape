import typing as t
import logging
from metashape import constants
from metashape.types import T, Member, _ForwardRef, MetaData
from metashape.marker import is_marked
from metashape._access import get_doc, get_name
from . import typeinfo

logger = logging.getLogger(__name__)


# TODO: remove this?
class Resolver:
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

    def resolve_doc(self, ob: object, *, verbose: bool = False) -> str:
        return get_doc(ob, verbose=verbose)

    def has_default(
        self,
        metadata: MetaData,
        *,
        name: str = constants.DEFAULT,
        missing: object = constants.MISSING
    ) -> bool:
        return metadata is not None and metadata.get(name, missing) is not missing

    def resolve_default(
        self, metadata: MetaData, *, name: str = constants.DEFAULT
    ) -> object:
        return metadata and metadata[name]

    def fill_metadata(
        self, prop: t.Dict[str, t.Any], metadata: MetaData, *, name: str
    ) -> t.Dict[str, t.Any]:
        if metadata is not None and name in metadata:
            prop.update(metadata[name])
        return prop

    def resolve_type_info(self, typ: t.Type[t.Any]) -> typeinfo.TypeInfo:
        return typeinfo.typeinfo(typ)
