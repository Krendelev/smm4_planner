from collections import namedtuple

Scope = namedtuple("Scope", ["name", "scopes", "id", "range", "params"])
Record = namedtuple(
    "Record",
    ["vk", "tg", "fb", "pub_day", "pub_time", "text", "photo", "published", "range"],
)
PubData = namedtuple("PubData", ["range", "channels", "text", "photo", "delay"])

spreadsheet = Scope(
    name="spreadsheets",
    scopes=["https://www.googleapis.com/auth/spreadsheets"],
    id="1Te65OZgashZL52MQAVFAj7W6oC1GVaY-hxr336D5q1o",
    range="Лист1!A3:H",
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
