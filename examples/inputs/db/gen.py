import typing as t
from sqlalchemy import create_engine, MetaData
from handofcats import as_command
from prestring.python import Module

# TODO: label
# TODO: nullable
# TODO: index
# TODO: constraints
# TODO: primary key
# TODO: original column name


def resolve_pytype(col, *, m) -> t.Type[t.Any]:
    try:
        typ = col.type.python_type
        if typ.__module__ != "builtins":
            m.g.from_(typ.__module__).import_(typ.__qualname__)
        return typ
    except NotImplementedError:
        return t.Any


def str_from_pytype(typ: t.Type[t.Any], *, nullable: bool = False) -> str:
    if nullable:
        return f"t.Optional[{typ.__qualname__}]"
    return typ.__qualname__


def gen(metadata: MetaData, *, m):
    for table in metadata.sorted_tables:
        if str(table.name) == "sqlite_sequence":
            continue

        with m.class_(str(table.name)):
            # m.docstring("hello")
            m.stmt("__metadata__ = {}", {"tablename": str(table.name)})
            m.sep()
            for c in table.columns:
                metadata = {}
                if c.primary_key:
                    metadata["primary_key"] = True

                typ = resolve_pytype(c, m=m)
                if not metadata:
                    m.stmt("{}: {}", c.name, str_from_pytype(typ, nullable=c.nullable))
                else:
                    m.g.from_("metashape.declarative").import_("field")
                    m.stmt(
                        "{}: {} = field(default=None, metadata={})",
                        c.name,
                        str_from_pytype(typ, nullable=c.nullable),
                        metadata,
                    )
    return m


@as_command
def run(*, db: str) -> None:
    engine = create_engine(db)
    metadata = MetaData(bind=engine)
    metadata.reflect()

    m = Module(import_unique=True)
    m.g = m.submodule()
    m.g.from_("__future__").import_("annotations")
    m.g.import_("typing", as_="t # noqa F401")

    m = gen(metadata, m=m)
    if m.g.imported_set:
        m.g.sep()
    print(m)
