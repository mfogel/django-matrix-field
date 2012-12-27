from django import forms
from .validators import DataTypeValidator, DimensionsValidator


class MatrixField(forms.Field):

    def __init__(self, datatype=None, dimensions=None, **kwargs):
        super(MatrixField, self).__init__(**kwargs)
        self.validators.append(DataTypeValidator(datatype=datatype))
        self.validators.append(DimensionsValidator(dimensions=dimensions))
