# SMM planner

Plan your media campaign and post to [VKontakte](https://vk.com), [Facebook](https://facebook.com) and [Telegram](https://telegram.org/).

## How to install

Python3 should be already installed.
Then use `pip` (or `pip3`, if there is a conflict with Python2) to install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Lay out your plan in Google Sheets. It should look like this:

| ВКонтакте | Телеграм | Фейсбук | День        | Время | Статья | Картинки | Опубликовано |
| --------- | -------- | ------- | ----------- | ----- | ------ | -------- | ------------ |
| да        | нет      | да      | понедельник | 14    | ссылка | ссылка   | нет          |

You can append info to the table while script is running.

Upload text and image files to be posted to Google Drive. Images should be in `jpg`, `png` or `gif` format. Put links to the files in the table.

Enable the Google Sheets API, download client configuration and save the file `credentials.json` to your working directory. Create groups at FB and VK and Telegram channel. Put all your credentials into the `.env` file in the working directory:

```bash
FB_MARKER=replace_with_marker
FB_GROUP_ID=replace_with_group_id
TELEGRAM_TOKEN=replace_with_token
CHANNEL_ID=-replace_with_channel_id
VK_ACCESS_TOKEN=replace_with_token
VK_GROUP_ID=replace_with_group_id
```

Run `main.py`.

```bash
$ python main.py
```

### Project Goals

The code is written for educational purposes on online-course for web-developers [dvmn.org](https://dvmn.org/).
