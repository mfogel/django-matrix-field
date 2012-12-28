from django.core.exceptions import ValidationError


class DataTypeValidator(object):
    "Validate that each element of a matrix is of the correct type"

    def __init__(self, datatype):
        super(DataTypeValidator, self).__init__()
        # str and unicode are mapped to 'database store for strings'
        self.datatype = (
            basestring if issubclass(datatype, basestring)
            else datatype
        )

    def __call__(self, value):
        if isinstance(value, (list, tuple)):
            for elem in value:
                self(elem)
        else:
            if not isinstance(value, self.datatype):
                raise ValidationError("Invalid datatype")


class DimensionsValidator(object):
    "Validate the matrix has correct dimensions"

    def __init__(self, dimensions):
        super(DimensionsValidator, self).__init__()
        self.dimensions = dimensions

    def __call__(self, value, index=0):
        if index == len(self.dimensions):
            if isinstance(value, (list, tuple)):
                raise ValidationError("Excessive depth of dimensions")
            return
        if not isinstance(value, (list, tuple)):
            raise ValidationError("Insufficient depth of dimensions")
        if not len(value) == self.dimensions[index]:
            raise ValidationError("Invalid dimension")
        for elem in value:
            self(elem, index+1)
