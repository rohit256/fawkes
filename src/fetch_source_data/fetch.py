import json
import sys
import os
import importlib

from shutil import copyfile
from fetch_app_store_reviews import *
from fetch_app_reviews import *
from fetch_salesforce_review import *
from fetch_spreadsheet_review import *
from fetch_twitter_data import *

#  This is so that the following imports work
sys.path.append(os.path.realpath("."))

from src.utils import *
from src.config import *

from src.app_config.app_config import AppConfig, ReviewChannelTypes

def fetch_csv(review_channel, app_name):
    fetch_file_save_path = FETCH_FILE_SAVE_PATH.format(
        dir_name=DATA_DUMP_DIR,
        app_name=app_name,
        channel_name=review_channel.channel_name,
        extension="csv")
    copyfile(review_channel[FILE_PATH], fetch_file_save_path)


def fetch_reviews():
    app_configs = open_json(
        APP_CONFIG_FILE.format(file_name=APP_CONFIG_FILE_NAME))

    for app in app_configs:
        app_config = AppConfig(
            open_json(
                APP_CONFIG_FILE.format(file_name=app)
            )
        )

        for review_channel in app_config.review_channels:
            if review_channel.is_channel_enabled and review_channel.channel_type != ReviewChannelTypes.BLANK:
                if review_channel.channel_type == ReviewChannelTypes.TWITTER:
                    fetch_from_twitter(
                        review_channel, app_config.app.name
                    )
                elif review_channel.channel_type == ReviewChannelTypes.SALESFORCE:
                    fetch_from_salesforce(
                        review_channel, app_config.app.name
                    )
                elif review_channel.channel_type == ReviewChannelTypes.SPREADSHEET:
                    fetch_review_from_spreadsheet(
                        review_channel, app_config.app.name
                    )
                elif review_channel.channel_type == ReviewChannelTypes.CSV:
                    fetch_csv(
                        review_channel, app_config.app.name
                    )
                elif review_channel.channel_type == ReviewChannelTypes.ANDROID:
                    fetch_app_reviews(
                        review_channel, app_config.app.name
                    )
                elif review_channel.channel_type == ReviewChannelTypes.IOS:
                    fetch_app_store_reviews(
                        review_channel, app_config.app.name
                    )
                else:
                    continue

        # Executing custom code after parsing.
        if app_config.custom_code_file != None:
            custom_code_module = importlib.import_module(
                APP + "." + app_config[CUSTOM_CODE_PATH], package=None)
            reviews = custom_code_module.run_custom_code_post_fetch()


if __name__ == "__main__":
    fetch_reviews()
