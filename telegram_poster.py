#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import telegram
import praw
import os
import logging
import html
import sys

from time import sleep
from datetime import datetime


log = logging.getLogger('telegram_poster')
log.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)


if 'TOKEN' not in os.environ:
    raise RuntimeError("Put bot token in TOKEN env var")

if 'SUBREDDIT' not in os.environ:
    raise RuntimeError("Put subreddit name in SUBREDDIT env var")

if 'CHANNEL' not in os.environ:
    raise RuntimeError("Put channel name in CHANNEL env var")

TOKEN = os.environ['TOKEN']
SUBREDDIT = os.environ['SUBREDDIT']
CHANNEL = os.environ['CHANNEL']
START_TIME = datetime.utcnow().timestamp()


# Filter out old submissions here by reading a 'last_submission.id file'
def read_last_submission_id():
    try:
        with open('last_submission.id', 'r') as f:
            return f.read().strip()
    except:
        return None


def write_last_submission_id(submission_id):
    try:
        with open('last_submission.id', 'w') as f:
            f.write(submission_id)
    except:
        log.exception("Error writing submission ID")


start_posting = False
last_submission_id = read_last_submission_id()

if not last_submission_id:
    log.info("Last posted submission not found, starting with all submissions")
    start_posting = True
else:
    log.info("Last posted submission is {}".format(last_submission_id))

r = praw.Reddit(user_agent='Reddit Telegram poster by /u/roignac',
                site_name="default")
r.read_only = True
subreddit = r.subreddit(SUBREDDIT)

bot = telegram.Bot(token=TOKEN)

while True:
    try:
        for submission in subreddit.stream.submissions():
            try:
                link = "https://redd.it/{id}".format(id=submission.id)
                if not start_posting and submission.created_utc < START_TIME:
                    log.info("Skipping {} - last sent submission not yet found".format(
                        submission.id))
                    if submission.id == last_submission_id:
                        start_posting = True
                    continue

                flair = html.escape(submission.link_flair_text or '')
                title = html.escape(submission.title or '')
                user = html.escape(submission.author.name or '')

                message_template = "<a href='{link}'>{title}</a> by <b>{user}</b> ({flair})"
                if not flair:
                    message_template = "<a href='{link}'>{title}</a> by <b>{user}</b>"

                message = message_template.format(flair=flair, title=title, link=link, user=user)

                log.info("Posting {}".format(link))
                bot.sendMessage(chat_id=CHANNEL, parse_mode=telegram.ParseMode.HTML, text=message)
                write_last_submission_id(submission.id)
            except Exception as e:
                log.exception("Error parsing {}".format(link))
    except Exception as e:
        log.exception("Error fetching new submissions, restarting in 10 secs")
        sleep(10)
