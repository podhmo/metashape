if __name__ == "__main__":
    from metashape.cli import main
    from metashape.outputs.graphql import codegen

    main(emit=codegen)
