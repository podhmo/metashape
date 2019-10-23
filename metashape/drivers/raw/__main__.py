if __name__ == "__main__":
    from metashape.cli import main
    from metashape.drivers.raw import emit

    main(emit=emit)
