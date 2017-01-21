#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import telegram
import praw
import os
import logging
import html

log = logging.getLogger()
log.setLevel(logging.INFO)

if 'TOKEN' not in os.environ:
    raise RuntimeError("Put bot token in TOKEN env var")

if 'SUBREDDIT' not in os.environ:
    raise RuntimeError("Put subreddit name in SUBREDDIT env var")

if 'CHANNEL' not in os.environ:
    raise RuntimeError("Put channel name in CHANNEL env var")

TOKEN = os.environ['TOKEN']
SUBREDDIT = os.environ['SUBREDDIT']
CHANNEL = os.environ['CHANNEL']

r = praw.Reddit(user_agent='Reddit Telegram poster by /u/roignac',
                site_name="default")
r.read_only = True

bot = telegram.Bot(token=TOKEN)
subreddit = r.subreddit(SUBREDDIT)

for submission in subreddit.stream.submissions():
    try:
        link = "https://redd.it/{id}".format(id=submission.id)
        flair = html.escape(submission.link_flair_text or '')
        title = html.escape(submission.title or '')
        user = html.escape(submission.author.name or '')

        message_template = "<a href='{link}'>{title}</a> by <b>{user}</b> ({flair})"
        if not flair:
            message_template = "<a href='{link}'>{title}</a> by <b>{user}</b>"

        message = message_template.format(flair=flair, title=title, link=link, user=user)

        log.info("Posting {}".format(message))
        bot.sendMessage(chat_id=CHANNEL, parse_mode=telegram.ParseMode.HTML, text=message)
    except Exception as e:
        log.exception("Error parsing {}".format(link))
