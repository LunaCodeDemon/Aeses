"""
    Test module for sqldata.py
    Remember to remove to make sure that the database gets deleted afterwards.
"""
from datetime import datetime
import numpy
from scripts import sqldata


def test_reminder():
    """
        Test reminder database functions
    """
    reminder = sqldata.Reminder("Hello", 12, 53, 22, True,
                                numpy.datetime64(datetime.now()),
                                numpy.datetime64(datetime.now()))
    sqldata.create_table_reminder()
    sqldata.cleanup_reminders(datetime.now())
    sqldata.insert_reminder(reminder)
    assert sqldata.restore_reminders()[0] == reminder
