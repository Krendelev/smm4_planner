import datetime
import io
import itertools
import os
import pickle
import re
import string

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from data_providers import PubData, Record, files, spreadsheet
from settings import TRUTH, WEEKDAYS
from social_media import post_to_fb, post_to_tg, post_to_vk


# modified from Google API docs
def get_credentials(scope):
    creds = None
    token_name = f"{scope.name}.pickle"
    if os.path.exists(token_name):
        with open(token_name, "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", scope.scopes
            )
            creds = flow.run_local_server(port=0)

        with open(token_name, "wb") as token:
            pickle.dump(creds, token)
    return creds


def get_service(scope):
    credentials = get_credentials(scope)
    service = build(*scope.params, credentials=credentials)
    return service


def get_records(scope):
    service = get_service(scope)
    discovery_resource = getattr(service, scope.name)()

    name, start = split_range(scope.range)
    for num in itertools.count(start=start):
        range_ = f"{name}!{num}:{num}"
        result = (
            discovery_resource.values()
            .get(spreadsheetId=scope.id, range=range_, valueRenderOption="FORMULA")
            .execute()
        )
        record = result.get("values", [])
        if not record:
            break
        record[0].append(range_)
        yield Record._make(record[0])


def extract_data(record):
    channels = [
        channel[0]
        for channel in zip(
            (post_to_vk, post_to_tg, post_to_fb),
            (TRUTH[record.vk], TRUTH[record.tg], TRUTH[record.fb]),
        )
        if all(channel)
    ]
    pub_data = PubData(
        range=record.range,
        channels=channels,
        text=get_id(record.text),
        photo=get_id(record.photo),
        delay=get_delay(record.pub_day, record.pub_time),
    )
    return pub_data


def get_text_request(service, file_id, scope=files):
    discovery_resource = getattr(service, scope.name)()
    return discovery_resource.export_media(fileId=file_id, mimeType="text/plain")


def get_photo_request(service, file_id):
    return service.files().get_media(fileId=file_id)


def get_photo_name(service, file_id):
    file_info = service.files().get(fileId=file_id, fields="name").execute()
    return file_info["name"]


def download_file(request):
    result = io.BytesIO()
    downloader = MediaIoBaseDownload(result, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
    return result


def get_media(file_id, callback):
    service = get_service(files)
    bytes_io = file_id and download_file(callback(service, file_id)) or None
    if "photo" in callback.__name__ and file_id:
        bytes_io.name = get_photo_name(service, file_id)
    return bytes_io


def update_record(scope, range_):
    service = get_service(scope)
    discovery_resource = getattr(service, scope.name)()

    published = {val: key for key, val in TRUTH.items()}
    name, pos = split_range(range_)
    value_range_body = {"values": [[published[True]]]}
    request = (
        discovery_resource.values().update(
            spreadsheetId=scope.id,
            range=f"{name}!H{pos}:H{pos}",
            valueInputOption="RAW",
            body=value_range_body,
        )
    ).execute()

    return None


def get_id(text):
    pattern = re.compile(r"(?:.+=)([^\"]+)")
    found = re.findall(pattern, text)
    return found[0] if found else None


def get_delay(weekday, hour):
    today = datetime.datetime.today()
    days = (WEEKDAYS[weekday] - today.weekday() + 7) % 7
    delta = datetime.timedelta(days=days)
    fin_time = datetime.time(hour=hour)
    fin_date = datetime.datetime.combine(today + delta, fin_time)
    return int(fin_date.timestamp() - today.timestamp())


def split_range(range_):
    name, boundaries = range_.split("!")  # "Лист1!A3:H"
    start, _ = boundaries.split(":")
    start = start.lstrip(string.ascii_uppercase)
    return name, int(start)
