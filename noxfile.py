# IMPORTS
import os
import runpy
import sys

PIPELINES = "pipelines"
sys.path.append(os.getcwd())


for f in os.listdir(PIPELINES):
    if f.endswith(".nox.py"):
        runpy.run_path(os.path.join(PIPELINES, f))
