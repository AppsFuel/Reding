from unittest import TestCase
from reding.fields import DateTimestamp


class DateTimestampTestCase(TestCase):
    def test_format(self):
        self.assertEqual(DateTimestamp().format(1379402591), 'Tue, 17 Sep 2013 09:23:11 -0000')
