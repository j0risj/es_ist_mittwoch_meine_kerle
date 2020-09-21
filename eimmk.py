import praw
import configparser
import logging
import datetime
import typing
import json
import smtplib
import logging
from datetime import datetime as dt

CONFIG = __load_config()
logger = logging.getLogger("EiMmK")
REDDIT = __init_reddit()

class PostNotFoundException(Exception):
    """
    Gets thrown if the script can't fetch the latest wednesday post for some reason
    """

    pass

def __load_config():
    """Loads the configuration from the config.ini file.

    Returns:
        configparser.SectionProxy: relevant config dictionary
    """
    config = configparser.ConfigParser()
    config.read("config.ini")
    config = config["DEFAULT"]
    return config

def __setup_logging() -> None:
    """Sets up logging to console and files.
    """
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s]: %(message)s", "%Y-%m-%d %H:%M:%S")
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    fh = logging.FileHandler("EiMmK.log", encoding="utf-8")
    fh.setFormatter(formatter)
    fh.setLevel(logging.INFO)
    fh_debug = logging.FileHandler("EiMmK_debug.log", encoding="utf-8")
    fh_debug.setFormatter(formatter)
    fh_debug.setLevel(logging.DEBUG)
    logger.addHandler(ch)
    logger.addHandler(fh)
    logger.addHandler(fh_debug)

def __init_reddit() -> praw.Reddit:
    """Initializes a reddit instance using the application read only pipeline.

    Returns:
        praw.Reddit: Initialized reddit instance
    """
    return praw.Reddit(client_id = CONFIG["client_id"],
                        client_secret = CONFIG["client_secret"],
                        user_agent = CONFIG["user_agent"])

def get_new_post() -> None or praw.models.Submission:
    """ TODO
    - check for wednesday
    - check local file for post on current day
    - fetch new post

    """
    if __is_date_wednesday(dt.now()):
        return None
    with open("last_posts.json", "r", encoding="utf-8") as f:
        last_posts = json.loads(f.read())
    
    

def __fetch_latest_wednesday_post() -> praw.models.Submission:
    latest_submissions = REDDIT.redditor("SmallLebowsky").submissions.new(limit=20)
    for submission in latest_submissions:
        if __is_date_wednesday(datetime.utcfromtimestamp(submission.created_utc)):
            if "Mittwoch" in submission.title:
                return submission
            else:
                raise PostNotFoundException
        

def __test():
    try:
        post = get_last_wednesday_post()
    except PostNotFoundException:
        # TODO send error message over mail
        pass

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
        tdelta = datetime.timedelta(days = -4 - weekday)
    elif weekday > 3:
        tdelta = datetime.timedelta(days = 3 - weekday)
    else:
        tdelta = datetime.timedelta()
    now = now + tdelta
    now = dt.combine(now.date(), datetime.time())
    return now

if __name__ == "__main__":
    get_new_post()