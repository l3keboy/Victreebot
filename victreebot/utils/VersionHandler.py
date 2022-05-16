# ------------------------------------------------------------------------- #
# VictreeBot                                                                #
#                                                                           #
# See LICENSE for more information. If this code is used, attribution       #
# would be appreciated.                                                     #
# Written by Luke Hendriks                                                  #
# ------------------------------------------------------------------------- #
# IMPORTS
import os

from dotenv import load_dotenv
from git import Repo

load_dotenv()
GITHUB_LOCAL_REPO_LOCATION = os.getenv("GITHUB_LOCAL_REPO_LOCATION")


# ------------------------------------------------------------------------- #
# VERSIONHANDLER CLASS #
# ------------------------------------------------------------------------- #
class VersionHandler:
    """VersionHandler class for the bot using github"""

    def __init__(self):
        """Initialize variables"""
        self.repo = Repo(GITHUB_LOCAL_REPO_LOCATION)
        self.remote = self.repo.remote("origin")
        self.version = f"{self.remote.fetch()[0].commit.count():,}"
        self.version_full = f"{self.repo.head.commit.summary}"

    @property
    def is_latest(self) -> bool:
        """Check if the local version is the latest commit"""
        return self.repo.commit() == self.remote.fetch()[0].commit

    def update_version(self) -> None:
        """Update the bot"""
        self.repo.head.reset(index=True, working_tree=True)
        self.remote.pull()
