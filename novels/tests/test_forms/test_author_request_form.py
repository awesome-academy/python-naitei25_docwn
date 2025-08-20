"""
Unit tests for AuthorRequestForm
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from datetime import date, timedelta

from novels.forms import AuthorRequestForm
from novels.models import AuthorRequest
from constants import Gender, UserRole


User = get_user_model()


class AuthorRequestFormTestCase(TestCase):
    """Base test case for AuthorRequestForm tests"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123',
            role=UserRole.USER.value
        )


class AuthorRequestFormValidationTests(AuthorRequestFormTestCase):
    """Test AuthorRequestForm validation"""
    
    def test_valid_form_minimal(self):
        """Test form with minimal valid data"""
        form_data = {
            'name': 'Test Author',
        }
        form = AuthorRequestForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_valid_form_full(self):
        """Test form with all valid data"""
        form_data = {
            'name': 'Test Author',
            'pen_name': 'Test Pen Name',
            'description': 'Test description',
            'birthday': '1980-01-01',
            'deathday': '2020-12-31',
            'gender': Gender.MALE.value,
            'country': 'Vietnam',
        }
        form = AuthorRequestForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_empty_name_invalid(self):
        """Test form with empty name is invalid"""
        form_data = {
            'name': '',
        }
        form = AuthorRequestForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
    
    def test_name_too_short_invalid(self):
        """Test form with name too short is invalid"""
        form_data = {
            'name': 'A',  # Only 1 character
        }
        form = AuthorRequestForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
    
    def test_name_whitespace_only_invalid(self):
        """Test form with name containing only whitespace is invalid"""
        form_data = {
            'name': '   ',  # Only whitespace
        }
        form = AuthorRequestForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
    
    def test_deathday_before_birthday_invalid(self):
        """Test form with deathday before birthday is invalid"""
        form_data = {
            'name': 'Test Author',
            'birthday': '2000-01-01',
            'deathday': '1999-12-31',  # Before birthday
        }
        form = AuthorRequestForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('deathday', form.errors)
    
    def test_deathday_same_as_birthday_invalid(self):
        """Test form with deathday same as birthday is invalid"""
        form_data = {
            'name': 'Test Author',
            'birthday': '2000-01-01',
            'deathday': '2000-01-01',  # Same as birthday
        }
        form = AuthorRequestForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('deathday', form.errors)
    
    def test_deathday_after_birthday_valid(self):
        """Test form with deathday after birthday is valid"""
        form_data = {
            'name': 'Test Author',
            'birthday': '2000-01-01',
            'deathday': '2020-01-01',  # After birthday
        }
        form = AuthorRequestForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_birthday_without_deathday_valid(self):
        """Test form with birthday but no deathday is valid"""
        form_data = {
            'name': 'Test Author',
            'birthday': '2000-01-01',
        }
        form = AuthorRequestForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_deathday_without_birthday_valid(self):
        """Test form with deathday but no birthday is valid"""
        form_data = {
            'name': 'Test Author',
            'deathday': '2020-01-01',
        }
        form = AuthorRequestForm(data=form_data)
        self.assertTrue(form.is_valid())


class AuthorRequestFormFieldTests(AuthorRequestFormTestCase):
    """Test AuthorRequestForm field configuration"""
    
    def test_form_fields(self):
        """Test form has correct fields"""
        form = AuthorRequestForm()
        expected_fields = ['name', 'pen_name', 'description', 'birthday', 'deathday', 'gender', 'country']
        self.assertEqual(list(form.fields.keys()), expected_fields)
    
    def test_gender_choices(self):
        """Test gender field has correct choices"""
        form = AuthorRequestForm()
        gender_field = form.fields['gender']
        
        # Should have empty choice plus all Gender enum choices
        expected_choices = [('', '--- Chọn giới tính ---')] + Gender.choices()
        self.assertEqual(gender_field.choices, expected_choices)
        self.assertFalse(gender_field.required)
    
    def test_form_widgets(self):
        """Test form widgets are correctly configured"""
        form = AuthorRequestForm()
        
        # Test name widget
        name_widget = form.fields['name'].widget
        self.assertIn('form-control', name_widget.attrs['class'])
        self.assertIn('required', name_widget.attrs)
        
        # Test description widget
        description_widget = form.fields['description'].widget
        self.assertIn('form-control', description_widget.attrs['class'])
        self.assertEqual(description_widget.attrs['rows'], 4)
        
        # Test birthday widget - check if it's a DateInput widget
        birthday_widget = form.fields['birthday'].widget
        self.assertIn('form-control', birthday_widget.attrs['class'])
        if 'type' in birthday_widget.attrs:
            self.assertEqual(birthday_widget.attrs['type'], 'date')
        
        # Test deathday widget - check if it's a DateInput widget
        deathday_widget = form.fields['deathday'].widget
        self.assertIn('form-control', deathday_widget.attrs['class'])
        if 'type' in deathday_widget.attrs:
            self.assertEqual(deathday_widget.attrs['type'], 'date')


