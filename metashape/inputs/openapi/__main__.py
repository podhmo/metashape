from handofcats import as_command
from dictknife import loading
from metashape.inputs.openapi import main


@as_command  # type:ignore
def run(filename: str, *, verbose: bool = False, profile: bool = False) -> None:
    if profile:
        import cProfile
        import pstats

        prof = cProfile.Profile()
        prof.enable()

    d = loading.loadfile(filename)
    main(d, verbose=verbose)

    if profile:
        prof.disable()
        s = pstats.Stats(prof)
        s.dump_stats("metashape-inputs-openapi.prof")
