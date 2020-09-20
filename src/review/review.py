import src.utils as utils
import src.constants as constants

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
    def __init__(self, *review, message = '', timestamp = '', app_name = '', channel_name = '', channel_type = ''):
        # The message in the review
        self.message = message
        # The timestamp when the review was submitted
        self.timestamp = timestamp
        # The app from which the review came
        self.app_name = app_name
        # The source/channel from which the review came
        self.channel_name = channel_name
        # The source/type from which the review came
        self.channel_type = channel_type
        # Every review hash id which is unique to the message and the timestamp
        self.hash_id = utils.calculate_hash(self.message + self.timestamp)
        # Derived Insights
        self.derived_insight = DerivedInsight()
        # The raw value of the review itself.
        self.raw_review = review

    def standardise_date_time(self, review_timezone, review_timestamp_format):
        self.timestamp = datetime.strptime(
            self.timestamp, review_timestamp_format # Parse it using the given timestamp format
        ).replace(
            tzinfo=timezone(review_timezone) # Replace the timezone with the given timezone
        ).astimezone(
            timezone('UTC') # Convert it to UTC timezone
        ).strftime(
            "%Y/%m/%d %H:%M:%S" # Convert it to a standard datetime format
        )

    def clean_review_message(self):
        # Removes links from message using regex
        regex = re.compile(constants.URL_REGEX)
        self.message = regex.sub("", self.message)

        # Removing the non ascii chars
        self.message = (self.message.encode("ascii", "ignore")).decode("utf-8")

    def to_dict(self):
        return {
            "message": self.message,
            "timestamp": self.timestamp,
            "app_name": self.app_name,
            "channel_name": self.channel_name,
            "channel_type": self.channel_type,
            "hash_id": self.hash_id,
            "derived_insight": self.derived_insight.to_dict(),
            "raw_review": self.raw_review,
        }
