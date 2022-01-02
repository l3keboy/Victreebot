# ------------------------------------------------------------------------- #
# VictreeBot                                                                #
#                                                                           #
# See LICENSE for more information. If this code is used, attribution       #
# would be appreciated.                                                     #
# Written by Luke Hendriks and Martijn Verlind                              #
# ------------------------------------------------------------------------- #
# IMPORTS
# Database and .env
import os
from dotenv import load_dotenv
# GitHub
from git import Repo

# .ENV AND .ENV VARIABLES
# Load .env
load_dotenv()
# Variables
# GitHub Variables
GITHUB_REPOSITORY_LOCAL = os.getenv('GITHUB_REPOSITORY_LOCAL')


class VersionHandler:
    def __init__(self):
        self.repo = Repo(GITHUB_REPOSITORY_LOCAL)
        self.remote = self.repo.remote("origin")
        self.version = f"{self.remote.fetch()[0].commit.count():,}"
        self.version_full = f"{self.repo.head.commit.summary}"

    @property
    def is_latest(self) -> bool:
        return self.repo.commit() == self.remote.fetch()[0].commit

    def update_version(self) -> None:
        self.repo.head.reset(index=True, working_tree=True)
        self.remote.pull()
