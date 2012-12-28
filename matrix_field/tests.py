import json

from django import forms
from django.core.exceptions import ValidationError
from django.db import models
from django.test import TestCase

from . import MatrixField, MatrixFormField


M1 = [[3, 4], [4, 5], [6, 7]]
M2 = [[[2.0]]]
M3a = ['a', 'b']
M3b = ['c', 'd']

M1_str = json.dumps(M1)
M2_str = json.dumps(M2)
M3a_str = json.dumps(M3a)
M3b_str = json.dumps(M3b)


class TestModel(models.Model):
    f1 = MatrixField(datatype='int', dimensions=(3, 2))
    f2 = MatrixField(datatype='float', dimensions=(1, 1, 1), blank=True)
    f3 = MatrixField(datatype='str', dimensions=(2,), blank=True,
                     default=M3a_str)


class TestForm(forms.Form):
    f1 = MatrixFormField(datatype='int', dimensions=(3, 2))
    f2 = MatrixFormField(datatype='float', dimensions=(1, 1, 1),
                         required=False)


class TestModelForm(forms.ModelForm):
    class Meta:
        model = TestModel


class MatrixFormFieldTestCase(TestCase):

    def test_valid_specify_all(self):
        form = TestForm({'f1': M1_str, 'f2': M2_str})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['f1'], M1)
        self.assertEqual(form.cleaned_data['f2'], M2)

    def test_valid_with_defaults(self):
        form = TestForm({'f1': M1_str})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['f1'], M1)
        self.assertEqual(form.cleaned_data['f2'], None)

    def test_invalid_blank(self):
        form = TestForm({})
        self.assertFalse(form.is_valid())
        self.assertTrue(any('required' in e for e in form.errors['f1']))

    def test_invalid_datatype(self):
        value = [[1.0, 1.0], [1.0, 1.0], [1.0, 1.0]]
        form = TestForm({'f1': json.dumps(value)})
        self.assertFalse(form.is_valid())
        self.assertTrue(any('datatype' in e for e in form.errors['f1']))

    def test_invalid_dimesion(self):
        form = TestForm({'f1': json.dumps([1])})
        self.assertFalse(form.is_valid())
        self.assertTrue(any('dimension' in e for e in form.errors['f1']))


class MatrixFieldModelFormTestCase(TestCase):

    def test_valid_specify_all(self):
        form = TestModelForm({'f1': M1_str, 'f2': M2_str, 'f3': M3b_str})
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(TestModel.objects.count(), 1)

        m = TestModel.objects.get()
        self.assertEqual(m.f1, M1)
        self.assertEqual(m.f2, M2)
        self.assertEqual(m.f3, M3b)

    def test_valid_with_defaults(self):
        # seems there should be a better way to get a form's default values...?
        # http://stackoverflow.com/questions/7399490/
        data = dict(
            (field_name, field.initial)
            for field_name, field in TestModelForm().fields.iteritems()
        )
        data.update({'f1': M1})
        form = TestModelForm(data=data)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(TestModel.objects.count(), 1)

        m = TestModel.objects.get()
        self.assertEqual(m.f2, None)
        self.assertEqual(m.f3, M3a)

    def test_invalid_required(self):
        form = TestModelForm({})
        self.assertFalse(form.is_valid())
        self.assertTrue(any('required' in e for e in form.errors['f1']))

    def test_invalid_datatype(self):
        value = [[1.0, 1.0], [1.0, 1.0], [1.0, 1.0]]
        form = TestModelForm({'f1': json.dumps(value)})
        self.assertFalse(form.is_valid())
        self.assertTrue(any('datatype' in e for e in form.errors['f1']))

    def test_invalid_dims1(self):
        form = TestModelForm({'f1': M1_str, 'f2': json.dumps([[1]])})
        self.assertFalse(form.is_valid())
        self.assertTrue(any('dimension' in e for e in form.errors['f2']))

    def test_invalid_dims2(self):
        value = ['a', 'b', 'c']
        form = TestModelForm({'f1': M1_str, 'f3': json.dumps(value)})
        self.assertFalse(form.is_valid())
        self.assertTrue(any('dimension' in e for e in form.errors['f3']))


class MatrixFieldTestCase(TestCase):

    def test_valid(self):
        m = TestModel.objects.create(f1=M1, f2=M2, f3=M3b)
        m = TestModel.objects.get(pk=m.pk)
        self.assertEqual(m.f1, M1)
        self.assertEqual(m.f2, M2)
        self.assertEqual(m.f3, M3b)

    def test_valid_blank(self):
        m = TestModel.objects.create(f1=M1)
        m = TestModel.objects.get(pk=m.pk)
        self.assertEqual(m.f2, None)
        self.assertEqual(m.f3, M3a)

    def test_invalid_type(self):
        with self.assertRaises(ValidationError):
            TestModel(f1=M1, f3=[2.0, 3.0]).full_clean()
        with self.assertRaises(ValidationError):
            TestModel(f1=M1, f2=[[[2]]]).full_clean()

    def test_invalid_dims(self):
        with self.assertRaises(ValidationError):
            TestModel(f1=M1, f2=['a']).full_clean()
        with self.assertRaises(ValidationError):
            TestModel(f1=M1, f3=[['a'], ['b']]).full_clean()

    def test_invalid_altogether(self):
        with self.assertRaises(ValidationError):
            TestModel(f1={'a': 2}).full_clean()
        with self.assertRaises(ValidationError):
            TestModel(f1=4).full_clean()
        with self.assertRaises(ValidationError):
            TestModel(f1='blah blah').full_clean()
