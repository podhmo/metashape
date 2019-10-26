if __name__ == "__main__":
    from metashape.cli import main
    from metashape.drivers.raw.emit import emit

    main(emit=emit)
