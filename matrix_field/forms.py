import json
from django import forms
from .validators import DataTypeValidator, DimensionsValidator


class MatrixFormField(forms.Field):

    def __init__(self, datatype=None, dimensions=None, **kwargs):
        super(MatrixFormField, self).__init__(**kwargs)
        self.validators.append(DataTypeValidator(datatype=datatype))
        self.validators.append(DimensionsValidator(dimensions=dimensions))

    def to_python(self, value):
        if value is None or isinstance(value, (list, tuple)):
            return value
        return json.loads(value)
