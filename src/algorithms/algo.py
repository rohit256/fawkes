import sys
import os
import importlib
import tensorflow as tf
import pathlib

from datetime import timezone
from pprint import pprint
from multiprocessing import Pool
from functools import partial
from datetime import datetime, timedelta

#  This is so that the following imports work
sys.path.append(os.path.realpath("."))

import src.utils.utils as utils
import src.utils.filter_utils as filter_utils
import src.constants as constants

from src.app_config.app_config import AppConfig, ReviewChannelTypes
from src.review.review import Review

from src.algorithms.text_match.text_match import *
from src.algorithms.sentiment import *
# import src.algorithms.lstm_classifier.lstm_classifier as lstm_classifier
# from src.algorithms.slackbot import *


def add_review_sentiment_score(review):
    # Add the sentiment to the review's derived insight and return the review
    review.derived_insight.sentiment = get_sentiment(review.message)
    # Return the review
    return review

def text_match_categortization(review, app_config, topics):
    # Find the category of the review
    category_scores, category = text_match(review.message, topics)
    # Add the category to the review's derived insight and return the review
    review.derived_insight.category = category
    # Return the review
    return review


# def lstm_classification(reviews, app_config, model, article_tokenizer,
#                         label_tokenizer, original_label_to_clean_label):
#     articles = [review.message for review in reviews]
#     categories = lstm_classifier.predict_labels(articles, app_config, model,
#                                                 article_tokenizer,
#                                                 label_tokenizer)

#     return [
#         format_output_json(
#             review, None, None,
#             {LSTM_CATEGORY: original_label_to_clean_label[categories[index]]})
#         for index, review in enumerate(reviews)
#     ]


def bug_feature_classification(review, topics):
    _, category = text_match(review.message, topics)
    # Add the bug-feature classification to the review's derived insight and return the review
    review.derived_insight.extra_properties[constants.BUG_FEATURE] = category
    # Return the review
    return review

def run_algo():
    app_configs = utils.open_json(
        constants.APP_CONFIG_FILE.format(file_name=constants.APP_CONFIG_FILE_NAME)
    )
    for app_config_file in app_configs:
        app_config = AppConfig(
            utils.open_json(
                app_config_file
            )
        )
        # Path where the user reviews were stored after parsing.
        parsed_user_reviews_file_path = constants.PARSED_USER_REVIEWS_FILE_PATH.format(
            base_folder=app_config.fawkes_internal_config.data.base_folder,
            dir_name=app_config.fawkes_internal_config.data.parsed_data_folder,
            app_name=app_config.app.name,
            extension=constants.JSON,
        )

        # Loading the reviews
        reviews = utils.open_json(parsed_user_reviews_file_path)

        # Converting the json object to Review object
        reviews = [Review.from_review_json(review) for review in reviews]

        # Filtering out reviews which are not applicable.
        reviews = filter_utils.filter_reviews_by_time(
            filter_utils.filter_reviews_by_channel(
                reviews, filter_utils.filter_disabled_review_channels(
                    app_config
                ),
            ),
            datetime.now(timezone.utc) - timedelta(days=app_config.algorithm_config.algorithm_days_filter)
        )

        # Number of process to make
        num_processes = min(constants.PROCESS_NUMBER, os.cpu_count())

        if constants.CIRCLECI in os.environ:
            num_processes = 2

        # Adding sentiment
        with Pool(num_processes) as process:
            reviews = process.map(add_review_sentiment_score, reviews)

        if app_config.algorithm_config.categorization_algorithm != None and app_config.algorithm_config.category_keywords_weights_file != None:
            # We read from the topic file first
            topics = {}
            topics = utils.open_json(app_config.algorithm_config.category_keywords_weights_file)

            # Adding text-match categorization
            with Pool(num_processes) as process:
                reviews = process.map(
                    partial(
                        text_match_categortization,
                        app_config=app_config,
                        topics=topics
                    ),
                    reviews
                )

        if app_config.algorithm_config.bug_feature_keywords_weights_file != None:
            # We read from the topic file first
            topics = {}
            topics = utils.open_json(app_config.algorithm_config.bug_feature_keywords_weights_file)

            # Adding bug/feature classification
            with Pool(num_processes) as process:
                reviews = process.map(
                    partial(
                        bug_feature_classification,
                        topics=topics
                    ),
                    reviews
                )

        # if CATEGORIZATION_ALGORITHM in app_config and app_config[
        #         CATEGORIZATION_ALGORITHM] == LSTM_CLASSIFIER:
        #     print("[LOG] Loading LSTM Model :: ")

        #     model = tf.keras.models.load_model(
        #         LSTM_TRAINED_MODEL_FILE.format(app_name=app_config.app.name))

        #     print("[LOG] Start Load of Token Files :: ")

        #     tokenizer_json = open_json(
        #         LSTM_ARTICLE_TOKENIZER_FILE.format(app_name=app_config.app.name))
        #     article_tokenizer = tf.keras.preprocessing.text.tokenizer_from_json(
        #         tokenizer_json)

        #     tokenizer_json = open_json(
        #         LSTM_LABEL_TOKENIZER_FILE.format(app_name=app_config.app.name))
        #     label_tokenizer = tf.keras.preprocessing.text.tokenizer_from_json(
        #         tokenizer_json)

        #     print("[LOG] End Load of Token Files :: ")

        #     print("[LOG] Starting LSTM Categorization :: ")

        #     original_label_to_clean_label = {}
        #     for review in reviews:
        #         label = review.derived_insight.category
        #         cleaned_label = re.sub(r'\W+', '', label)
        #         cleaned_label = cleaned_label.lower()
        #         # Convert this to lower case as the tokenized label is lower
        #         # case
        #         original_label_to_clean_label[cleaned_label] = label

        #     # Adding LSTM categorization
        #     reviews = lstm_classification(reviews, app_config, model,
        #                                   article_tokenizer, label_tokenizer,
        #                                   original_label_to_clean_label)

        #     lstm_text_match_parity = 0

        #     for review in reviews:
        #         if review.derived_insight.category != review[
        #                 DERIVED_INSIGHTS][EXTRA_PROPERTIES][LSTM_CATEGORY]:
        #             lstm_text_match_parity += 1

        #     print("[LOG] Number of reviews classified differently : ",
        #           lstm_text_match_parity)
        #     print("[LOG] Total Reviews : ", len(reviews))

        #     if len(reviews) != 0:
        #         print("[LOG] % inaccuracy : ",
        #               (100.0 * lstm_text_match_parity) / len(reviews))

        #     print("[LOG] Ending LSTM Categorization :: ")

        # Create the intermediate folders
        processed_user_reviews_file_path = constants.PROCESSED_USER_REVIEWS_FILE_PATH.format(
            base_folder=app_config.fawkes_internal_config.data.base_folder,
            dir_name=app_config.fawkes_internal_config.data.processed_data_folder,
            app_name=app_config.app.name,
            extension=constants.JSON,
        )
        dir_name = os.path.dirname(processed_user_reviews_file_path)
        pathlib.Path(dir_name).mkdir(parents=True, exist_ok=True)

        utils.dump_json(
            [review.to_dict() for review in reviews],
            processed_user_reviews_file_path,
        )


if __name__ == "__main__":
    run_algo()
