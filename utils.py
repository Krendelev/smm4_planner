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

from data_providers import PubData, Record, files
from settings import BOUNDARY, MARK, TRUTH, WEEKDAYS
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


def fetch_records(scope):
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


def get_record(records):
    for record in records:
        if (record.text or record.photo) and record.published != MARK[True]:
            return record
    return None


def make_publication(record):
    channels = itertools.compress(
        (post_to_vk, post_to_tg, post_to_fb),
        (TRUTH[record.vk], TRUTH[record.tg], TRUTH[record.fb]),
    )
    pub_data = PubData(
        range=record.range,
        channels=channels,
        text=get_id(record.text),
        photo=get_id(record.photo),
    )
    return pub_data


def get_text_request(service, file_id, scope=files):
    discovery_resource = getattr(service, scope.name)()
    return discovery_resource.export_media(fileId=file_id, mimeType="text/plain")


def get_photo_request(service, file_id):
    return service.files().get_media(fileId=file_id)


def get_file_name(service, file_id):
    file_info = service.files().get(fileId=file_id, fields="name").execute()
    return file_info["name"]


def download_file(request):
    result = io.BytesIO()
    downloader = MediaIoBaseDownload(result, request)
    done = False
    while done is False:
        _, done = downloader.next_chunk()
    return result


def get_media(file_id, callback):
    service = get_service(files)
    media = download_file(callback(service, file_id))
    media.name = get_file_name(service, file_id)
    return media


def update_record(scope, range_):
    service = get_service(scope)
    discovery_resource = getattr(service, scope.name)()

    name, pos = split_range(range_)
    value_range_body = {"values": [[MARK[True]]]}
    request = discovery_resource.values().update(
        spreadsheetId=scope.id,
        range=f"{name}!H{pos}:H{pos}",
        valueInputOption="RAW",
        body=value_range_body,
    )
    request.execute()
    return None


def get_id(text):
    pattern = re.compile(r"(?:.+=)([^\"]+)")
    found = re.findall(pattern, text)
    return found[0] if found else None


def pub_datetime(weekday, hour):
    today = datetime.datetime.today()
    days_ahead = (WEEKDAYS[weekday] - today.weekday() + 7) % 7
    delta = datetime.timedelta(days=days_ahead)
    pub_time = datetime.time(hour=hour)
    return datetime.datetime.combine(today + delta, pub_time)


def time_is_now(then):
    now = datetime.datetime.today()
    return (now - then).seconds < BOUNDARY


def split_range(range_):
    name, boundaries = range_.split("!")
    start, _ = boundaries.split(":")
    start = int(start.lstrip(string.ascii_uppercase))
    return name, start
