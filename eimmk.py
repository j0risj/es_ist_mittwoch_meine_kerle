import configparser
import datetime
import json
import logging
import logging.config
import smtplib
import sys
import typing
from datetime import datetime as dt
from logging.handlers import SMTPHandler

import praw

from discordhandler import DiscordHandler

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    "[%(asctime)s][%(name)s][%(levelname)s]: %(message)s", "%Y-%m-%d %H:%M:%S")
ch = logging.StreamHandler()
ch.setFormatter(formatter)
fh = logging.FileHandler("EiMmK.log", encoding="utf-8")
fh.setFormatter(formatter)
fh.setLevel(logging.INFO)
logger.addHandler(ch)
logger.addHandler(fh)

config = configparser.ConfigParser()
try:
    config.read("config_default.ini", encoding="utf-8")
    config.read("config.ini", encoding="utf-8")
except Exception:
    logger.exception("Unexpected exception while trying to read"
                     + "config file")


# TODO more error logging
# TODO implement ignored config values


class PostNotFoundException(Exception):
    """
    Gets thrown if the script can't fetch the latest wednesday post for 
    some reason
    """
    pass


def __setup_advanced_logging() -> None:
    """Sets up advanced logging per mail and Discord
    """
    if config.getboolean("logging", "enable_mail_logging"):
        mailcfg = dict(config.items("mail_logging"))
        mailhost = (mailcfg["mailhost"], mailcfg["mailport"])
        toaddrs = mailcfg["toaddrs"].split(",")
        credentials = (mailcfg["username"], mailcfg["password"])
        eh = SMTPHandler(mailhost=mailhost,
                         fromaddr=mailcfg["fromaddr"],
                         toaddrs=toaddrs,
                         subject=mailcfg["subject"],
                         credentials=credentials,
                         secure=(),
                         timeout=config.getint("mail_logging",
                                               "timeout"))
        eh.setFormatter(formatter)
        eh.setLevel(logging.WARNING)
        logger.addHandler(eh)

    if config.getboolean("logging", "enable_discord_logging"):
        dh = DiscordHandler(config["discord_logging"]["username"],
                            config["discord_logging"]["webhook_url"])
        dh.setFormatter(formatter)
        dh.setLevel(logging.WARNING)
        logger.addHandler(dh)
    logger.debug("Successfully setup advanced loggers")
    
# TODO move somewhere else?
__setup_advanced_logging()


def __init_reddit() -> praw.Reddit:
    """Initializes a reddit instance using the application read only 
    pipeline.

    Returns:
        praw.Reddit: Initialized reddit instance
    """
    reddit = praw.Reddit(client_id=config["reddit"]["client_id"],
                         client_secret=config["reddit"]["client_secret"],
                         user_agent=config["reddit"]["user_agent"])
    logger.debug("Successfully initialized praw reddit instance")
    return reddit


def get_new_post() -> typing.Optional[praw.models.Submission]:
    """Checks for a new wednesday post and returns it if available

    Returns:
        typing.Optional[praw.models.Submission]: The new wednesday post
        or None if none available or already fetched today
    """

    if __is_date_wednesday(dt.now()):
        logger.debug("It's not wednesday (I think)")
        return None
    try:
        with open("last_posts.json", "r", encoding="utf-8") as f:
            last_posts = json.loads(f.read())
    except Exception:
        logger.exception("Something went wrong reading the "
                         + "last_posts.json file, "
                         + "assuming first-time run")
        last_posts = {}
    key = dt.now().strftime("%Y-%m-%d")
    if key in last_posts:
        logger.debug("Already have seen today's post")
        return None
    logger.debug("Fetching latest post")

    try:
        post = __fetch_latest_wednesday_post()
    except PostNotFoundException:
        logger.info("No new post found")
        return None

    logger.info("New post found")
    last_posts[key] = post.permalink
    with open("last_posts.json", "a", encoding="utf-8") as f:
        json.dump(last_posts, f)
    return post

def get_new_post_url() -> typing.Optional[str]:
    post = get_new_post()
    if post is not None:
        return "https://www.reddit.com" + post.permalink   


def __fetch_latest_wednesday_post() -> praw.models.Submission:
    reddit = __init_reddit()
    latest_submissions = reddit.redditor(
        "SmallLebowsky").submissions.new(limit=20)
    for submission in latest_submissions:
        # BUG Has to check if wednesday in Germany but checks for UTC!
        if __is_date_wednesday(dt.utcfromtimestamp(submission
                                                         .created_utc)):
            if "Mittwoch" in submission.title:
                return submission
            else:
                raise PostNotFoundException


def __is_date_wednesday(date: dt) -> bool:
    """Checks if a given date is a wednesday

    Args:
        date (dt): Date

    Returns:
        bool: True if wednesday, False if not
    """
    return (date.isoweekday() == 3)


def __get_last_wednesday_date(now: dt = None) -> datetime.date:
    """Returns the date of the last wednesday before the current date.

    If the current date is a wednesday, the current date gets returned.
    The datetime object has all time values set to zero.

    Args:
        now (dt, optional): Date. Defaults to None.

    Returns:
        datetime.date: Date of the wednesday before the current date.
    """
    if now is None:
        now = dt.utcnow()
    weekday = now.isoweekday()
    if weekday < 3:
        tdelta = datetime.timedelta(days=-4 - weekday)
    elif weekday > 3:
        tdelta = datetime.timedelta(days=3 - weekday)
    else:
        tdelta = datetime.timedelta()
    now = now + tdelta
    now = dt.combine(now.date(), datetime.time())
    return now

if __name__ == "__main__":
    logger.name = "eimmk"
    try:
        print(get_new_post_url())
    except Exception:
        logger.exception("Unexpected exception caught")
