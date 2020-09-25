import praw
import configparser
import logging
import logging.config
import datetime
import typing
import json
import smtplib
import logging
import sys
from discordhandler import DiscordHandler
from logging.handlers import SMTPHandler
from datetime import datetime as dt


logging.config.fileConfig("basic_logging_config.ini")
logger = logging.getLogger("eimmk")


# TODO more error logging
# TODO implement ignored config values


class PostNotFoundException(Exception):
    """
    Gets thrown if the script can't fetch the latest wednesday post for 
    some reason
    """
    pass


def __load_config():
    """Loads the configuration from the config.ini file.

    Returns:
        configparser.SectionProxy: relevant config dictionary
    """
    config = configparser.ConfigParser()
    config.read("config.ini", encoding="utf-8")
    return config


def __setup_logging() -> logging.Logger:
    """Sets up logging to console and files.
    """
    formatter = logger.handlers[0].formatter
    if config.getboolean("logging","enable_mail_logging"):
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
    if config.getboolean("logging","enable_discord_logging"):
        dh = DiscordHandler(config["discord_logging"]["username"],
                            config["discord_logging"]["webhook_url"])
        dh.setFormatter(formatter)
        dh.setLevel(logging.WARNING)
        logger.addHandler(dh)
    logger.debug("Successfully setup logger")
    return logger


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
        logger.info("It's not wednesday (I think)")
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
        logger.info("Already have seen today's post")
        return None
    logger.debug("Fetching latest post")

    try:
        post = __fetch_latest_wednesday_post()
    except PostNotFoundException:
        logger.info("No new post found")
        return None

    logger.info("New post found")
    last_posts[key] = post
    with open("last_posts.json", "a", encoding="utf-8") as f:
        json.dump(last_posts, f)
    return last_posts


def __fetch_latest_wednesday_post() -> praw.models.Submission:
    latest_submissions = reddit.redditor(
        "SmallLebowsky").submissions.new(limit=20)
    for submission in latest_submissions:
        # BUG Has to check if wednesday in Germany but checks for UTC!
        if __is_date_wednesday(datetime.utcfromtimestamp(submission
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

config = __load_config()
__setup_logging()
reddit = __init_reddit()

if __name__ == "__main__":
    logger.warning("Test")
    # post = get_new_post()
    # if post is None:
    #     logger.info("No new post found, exiting...")
    # else:
