# tests/test_filter.py
import pytest
from filter import Filter
import logging

# Setup logging to capture log output
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_filter_approval():
    filter = Filter(threshold=7)
    assert filter.is_approved(score=8, feedback="This is a great book") == True
    assert filter.is_approved(score=7, feedback="This book needs some work") == True
    assert filter.is_approved(score=6, feedback="This book is not good") == False

def test_filter_rejection_with_keywords():
    filter = Filter(threshold=5, feedback_keywords=["bad", "poor"])
    assert filter.is_approved(score=8, feedback="This is a poor book") == False
    assert filter.is_approved(score=4, feedback="This book is bad") == False
    assert filter.is_approved(score=6, feedback="This is a good book") == True

def test_filter_negative_score():
    filter = Filter(threshold=5)
    assert filter.is_approved(score=-1, feedback="This is a bad book") == False

def test_filter_invalid_score_type():
    filter = Filter(threshold=5)
    assert filter.is_approved(score="invalid", feedback="This book is bad") == False

def test_filter_set_threshold():
    filter = Filter(threshold=5)
    assert filter.threshold == 5
    filter.set_threshold(8)
    assert filter.threshold == 8
    assert filter.is_approved(score=7, feedback="Good") == False
    assert filter.is_approved(score=9, feedback="Good") == True

def test_add_negative_keywords():
    filter = Filter(threshold=5)
    assert not filter.feedback_keywords
    filter.add_negative_keywords(["bad", "poor"])
    assert filter.feedback_keywords == ["bad", "poor"]
    assert filter.is_approved(score=8, feedback="This is a poor book") == False

def test_clear_negative_keywords():
    filter = Filter(threshold=5, feedback_keywords=["bad","poor"])
    assert filter.feedback_keywords
    filter.clear_negative_keywords()
    assert not filter.feedback_keywords
    assert filter.is_approved(score=8, feedback="This is a poor book") == True