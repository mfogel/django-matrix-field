import json

from django.db import models


class MatrixField(models.Field):
    """
    Provides database store for matrices.
    """

    description = "A matrix"
    __metaclass__ = models.SubfieldBase

    MAX_LENGTH = 65535

    def __init__(self, **kwargs):
        defaults = {
            'max_length': self.MAX_LENGTH,
        }
        defaults.update(kwargs)
        super(MatrixField, self).__init__(**defaults)

    def get_internal_type(self):
        # TODO: take advantage of postgres matrix type
        return 'CharField'

    def to_python(self, value):
        "Convert to python matrix (arrays of arrays)"
        return json.loads(value)

    def get_prep_value(self, value):
        "Convert to string"
        return json.dumps(value)


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
                    'max_length', { 'default': MatrixField.MAX_LENGTH }
                ],
            },
        )],
        patterns=['matrix_field\.fields\.']
    )
