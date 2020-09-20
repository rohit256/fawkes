from shutil import copyfile
from src.config import *

def fetch_csv(review_channel, app_name):
    fetch_file_save_path = RAW_USER_REVIEWS_FILE_PATH.format(
        dir_name=DATA_DUMP_DIR,
        app_name=app_name,
        channel_name=review_channel.channel_name,
        extension="csv")

    copyfile(review_channel.file_path, fetch_file_save_path)
