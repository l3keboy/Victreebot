# ------------------------------------------------------------------------- #
# Husqy Discord Bot, see https://www.husqy.xyz for more info                #
#                                                                           #
# Copyright (C) Husqy - All Rights Reserved                                 #
# Unauthorized copying of this file, via any medium is strictly prohibited  #
# Proprietary and confidential                                              #
# Written by Luke Hendriks <luke@la-online.nl>, July 2021 (C)               #
# ------------------------------------------------------------------------- #
# IMPORTS
# Database and .env
import os
from dotenv import load_dotenv
import asyncpg
# Own Files
from utils import LoggingHandler

# .ENV AND .ENV VARIABLES
# Load .env
load_dotenv()
# Variables
# Database Variables
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_DATABASENAME = os.getenv("DB_DATABASENAME")


async def acquire_database():
    try:
        database = await asyncpg.create_pool(
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASENAME,
            host=DB_HOST,
            port=int(DB_PORT),
        )
        return database
    except Exception as e:
        LoggingHandler.LoggingHandler().logger_victreebot_database.info(f"Connection to databse failed: {e}")
        return
