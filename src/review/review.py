import sys
import os
import re
from datetime import datetime, timedelta
from pytz import timezone

# This is so that below import works.  Sets the pwd to home directory
sys.path.append(os.path.realpath("."))

import src.utils.utils as utils
import src.constants as constants

url_regex = re.compile(constants.URL_REGEX)

class DerivedInsight:
    def __init__(self):
        # The sentiment values
        self.sentiment = {
            "neg": 0.0,
            "neu": 0.0,
            "pos": 0.0,
            "compound": 0.0
        }
        # The category (inferred) of the review
        self.category = "uncategorized" # TODO: Move this to constants
        # Free Flowing dict to store any other information
        self.extra_properties = {}

    def to_dict(self):
        return {
            "sentiment": self.sentiment,
            "category": self.category,
            "extra_properties": self.extra_properties,
        }

class Review:
    def __init__(
        self,
        *review,
        message = "",
        timestamp = "",
        app_name = "",
        channel_name = "",
        channel_type = "",
        rating = None,
        review_timezone="UTC",
        timestamp_format="%Y/%m/%d %H:%M:%S"
    ):
        # The message in the review
        self.message = message
        # The timestamp when the review was submitted
        self.timestamp = timestamp
        # Rating.
        self.rating = rating
        # The app from which the review came
        self.app_name = app_name
        # The source/channel from which the review came
        self.channel_name = channel_name
        # The source/type from which the review came
        self.channel_type = channel_type
        # Every review hash id which is unique to the message and the timestamp
        self.hash_id = utils.calculate_hash(message + timestamp)
        # Derived Insights
        self.derived_insight = DerivedInsight()
        # The raw value of the review itself.
        self.raw_review = review

        # Now that we have all info that we wanted for a review.
        # We do some post processing.
        # Fixing the timezone
        self.timestamp = datetime.strptime(
            timestamp, timestamp_format # Parse it using the given timestamp format
        ).replace(
            tzinfo=timezone(review_timezone) # Replace the timezone with the given timezone
        ).astimezone(
            timezone("UTC") # Convert it to UTC timezone
        )
        # Clean up the message
        # Removes links from message using regex
        self.message = url_regex.sub("", self.message)
        # Removing the non ascii chars
        self.message = (self.message.encode("ascii", "ignore")).decode("utf-8")

    @classmethod
    def from_review_json(cls, review):
        return cls(
            review,
            message=review["message"],
            timestamp=review["timestamp"],
            app_name=review["app_name"],
            channel_name=review["channel_name"],
            channel_type=review["channel_type"],
            rating=review["rating"],
        )

    def to_dict(self):
        return {
            "message": self.message,
            "timestamp": self.timestamp.strftime(
                "%Y/%m/%d %H:%M:%S" # Convert it to a standard datetime format
            ),
            "rating": self.rating,
            "app_name": self.app_name,
            "channel_name": self.channel_name,
            "channel_type": self.channel_type,
            "hash_id": self.hash_id,
            "derived_insight": self.derived_insight.to_dict(),
            "raw_review": self.raw_review,
        }
