import typing as t
import typing_extensions as tx
import logging
import typing_inspect
from metashape.analyze import typeinfo


logger = logging.getLogger(__name__)
JSONSchemaType = tx.Literal["boolean", "string", "integer", "number", "object", "array"]


def schema_type(info: typeinfo.TypeInfo, *, unknown: str = "object") -> str:
    # todo: accessor
    if "container" in info:
        if info["container"] in ("list", "tuple"):
            return "array"
        elif info["container"] == "dict":
            return "object"
    elif "underlying" in info:
        typ = info["underlying"]
        if issubclass(typ, str):
            return "string"
        elif issubclass(typ, bool):
            return "boolean"
        elif issubclass(typ, int):
            return "integer"
        elif issubclass(typ, float):
            return "number"
    logger.info("unexpected type: %r", typ)
    return unknown


def enum(info: typeinfo.TypeInfo) -> t.Tuple[str]:
    typ = info["normalized"]
    origin = getattr(typ, "__origin__", None)  # xxx
    if origin != tx.Literal:
        return ()
    return typing_inspect.get_args(typ)
