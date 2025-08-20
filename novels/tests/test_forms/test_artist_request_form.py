"""
Unit tests for ArtistRequestForm
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from datetime import date, timedelta

from novels.forms import ArtistRequestForm
from novels.models import ArtistRequest
from constants import Gender, UserRole


User = get_user_model()


class ArtistRequestFormTestCase(TestCase):
    """Base test case for ArtistRequestForm tests"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123',
            role=UserRole.USER.value
        )


class ArtistRequestFormValidationTests(ArtistRequestFormTestCase):
    """Test ArtistRequestForm validation"""
    
    def test_valid_form_minimal(self):
        """Test form with minimal valid data"""
        form_data = {
            'name': 'Test Artist',
        }
        form = ArtistRequestForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_valid_form_full(self):
        """Test form with all valid data"""
        form_data = {
            'name': 'Test Artist',
            'pen_name': 'Test Pen Name',
            'description': 'Test description',
            'birthday': '1985-01-01',
            'deathday': '2021-12-31',
            'gender': Gender.FEMALE.value,
            'country': 'Japan',
        }
        form = ArtistRequestForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_empty_name_invalid(self):
        """Test form with empty name is invalid"""
        form_data = {
            'name': '',
        }
        form = ArtistRequestForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
    
    def test_name_too_short_invalid(self):
        """Test form with name too short is invalid"""
        form_data = {
            'name': 'A',  # Only 1 character
        }
        form = ArtistRequestForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
    
    def test_name_whitespace_only_invalid(self):
        """Test form with name containing only whitespace is invalid"""
        form_data = {
            'name': '   ',  # Only whitespace
        }
        form = ArtistRequestForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
    
    def test_deathday_before_birthday_invalid(self):
        """Test form with deathday before birthday is invalid"""
        form_data = {
            'name': 'Test Artist',
            'birthday': '2000-01-01',
            'deathday': '1999-12-31',  # Before birthday
        }
        form = ArtistRequestForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('deathday', form.errors)
    
    def test_deathday_same_as_birthday_invalid(self):
        """Test form with deathday same as birthday is invalid"""
        form_data = {
            'name': 'Test Artist',
            'birthday': '2000-01-01',
            'deathday': '2000-01-01',  # Same as birthday
        }
        form = ArtistRequestForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('deathday', form.errors)
    
    def test_deathday_after_birthday_valid(self):
        """Test form with deathday after birthday is valid"""
        form_data = {
            'name': 'Test Artist',
            'birthday': '2000-01-01',
            'deathday': '2020-01-01',  # After birthday
        }
        form = ArtistRequestForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_birthday_without_deathday_valid(self):
        """Test form with birthday but no deathday is valid"""
        form_data = {
            'name': 'Test Artist',
            'birthday': '2000-01-01',
        }
        form = ArtistRequestForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_deathday_without_birthday_valid(self):
        """Test form with deathday but no birthday is valid"""
        form_data = {
            'name': 'Test Artist',
            'deathday': '2020-01-01',
        }
        form = ArtistRequestForm(data=form_data)
        self.assertTrue(form.is_valid())


class ArtistRequestFormFieldTests(ArtistRequestFormTestCase):
    """Test ArtistRequestForm field configuration"""
    
    def test_form_fields(self):
        """Test form has correct fields"""
        form = ArtistRequestForm()
        expected_fields = ['name', 'pen_name', 'description', 'birthday', 'deathday', 'gender', 'country']
        self.assertEqual(list(form.fields.keys()), expected_fields)
    
    def test_gender_choices(self):
        """Test gender field has correct choices"""
        form = ArtistRequestForm()
        gender_field = form.fields['gender']
        
        # Should have empty choice plus all Gender enum choices
        expected_choices = [('', '--- Chọn giới tính ---')] + Gender.choices()
        self.assertEqual(gender_field.choices, expected_choices)
        self.assertFalse(gender_field.required)
    
    def test_form_widgets(self):
        """Test form widgets are correctly configured"""
        form = ArtistRequestForm()
        
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