class AuthorRequestFormSaveTests(AuthorRequestFormTestCase):
    """Test AuthorRequestForm save functionality"""
    
    def test_form_save_creates_author_request(self):
        """Test form save creates AuthorRequest instance"""
        form_data = {
            'name': 'Test Author',
            'pen_name': 'Test Pen Name',
            'description': 'Test description',
            'country': 'Vietnam',
        }
        form = AuthorRequestForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        # Test save with commit=False
        author_request = form.save(commit=False)
        author_request.created_by = self.user
        author_request.save()
        
        self.assertEqual(author_request.name, 'Test Author')
        self.assertEqual(author_request.pen_name, 'Test Pen Name')
        self.assertEqual(author_request.description, 'Test description')
        self.assertEqual(author_request.country, 'Vietnam')
        self.assertEqual(author_request.created_by, self.user)
    
    def test_form_save_with_dates(self):
        """Test form save with date fields"""
        form_data = {
            'name': 'Test Author',
            'birthday': '1980-01-01',
            'deathday': '2020-12-31',
        }
        form = AuthorRequestForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        author_request = form.save(commit=False)
        author_request.created_by = self.user
        author_request.save()
        
        self.assertEqual(author_request.birthday, date(1980, 1, 1))
        self.assertEqual(author_request.deathday, date(2020, 12, 31))


class AuthorRequestFormCleaningTests(AuthorRequestFormTestCase):
    """Test AuthorRequestForm data cleaning"""
    
    def test_clean_name_strips_whitespace(self):
        """Test clean_name strips whitespace"""
        form_data = {
            'name': '  Test Author  ',
        }
        form = AuthorRequestForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['name'], 'Test Author')
    
    def test_clean_name_minimum_length(self):
        """Test clean_name enforces minimum length"""
        form_data = {
            'name': 'AB',  # 2 characters - should be valid
        }
        form = AuthorRequestForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        form_data = {
            'name': 'A',  # 1 character - should be invalid
        }
        form = AuthorRequestForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
    
    def test_clean_deathday_validation(self):
        """Test clean_deathday validates against birthday"""
        # Test deathday after birthday (valid)
        form_data = {
            'name': 'Test Author',
            'birthday': '1980-01-01',
            'deathday': '2020-01-01',
        }
        form = AuthorRequestForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        # Test deathday before birthday (invalid)
        form_data = {
            'name': 'Test Author',
            'birthday': '2020-01-01',
            'deathday': '1980-01-01',
        }
        form = AuthorRequestForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('deathday', form.errors)


class AuthorRequestFormLabelTests(AuthorRequestFormTestCase):
    """Test AuthorRequestForm field labels"""
    
    def test_field_labels(self):
        """Test form field labels are correctly set"""
        form = AuthorRequestForm()
        
        expected_labels = {
            'name': 'Tên tác giả *',
            'pen_name': 'Bút danh',
            'description': 'Mô tả',
            'birthday': 'Ngày sinh',
            'deathday': 'Ngày mất',
            'gender': 'Giới tính',
            'country': 'Quốc gia',
        }
        
        for field_name, expected_label in expected_labels.items():
            with self.subTest(field=field_name):
                self.assertEqual(form.fields[field_name].label, expected_label)
