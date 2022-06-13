# ------------------------------------------------------------------------- #
# VictreeBot                                                                #
#                                                                           #
# See LICENSE for more information. If this code is used, attribution       #
# would be appreciated.                                                     #
# Written by Luke Hendriks                                                  #
# ------------------------------------------------------------------------- #
# IMPORTS
import os
import shutil
import subprocess
import time

import nox

from pipelines import config

GIT = shutil.which("git")


@nox.session(reuse_venv=True)
def check_format(session: nox.Session) -> None:
    """Remove whitespace, run isort and black."""
    session.install("-r", "requirements.txt")

    session.run("isort", *config.PYTHON_PATHS, "-c")
    session.run("black", *config.PYTHON_PATHS, "--check")


@nox.session(reuse_venv=True)
def reformat(session: nox.Session) -> None:
    """Remove whitespace, run isort and black."""
    session.install("-r", "requirements.txt")

    remove_trailing_whitespaces(session)

    session.run("isort", *config.PYTHON_PATHS)
    session.run("black", *config.PYTHON_PATHS)


def remove_trailing_whitespaces(session: nox.Session, check_only: bool = False) -> None:
    session.log(f"Searching for stray trailing whitespaces in files ending in {config.REFORMAT_FILE_EXTS}")

    count = 0
    total = 0

    start = time.perf_counter()
    for path in config.FULL_REFORMAT:
        if os.path.isfile(path):
            total += 1
            count += remove_trailing_whitespaces_for_file(path, session, check_only)

        for root, dirs, files in os.walk(path, topdown=True, followlinks=False):
            for file in files:
                if file.casefold().endswith(config.REFORMAT_FILE_EXTS):
                    total += 1
                    count += remove_trailing_whitespaces_for_file(os.path.join(root, file), session, check_only)

                i = len(dirs) - 1
                while i >= 0:
                    if dirs[i] == "__pycache__":
                        del dirs[i]
                    i -= 1

    end = time.perf_counter()

    remark = "Good job! " if not count else ""
    message = "Had to fix" if not check_only else "Found issues in"
    session.log(
        f"{message} {count} file(s). "
        f"{remark}Took {1_000 * (end - start):.2f}ms to check {total} files in this project.",
    )

    if check_only and count:
        session.error("Trailing whitespaces found. Try running 'nox -s reformat-code' to fix them")


def remove_trailing_whitespaces_for_file(file: str, session: nox.Session, check_only: bool) -> bool:
    try:
        with open(file, "rb") as fp:
            lines = fp.readlines()
            new_lines = lines[:]

        for i in range(len(new_lines)):
            line = lines[i].rstrip(b"\n\r \t")
            line += b"\n"
            new_lines[i] = line

        if lines == new_lines:
            return False

        if check_only:
            session.log(f"Trailing whitespaces found in {file}")
            return True

        session.log(f"Removing trailing whitespaces present in {file}")

        with open(file, "wb") as fp:
            fp.writelines(new_lines)

        if GIT is not None:
            result = subprocess.check_call(
                [GIT, "add", file, "-vf"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=None
            )
            assert result == 0, f"`git add {file} -v' exited with code {result}"

        return True
    except Exception as ex:
        print("Failed to check", file, "because", type(ex).__name__, ex)
        return False
