# ------------------------------------------------------------------------- #
# VictreeBot                                                                #
#                                                                           #
# See LICENSE for more information. If this code is used, attribution       #
# would be appreciated.                                                     #
# Written by Luke Hendriks                                                  #
# ------------------------------------------------------------------------- #
# IMPORTS
import os

# Packages
MAIN_PACKAGE = "victreebot"
PIPELINES = "pipelines"

# Linting and configs
PYPROJECT_TOML = "pyproject.toml"

# Python paths for flake8 and reformat
PYTHON_PATHS = (MAIN_PACKAGE, PIPELINES, "noxfile.py")

# Reformatting paths
REFORMAT_FILE_EXTS = (
    ".py",
    ".pyx",
    ".pyi",
    ".yml",
    ".yaml",
    ".json",
    ".toml",
    ".md",
    ".gitignore",
    ".flake8",
    ".txt",
)

FULL_REFORMAT = (
    *PYTHON_PATHS,
    *(f for f in os.listdir(".") if os.path.isfile(f) and f.endswith(REFORMAT_FILE_EXTS)),
    ".github",
)
