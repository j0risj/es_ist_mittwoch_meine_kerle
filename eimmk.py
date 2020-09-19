import praw
import configparser
import logging
import datetime
import typing
import json
import smtplib
from datetime import datetime as dt

class PostNotFoundException(Exception):
    pass

class Eimmk:
    def __init__(self):
        self.config = load_config()
        self.reddit = self.init_reddit()


    def init_reddit(self) -> praw.Reddit:
        return praw.Reddit(client_id = self.config["client_id"],
                           client_secret = self.config["client_secret"],
                           user_agent = self.config["user_agent"])


    def get_latest_wednesday_post(self) -> praw.models.Submission:
        latest_submissions = self.reddit.redditor("SmallLebowsky").submissions.new(limit=20)
        for submission in latest_submissions:
            if is_date_wednesday(datetime.utcfromtimestamp(submission.created_utc)):
                if "Mittwoch" in submission.title:
                    return submission
                else:
                    raise PostNotFoundException
        

    def test(self):
        try:
            post = self.get_last_wednesday_post()
        except PostNotFoundException:
            # TODO send error message over mail
            pass



def is_date_wednesday(date: dt) -> bool:
    return (date.isoweekday() == 3)


def get_last_wednesday_date(now: dt = None) -> datetime.date:
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
    


    



def load_config():
    config = configparser.ConfigParser()
    config.read("config.ini")
    config = config["DEFAULT"]
    return config



if __name__ == "__main__":
    Eimmk().test()