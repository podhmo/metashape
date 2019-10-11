import typing as t
import typing_extensions as tx
import typing_inspect

# TODO: move
JSONSchemaType = tx.Literal["boolean", "string", "integer", "number", "object", "array"]


class TypeInfoDict(tx.TypedDict, total=True):
    type: JSONSchemaType
    optional: bool


def _is_typing_type(typ: t.Type[t.Any]) -> bool:
    return hasattr(typ, "__origin__")


def _get_typing_origin(typ: t.Type[t.Any]) -> t.Optional[t.Type[t.Any]]:
    return getattr(typ, "__origin__", None)


def type_info(
    typ: t.Type[t.Any], *, strict: bool = True, _nonetype=type(None)
) -> TypeInfoDict:
    optional = False
    if _is_typing_type(typ):
        args = typing_inspect.get_args(typ)
        if len(args) == 2 and typ.__origin__ == t.Union:
            if args[0] == _nonetype:
                optional = True
                typ = args[1]
            elif args[1] == _nonetype:
                optional = True
                typ = args[0]

        if _is_typing_type(typ):
            origin = _get_typing_origin(typ)
            if origin == tx.Literal:
                typ = type(typing_inspect.get_args(typ)[0])
            elif issubclass(origin, t.Sequence):
                return {"type": "array", "optional": optional}
            elif issubclass(origin, t.Mapping):
                return {"type": "object", "optional": optional}

    if issubclass(typ, str):
        return {"type": "string", "optional": optional}
    elif issubclass(typ, bool):
        return {"type": "boolean", "optional": optional}
    elif issubclass(typ, int):
        return {"type": "integer", "optional": optional}
    elif issubclass(typ, float):
        return {"type": "number", "optional": optional}
    elif hasattr(typ, "keys"):
        return {"type": "object", "optional": optional}
    elif issubclass(typ, (list, tuple)):  # sequence?
        return {"type": "array", "optional": optional}
    else:
        return {"type": "object", "optional": optional}


# TODO: enum's description
def enum(typ: t.Type[t.Any]) -> t.Tuple[str]:
    origin = _get_typing_origin(typ)
    if origin is None:
        return ()
    if origin != tx.Literal:
        return ()
    return typing_inspect.get_args(typ)
