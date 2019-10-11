import typing as t
import typing_extensions as tx
import typing_inspect

# TODO: move
JSONSchemaType = tx.Literal["boolean", "string", "integer", "number", "object", "array"]


class TypeInfoDict(tx.TypedDict, total=True):
    type: JSONSchemaType
    optional: bool


def resolve_type_info(
    typ: t.Type[t.Any], *, strict: bool = True, _nonetype=type(None)
) -> TypeInfoDict:
    optional = False
    if hasattr(typ, "__origin__"):  # xxx
        args = typing_inspect.get_args(typ)
        if len(args) == 2 and typ.__origin__ == t.Union:
            if args[0] == _nonetype:
                optional = True
                typ = args[1]
            elif args[1] == _nonetype:
                optional = True
                typ = args[0]

        if hasattr(typ, "__origin__"):  # xxx
            if issubclass(typ.__origin__, t.Sequence):
                return {"type": "array", "optional": optional}
            if issubclass(typ.__origin__, t.Mapping):
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
