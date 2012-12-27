from django import forms
from django.core.exceptions import ValidationError
from django.db import models
from django.test import TestCase

from . import MatrixField


M1 = ['a', 'b']
M2 = [[3, 4], [4, 5]]
M3 = [[[1.3, 1.4, 1.5], [1.2, 1.3, 1.4]], [[2.3, 2.4, 2.5], [3.3, 3.4, 3.5]]]
M4 = [[[2.0]]]


class TestModel(models.Model):
    str_2 = MatrixField(datatype=str, dimensions=(2,))
    int_2x2 = MatrixField(datatype=int, dimensions=(2, 2), blank=True)
    float_2x2x3 = MatrixField(datatype=float, dimensions=(2, 2, 3), blank=True)
    float_1x1x1 = MatrixField(datatype=float, dimensions=(1, 1, 1), blank=True)


class TestModelForm(forms.ModelForm):
    class Meta:
        model = TestModel


class MatrixFieldModelFormTestCase(TestCase):

    def test_valid(self):
        form = TestModelForm({
            'str_2': M1,
            'int_2x2': M2,
            'float_2x2x3': M3,
            'float_1x1x1': M4,
        })
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(TestModel.objects.count(), 1)

    def test_invalid_type(self):
        form = TestModelForm({
            'str_2': [3.0, 4.0],
        })
        self.assertFalse(form.is_valid())

    def test_invalid_dims1(self):
        form = TestModelForm({
            'float_1x1x1': [[1]],
        })
        self.assertFalse(form.is_valid())

    def test_invalid_dims2(self):
        form = TestModelForm({
            'str_2': ['a', 'b', 'c'],
        })
        self.assertFalse(form.is_valid())


class MatrixFieldDBTestCase(TestCase):

    def test_valid(self):
        m = TestModel.objects.create(
            str_2=M1,
            int_2x2=M2,
            float_2x2x3=M3,
            float_1x1x1=M4,
        )
        m = TestModel.objects.get(pk=m.pk)
        self.assertEqual(m.str_2, M1)
        self.assertEqual(m.int_2x2, M2)
        self.assertEqual(m.float_2x2x3, M3)
        self.assertEqual(m.float_1x1x1, M4)

    def test_valid_blank(self):
        m = TestModel.objects.create(str_2=M1)
        m = TestModel.objects.get(pk=m.pk)
        self.assertEqual(m.int_2x2, None)
        self.assertEqual(m.float_2x2x3, None)

    def test_invalid_type(self):
        with self.assertRaises(ValidationError):
            TestModel(str_2=[2.0, 3.0]).full_clean()
        with self.assertRaises(ValidationError):
            TestModel(float_1x1x1=[[[[2]]]]).full_clean()

    def test_invalid_dims(self):
        #with self.assertRaises(ValidationError):
        #    TestModel(str_2=['a']).full_clean()
        with self.assertRaises(ValidationError):
            TestModel(str_2=[['a'], ['b']]).full_clean()
        #with self.assertRaises(ValidationError):
        #    TestModel(float_1x1x1=[[2.0]]).full_clean()

    def test_invalid_altogether(self):
        with self.assertRaises(ValidationError):
            TestModel(str_2={'a': 2}).full_clean()
        with self.assertRaises(ValidationError):
            TestModel(str_2=4).full_clean()
        with self.assertRaises(ValidationError):
            TestModel(str_2='nil nil').full_clean()
