import io
import os

import requests
import telegram


def check_vk_response(response):
    if "error" in response:
        raise requests.HTTPError(response["error"]["error_msg"])
    return None


def get_upload_url(payload):
    url = "https://api.vk.com/method/photos.getWallUploadServer"
    params = {**payload, "group_id": os.environ["VK_GROUP_ID"]}
    response = requests.get(url, params=params).json()
    check_vk_response(response)
    return response["response"]["upload_url"]


def upload_picture(url, image):
    files = {"photo": (image.name, image.getvalue())}
    response = requests.post(url, files=files).json()
    check_vk_response(response)
    return response


def save_picture(payload, upload_info):
    url = "https://api.vk.com/method/photos.saveWallPhoto"
    params = {
        **payload,
        "group_id": os.environ["VK_GROUP_ID"],
        "server": upload_info["server"],
        "photo": upload_info["photo"],
        "hash": upload_info["hash"],
    }
    response = requests.post(url, params=params).json()
    check_vk_response(response)
    return response["response"][0]


def post_to_wall(payload, attachment, text):
    url = "https://api.vk.com/method/wall.post"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    params = {
        **payload,
        "owner_id": f"-{os.environ['VK_GROUP_ID']}",
        "from_group": 1,
        "attachments": attachment,
        "message": text,
    }
    response = requests.post(url, headers=headers, data=params).json()
    check_vk_response(response)
    return None


def post_to_vk(post):
    payload = {"access_token": os.environ["VK_ACCESS_TOKEN"], "v": 5.101}
    upload_url = get_upload_url(payload)
    attachment = None
    text = post["text"] and post["text"].getvalue().decode() or None
    if post["photo"]:
        upload_info = upload_picture(upload_url, post["photo"])
        pic_info = save_picture(payload, upload_info)
        attachment = f"photo{pic_info['owner_id']}_{pic_info['id']}"
    post_to_wall(payload, attachment, text)
    return None


def post_to_fb(post):
    url = f"https://graph.facebook.com/{os.environ['FB_GROUP_ID']}/feed"
    if post["photo"]:
        url = f"https://graph.facebook.com/{os.environ['FB_GROUP_ID']}/photos"
    text = post["text"] and post["text"].getvalue() or None
    files = post["photo"] and {"source": post["photo"].getvalue()} or None
    params = {"message": text, "access_token": os.environ["FB_MARKER"]}
    response = requests.post(url, params=params, files=files)
    response.raise_for_status()
    return None


def post_to_tg(post):
    chat_id = os.environ["CHANNEL_ID"]
    bot = telegram.Bot(os.environ["TELEGRAM_TOKEN"])
    if post["photo"]:
        bot.send_photo(chat_id=chat_id, photo=io.BytesIO(post["photo"].getvalue()))
    if post["text"]:
        bot.send_message(chat_id=chat_id, text=post["text"].getvalue().decode())
    return None
