import json

from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.db import models
from django.db.models.fields import NOT_PROVIDED

from .forms import MatrixFormField
from .validators import DataTypeValidator, DimensionsValidator


class MatrixField(models.Field):
    """
    Provides database store for matrices.
    """

    description = "A matrix"
    __metaclass__ = models.SubfieldBase

    MAX_LENGTH = 255

    def __init__(self, datatype=None, dimensions=None, **kwargs):
        if not datatype or not dimensions:
            raise ImproperlyConfigured("Required kwarg 'datatype' or "
                                       "'dimensions' missing")
        self.datatype, self.dimensions = datatype, dimensions
        defaults = {
            'max_length': self.MAX_LENGTH,
            'default': None,
        }
        defaults.update(kwargs)
        super(MatrixField, self).__init__(**defaults)
        self.validators.append(DataTypeValidator(self.datatype))
        self.validators.append(DimensionsValidator(self.dimensions))

    def get_internal_type(self):
        # TODO: take advantage of postgres matrix type
        #       kinda the whole reason this django app even exists...
        return 'CharField'

    def to_python(self, value):
        "Convert to python matrix (arrays of arrays)"
        if isinstance(value, (list, tuple)) or value is None:
            return value
        try:
            return json.loads(value)
        except:
            raise ValidationError("Unable to convert value to matrix")

    def get_prep_value(self, value):
        "Convert to string"
        return json.dumps(value)

    def formfield(self, **kwargs):
        defaults = {
            'datatype': self.datatype,
            'dimensions': self.dimensions,
            'form_class': MatrixFormField,
        }
        defaults.update(kwargs)
        return super(MatrixField, self).formfield(**defaults)


# South support
try:
    from south.modelsinspector import add_introspection_rules
except ImportError:
    pass
else:
    add_introspection_rules(
        rules=[(
            (MatrixField, ),    # Class(es) these apply to
            [],                 # Positional arguments (not used)
            {                   # Keyword argument
                'max_length': [
                    'max_length', {'default': MatrixField.MAX_LENGTH}
                ],
                'datatype': ['datatype', {'default': NOT_PROVIDED}],
                'dimensions': ['dimensions', {'default': NOT_PROVIDED}],
            },
        )],
        patterns=['matrix_field\.fields\.']
    )
