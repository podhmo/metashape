import typing as t
import sys
import subprocess
import os.path
import inflection


# TODO: drop json2models
def run(filename: str, name: t.Optional[str] = None) -> None:
    name = inflection.camelize(name or os.path.splitext(os.path.basename(filename))[0])
    cmd = ["json2models", "-m", name, filename, "-s", "flat"]
    print("  generated by:", *cmd, file=sys.stderr)

    p = subprocess.run(cmd, stdout=subprocess.PIPE, text=True)
    i = 0
    for line in p.stdout.split("\n"):
        if i >= 2:
            print(line)
        elif '"""' in line:
            i += 1


def main(argv=None):
    import argparse

    parser = argparse.ArgumentParser(description=None)
    parser.print_usage = parser.print_help
    parser.add_argument("filename")
    args = parser.parse_args(argv)
    run(**vars(args))


if __name__ == "__main__":
    main()
