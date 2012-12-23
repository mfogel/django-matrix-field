from django import forms
from django.db import models
from django.test import TestCase

from . import MatrixField

M1 = [3,4]
M2 = [[3,4],[4,5]]
M3 = [[[3,4,5,6],[12,13,14,15]],[[23,24,25,26],[33,34,35,36]]]
M4 = [[[[2]]]]


class TestModel(models.Model):
    mx = MatrixField()
    mx_null = MatrixField(null=True)
    mx_blank = MatrixField(blank=True)
    mx_blank_null = MatrixField(blank=True, null=True)


class TestModelForm(forms.ModelForm):
    class Meta:
        model = TestModel


class MatrixFieldModelFormTestCase(TestCase):

    def test_valid1(self):
        pass


class TimeZoneFieldDBTestCase(TestCase):

    def test_valid1(self):
        pass
