import logging
import time

import requests
import telegram
from dotenv import load_dotenv
from googleapiclient.errors import HttpError

import utils
from data_providers import spreadsheet
from settings import TRUTH


CALLBACKS = {"text": utils.get_text_request, "photo": utils.get_photo_request}

logging.basicConfig(
    filename="post.log",
    filemode="w",
    format="%(asctime)s:%(message)s",
    level=logging.ERROR,
)

load_dotenv()

try:
    records = utils.get_records(spreadsheet)
except KeyError:
    exit("Your spreadsheet is empty")
except HttpError as error:
    exit(error)

for record in records:
    if not (record.text or record.photo) or TRUTH[record.published]:
        continue

    publication = utils.make_publication(record)

    post = {}
    for media, callback in CALLBACKS.items():
        file_id = getattr(publication, media)
        post[media] = utils.get_media(file_id, callback)

    time.sleep(publication.delay)

    for channel in publication.channels:
        try:
            channel(post)
        except AttributeError as error:
            logging.error(error)
        except requests.HTTPError as error:
            logging.error(error)
        except (telegram.error.NetworkError, telegram.error.TelegramError) as error:
            logging.error(error)

    utils.update_record(spreadsheet, publication.range)
