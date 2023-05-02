#!/usr/bin/env python

import argparse
import importlib
import subprocess
import sys


def ensure_environment(notebook, libraries):
    for lib_name in libraries:
        try:
            importlib.import_module(lib_name)

        except Exception:
            try:

                importlib.import_module(lib_name, f".{lib_name}")
            except ModuleNotFoundError or ImportError as ee:

                print(
                    f"{notebook} uses a library that is not present in the current environment: {ee.msg}",
                    file=sys.stderr,
                )
                exit(1)


def scan_notebook(notebook_path):
    notebook_path = notebook_path.replace(" ", "\\ ")
    command = f"pipreqsnb {notebook_path} --print"

    libraries = []
    p = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
    )

    while True:
        inline = p.stdout.readline()
        if not inline:
            break
        parsed_out = inline.decode("UTF-8").lower()
        if "==" in parsed_out:
            library = parsed_out.split("==")[0]
            libraries.append(library)
    print(libraries)

    ensure_environment(notebook_path, libraries)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--notebook", help="<Required> Set flag", required=True)
    args = parser.parse_args()
    scan_notebook(args.notebook)
