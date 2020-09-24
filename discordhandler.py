import requests
import logging


class DiscordHandler(logging.Handler):
    def __init__(self, username: str, webhook_url: str, 
                 avatar_url: str = None) -> None:
        logging.Handler.__init__(self)
        self.json_data = {
            "username": username}
        self.webhook_url = webhook_url
        if avatar_url is not None:
            self.json_data["avatar_url"] = avatar_url


    def emit(self, record):
        msg = self.format(record)
        self.json_data["content"] = f"```\n{msg}\n```"
        response = requests.post(self.webhook_url, json=self.json_data)
        response.raise_for_status()
        
if __name__ == "__main__":
    logger = logging.getLogger("Logging Test")
    webhook_url = input("Discord webhook url: \n")
    dh = DiscordHandler(logger.name, webhook_url)
    formatter = logging.Formatter(
    "[%(asctime)s][%(name)s][%(levelname)s]: %(message)s",
    "%Y-%m-%d %H:%M:%S")
    dh.setFormatter(formatter)
    logger.addHandler(dh)
    logger.error("This is a test log to discord")
