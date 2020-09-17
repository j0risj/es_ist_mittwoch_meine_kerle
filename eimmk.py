import praw
import configparser
import logging
import datetime
from datetime import datetime as dt

class Eimmk:
    def __init__(self):
        self.config = load_config()
        self.reddit = self.init_reddit()

    def init_reddit(self):
        return praw.Reddit(client_id = self.config["client_id"],
                           client_secret = self.config["client_secret"],
                           user_agent = self.config["user_agent"])

    def get_latest_wednesday_posts(self):
        latest_submissions = self.reddit.redditor("SmallLebowsky").submissions.new(limit=20)
        for submission in latest_submissions:
            if is_date_wednesday(datetime.utcfromtimestamp(submission.created_utc)) and "Mittwoch" in submission.title:
                latest_submission = submission
        return latest_submission

    def test(self):
        print(is_date_wednesday(dt.now()))
        print(is_date_wednesday(dt.now() - datetime.timedelta(days=1)))
        print(get_last_wednesday_date())


def is_date_wednesday(date: dt) -> bool:
    return (date.isoweekday() == 3)

def get_last_wednesday_date() -> datetime.date:
    now = dt.utcnow()
    now = now - datetime.timedelta(days = 5)
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