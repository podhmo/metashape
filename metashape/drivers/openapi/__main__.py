if __name__ == "__main__":
    from metashape.cli import main
    from metashape.drivers.openapi import emit

    main(emit=emit)
