if __name__ == "__main__":
    from metashape.cli import main
    from metashape.outputs.raw.emit import emit

    main(emit=emit)
