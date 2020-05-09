import typing as t
import typing_extensions as tx
import logging
import typing_inspect
from metashape.analyze import typeinfo


logger = logging.getLogger(__name__)
JSONSchemaType = tx.Literal["boolean", "string", "integer", "number", "object", "array"]


def schema_type(
    info: typeinfo.TypeInfo, *, unknown: JSONSchemaType = "object"
) -> JSONSchemaType:
    if info.is_container:
        if info.container.container in ("list", "tuple"):
            return "array"
        elif info.container.container == "dict":
            return "object"
    else:  # Atom
        typ = info.underlying
        if issubclass(typ, str):
            return "string"
        elif issubclass(typ, bool):
            return "boolean"
        elif issubclass(typ, int):
            return "integer"
        elif issubclass(typ, float):
            return "number"
    logger.warning("unexpected type: %r", typ)
    return unknown


# TODO: strict typing
# TODO: move
def enum(info: typeinfo.TypeInfo) -> t.Tuple[str]:
    typ = info.normalized
    origin = getattr(typ, "__origin__", None)
    if origin != tx.Literal:
        return ()  # type: ignore
    return typing_inspect.get_args(typ)  # type: ignore
