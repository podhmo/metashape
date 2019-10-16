import logging
from metashape.analyze import typeinfo

logger = logging.getLogger(__name__)


def schema_type(info: typeinfo.TypeInfo) -> str:
    if "container" in info:
        raise ValueError("not supported")
        # if info["container"] in ("list", "tuple"):
        #     return "array"
        # elif info["container"] == "dict":
        #     return "object"
    elif "underlying" in info:
        typ = info["underlying"]
        if issubclass(typ, str):
            return "String"
        elif issubclass(typ, bool):
            return "Boolean"
        elif issubclass(typ, int):
            return "Integer"
    logger.warning("unexpected type: %r", typ)
    raise ValueError("unsupported %r", info)
