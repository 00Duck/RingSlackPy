import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import logging

class SlackBot:
    """Initialize a simple slack bot with a default channel. Example channel name: #my-channel"""
    def __init__(self, c):
        self.channel = c
        self.client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])
        logging.basicConfig(format='%(asctime)s\t%(levelname)s\t%(message)s',
                        datefmt='%Y-%d-%m %H:%M:%S', filename='server.log', level=logging.INFO)
    
    def set_channel(self, c):
        self.channel = c

    def send_message(self, msg, upload_snapshot=False):
        try:
            self.client.chat_postMessage(channel=self.channel, text=msg)
            if upload_snapshot == True:
                self.client.files_upload(
                    channels=self.channel,
                    file="last_screenshot.jpg",
                    title="Door"
                )
        except SlackApiError as e:
            logging.error("SlackBot could not post message. OK: %s, Error: %s", e.response["ok"], e.response["error"])

