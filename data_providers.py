import os
from collections import namedtuple

from dotenv import load_dotenv

load_dotenv()

Scope = namedtuple("Scope", ["name", "scopes", "id", "range", "params"])
Record = namedtuple(
    "Record",
    ["vk", "tg", "fb", "pub_day", "pub_time", "text", "photo", "published", "range"],
)
PubData = namedtuple("PubData", ["range", "channels", "text", "photo", "delay"])

spreadsheet = Scope(
    name="spreadsheets",
    scopes=["https://www.googleapis.com/auth/spreadsheets"],
    id=os.environ["SPREADSHEET_ID"],
    range=os.environ["SPREADSHEET_RANGE"],
    params=["sheets", "v4"],
)

files = Scope(
    name="files",
    scopes=[
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/documents.readonly",
    ],
    id=None,
    range=None,
    params=["drive", "v3"],
)
