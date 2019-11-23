if __name__ == "__main__":
    from metashape.cli import main
    from metashape.outputs.raw import codegen

    main(emit=codegen)
