import model.properties
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext import db
from google.appengine.api import datastore_errors
from google.appengine.ext.webapp import template
import re

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




class SlugProperty(db.StringProperty):

    """A (rough) App Engine equivalent to Django's SlugField."""

    re_strip = re.compile(r'[^\w\s-]')
    re_dashify = re.compile(r'[-\s]+')

    def __init__(self, auto_calculate, **kwargs):
        """Initialize a slug with the property to base it on.
        
        The property passed in for auto_calculate should be the property object
        itself from the model::

          class Spam(BaseModel):
            name = db.StringProperty()
            slug = SlugProperty(name)

        """
        super(SlugProperty, self).__init__(**kwargs)
        self.auto_calculate = auto_calculate

    @classmethod
    def slugify(yo_mama, value):
        cleanup = yo_mama.re_strip.sub('', value).strip().lower()
        return yo_mama.re_dashify.sub('-', cleanup)

    def default_value(self):
        """Cannot calculate a default value because of a lack of details for
        use with the descriptor."""
        return super(SlugProperty, self).default_value()

    def get_value_for_datastore(self, model_instance):
        """Convert slug into format to go into the datastore."""
        value = self.auto_calculate.__get__(model_instance, None)
        return self.slugify(value)

    def validate(self, value):
        """Validate the slug meets formatting restrictions."""
        # Django does [^\w\s-] to '', strips, lowers, then [-\s] to '-'.
        if value and (value.lower() != value or ' ' in value):
            raise db.BadValueError("%r must be lowercase and have no spaces" %
                                    value)
        return super(SlugProperty, self).validate(value)
        