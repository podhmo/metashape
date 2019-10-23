import logging
from metashape.analyze import typeinfo
from metashape.types import ID

logger = logging.getLogger(__name__)


def _underlying_schema_type(info: typeinfo.TypeInfo) -> str:
    typ = info["underlying"]
    if info["supertypes"] and info["supertypes"][0] == ID:
        return "ID"

    if issubclass(typ, str):
        return "String"
    elif issubclass(typ, bool):
        return "Boolean"
    elif issubclass(typ, float):
        return "Float"
    elif issubclass(typ, int):
        return "Int"
    elif info["custom"] is not None:  # t.Type?
        return typ.__name__
    logger.warning("unexpected type: %r", info)
    raise ValueError("unsupported %r", info)


def schema_type(info: typeinfo.TypeInfo) -> str:
    if "container" in info:
        # dict? (additionalProperties?)
        if info["container"] in ("list", "tuple") and len(info["args"]) == 1:
            typ = schema_type(info["args"][0])
            typ = f"[{typ}]"
            if info["is_optional"]:
                typ = f"{typ}!"
            return typ
    elif "underlying" in info:
        typ = _underlying_schema_type(info)
        if info["is_optional"]:
            typ = f"{typ}!"
        return typ
    logger.warning("unexpected type: %r", info)
    raise ValueError("unsupported %r", info)
