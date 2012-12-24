import json

from django.core.exceptions import ValidationError
from django.db import models

from .forms import MatrixField as MatrixFormField
from .validators import DataTypeValidator, DimensionsValidator


class MatrixField(models.Field):
    """
    Provides database store for matrices.
    """

    description = "A matrix"
    __metaclass__ = models.SubfieldBase

    MAX_LENGTH = 65535

    def __init__(self, datatype=None, dimensions=None, **kwargs):
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
    # TODO: how to handle dimensions, datatype?
    add_introspection_rules(
        rules=[(
            (MatrixField, ),    # Class(es) these apply to
            [],                 # Positional arguments (not used)
            {                   # Keyword argument
                'max_length': [
                    'max_length', { 'default': MatrixField.MAX_LENGTH }
                ],
            },
        )],
        patterns=['matrix_field\.fields\.']
    )
