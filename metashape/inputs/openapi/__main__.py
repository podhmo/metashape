from handofcats import as_command
from dictknife import loading
from metashape.inputs.openapi import Context, visit, emit


@as_command
def run(filename: str) -> None:
    d = loading.loadfile(filename)
    ctx = Context()
    visit(ctx, d)
    print(emit(ctx))