class ArtistRequestFormSaveTests(ArtistRequestFormTestCase):
    """Test ArtistRequestForm save functionality"""
    
    def test_form_save_creates_artist_request(self):
        """Test form save creates ArtistRequest instance"""
        form_data = {
            'name': 'Test Artist',
            'pen_name': 'Test Pen Name',
            'description': 'Test description',
            'country': 'Japan',
        }
        form = ArtistRequestForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        # Test save with commit=False
        artist_request = form.save(commit=False)
        artist_request.created_by = self.user
        artist_request.save()
        
        self.assertEqual(artist_request.name, 'Test Artist')
        self.assertEqual(artist_request.pen_name, 'Test Pen Name')
        self.assertEqual(artist_request.description, 'Test description')
        self.assertEqual(artist_request.country, 'Japan')
        self.assertEqual(artist_request.created_by, self.user)
    
    def test_form_save_with_dates(self):
        """Test form save with date fields"""
        form_data = {
            'name': 'Test Artist',
            'birthday': '1985-01-01',
            'deathday': '2021-12-31',
        }
        form = ArtistRequestForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        artist_request = form.save(commit=False)
        artist_request.created_by = self.user
        artist_request.save()
        
        self.assertEqual(artist_request.birthday, date(1985, 1, 1))
        self.assertEqual(artist_request.deathday, date(2021, 12, 31))


class ArtistRequestFormCleaningTests(ArtistRequestFormTestCase):
    """Test ArtistRequestForm data cleaning"""
    
    def test_clean_name_strips_whitespace(self):
        """Test clean_name strips whitespace"""
        form_data = {
            'name': '  Test Artist  ',
        }
        form = ArtistRequestForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['name'], 'Test Artist')
    
    def test_clean_name_minimum_length(self):
        """Test clean_name enforces minimum length"""
        form_data = {
            'name': 'AB',  # 2 characters - should be valid
        }
        form = ArtistRequestForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        form_data = {
            'name': 'A',  # 1 character - should be invalid
        }
        form = ArtistRequestForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
    
    def test_clean_deathday_validation(self):
        """Test clean_deathday validates against birthday"""
        # Test deathday after birthday (valid)
        form_data = {
            'name': 'Test Artist',
            'birthday': '1985-01-01',
            'deathday': '2021-01-01',
        }
        form = ArtistRequestForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        # Test deathday before birthday (invalid)
        form_data = {
            'name': 'Test Artist',
            'birthday': '2021-01-01',
            'deathday': '1985-01-01',
        }
        form = ArtistRequestForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('deathday', form.errors)


class ArtistRequestFormLabelTests(ArtistRequestFormTestCase):
    """Test ArtistRequestForm field labels"""
    
    def test_field_labels(self):
        """Test form field labels are correctly set"""
        form = ArtistRequestForm()
        
        expected_labels = {
            'name': 'Tên họa sĩ *',
            'pen_name': 'Nghệ danh',
            'description': 'Mô tả',
            'birthday': 'Ngày sinh',
            'deathday': 'Ngày mất',
            'gender': 'Giới tính',
            'country': 'Quốc gia',
        }
        
        for field_name, expected_label in expected_labels.items():
            with self.subTest(field=field_name):
                self.assertEqual(form.fields[field_name].label, expected_label)


class ArtistRequestFormPlaceholderTests(ArtistRequestFormTestCase):
    """Test ArtistRequestForm field placeholders"""
    
    def test_field_placeholders(self):
        """Test form field placeholders are correctly set"""
        form = ArtistRequestForm()
        
        # Test specific placeholders
        self.assertIn('Tên thật của họa sĩ', form.fields['name'].widget.attrs['placeholder'])
        self.assertIn('Nghệ danh (nếu có)', form.fields['pen_name'].widget.attrs['placeholder'])
        self.assertIn('Mô tả về họa sĩ', form.fields['description'].widget.attrs['placeholder'])
        self.assertIn('Quốc gia', form.fields['country'].widget.attrs['placeholder'])
