from handofcats import as_command
from dictknife import loading
from metashape.inputs.openapi import main


@as_command
def run(filename: str) -> None:
    d = loading.loadfile(filename)
    main(d)