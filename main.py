import logging
import time

import requests
import telegram
from dotenv import load_dotenv
from googleapiclient.errors import HttpError

import utils
from data_providers import spreadsheet
from settings import DELAY, MARK, TRUTH


CALLBACKS = {"text": utils.get_text_request, "photo": utils.get_photo_request}

logging.basicConfig(
    filename="post.log",
    filemode="w",
    format="%(asctime)s:%(message)s",
    level=logging.ERROR,
)

load_dotenv()

while True:
    try:
        records = utils.fetch_records(spreadsheet)
    except KeyError:
        exit("Your spreadsheet is empty")
    except HttpError as error:
        exit(error)

    record = utils.get_record(records)
    if record:
        publication_time = utils.pub_datetime(record.pub_day, record.pub_time)
    else:
        time.sleep(DELAY)
        continue

    if utils.time_is_now(publication_time):
        publication = utils.make_publication(record)
        post = {}
        for media, callback in CALLBACKS.items():
            file_id = getattr(publication, media)
            post[media] = file_id and utils.get_media(file_id, callback) or None

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

    time.sleep(DELAY)
