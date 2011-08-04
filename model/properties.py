import model.properties
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext import db
from google.appengine.api import datastore_errors
from google.appengine.ext.webapp import template


class GenderProperty(db.Property):
    data_type = bool
    values = ['femenino', 'masculino']

    def validate(self, value):
        value = super(GenderProperty, self).validate(value)
        if value is not None and value not in self.values:
            raise datastore_errors.BadValueError(
                "Property %s must be '%s' or '%s'" % (self.name,
                    self.values[0], self.values[1]))
        return value

    def get_value_for_datastore(self, model_instance):
        value = self.__get__(model_instance, model_instance.__class__)
        if value is not None:
            return bool(self.values.index(value))

    def make_value_from_datastore(self, value):
        if value is not None:
            return self.values[int(value)]

    def empty(self, value):
        return value is None

