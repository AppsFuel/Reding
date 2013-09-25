from datetime import datetime
from flask.ext.restful.fields import DateTime


class DateTimestamp(DateTime):
    def format(self, value):
        return super(DateTimestamp, self).format(datetime.fromtimestamp(value))
