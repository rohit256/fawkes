import utils from  src.utils

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

class Review:
    def __init__(self, review):
        # The message in the review
        self.message = review["message"]
        # The timestamp when the review was submitted
        self.timestamp = review["timestamp"]
        # Every review hash id which is unique to the message and the timestamp
        self.hash_id = utils.calculate_hash(self.message + self.timestamp)
        # Derived Insights
        self.derived_insight = DerivedInsight()
        # The raw value of the review itself.
        self.raw_review = review
