# filter.py
import logging

class Filter:
    """
    Class for filtering content based on a score and feedback.
    """

    def __init__(self, threshold, feedback_keywords=None):
        """
        Initializes the filter object.

        Args:
            threshold (int): The score threshold for filtering content.
            feedback_keywords (list): A list of negative keywords that, if present in the feedback, will result in disapproval.
        """
        self.threshold = threshold
        self.feedback_keywords = feedback_keywords if feedback_keywords else []
        logging.info(f"Filter initialized with threshold: {self.threshold}, negative keywords: {self.feedback_keywords}")

    def set_threshold(self, threshold):
      """
      Sets a new score threshold
      """
      self.threshold = threshold
      logging.info(f"Filter threshold updated to: {self.threshold}")

    def add_negative_keywords(self, keywords):
        """
        Adds negative keywords to the filter criteria
        """
        self.feedback_keywords.extend(keywords)
        logging.info(f"Filter negative keywords updated. Current keywords: {self.feedback_keywords}")
    
    def clear_negative_keywords(self):
        """
        Removes the negative keywords
        """
        self.feedback_keywords = []
        logging.info(f"Filter negative keywords cleared.")

    def is_approved(self, score, feedback):
        """
        Checks if content is approved based on the given score and feedback.

        Args:
            score (int): The score of the content.
            feedback (str): The feedback provided by the reviewer.

        Returns:
            bool: True if the score meets or exceeds the threshold and no negative keywords are found in the feedback, False otherwise.
        """
        if not isinstance(score, int):
            logging.error(f"Invalid score type: {type(score)}. Score must be an int.")
            return False

        if score < 0:
             logging.error("Score must be a positive number.")
             return False

        if score >= self.threshold:
            if self.feedback_keywords:
              for keyword in self.feedback_keywords:
                if keyword.lower() in feedback.lower():
                    logging.info(f"Book disapproved due to negative keyword '{keyword}' in feedback.")
                    return False
              logging.info(f"Book approved with score: {score} and feedback: {feedback}")
              return True
            else:
               logging.info(f"Book approved with score: {score}")
               return True

        logging.info(f"Book not approved with score: {score} and feedback: {feedback}")
        return False