from django.test import TestCase
from interactions.forms import RequestForm, AdminRequestProcessForm
from constants import MAX_REQUEST_TITLE_LENGTH
import warnings

warnings.filterwarnings("ignore", message="No directory at:")


class RequestFormTest(TestCase):
    def test_request_form_valid_data(self):
        """Test form với dữ liệu hợp lệ"""
        form_data = {
            'title': 'Test Request Title',
            'content': 'This is a detailed test request content that should be valid.'
        }
        form = RequestForm(data=form_data)
        self.assertTrue(form.is_valid())
        
    def test_request_form_empty_data(self):
        """Test form với dữ liệu rỗng"""
        form = RequestForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
        self.assertIn('content', form.errors)
        
    def test_request_form_title_too_short(self):
        """Test title quá ngắn"""
        form_data = {
            'title': 'abc',  # Chỉ có 3 ký tự
            'content': 'Valid content here'
        }
        form = RequestForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
        self.assertIn('ít nhất 5 ký tự', str(form.errors['title']))
        
    def test_request_form_content_too_short(self):
        """Test content quá ngắn"""
        form_data = {
            'title': 'Valid Title',
            'content': 'short'  # Chỉ có 5 ký tự
        }
        form = RequestForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('content', form.errors)
        self.assertIn('ít nhất 10 ký tự', str(form.errors['content']))
        
    def test_request_form_title_max_length(self):
        """Test title với độ dài tối đa"""
        long_title = 'x' * (MAX_REQUEST_TITLE_LENGTH + 1)
        form_data = {
            'title': long_title,
            'content': 'Valid content here'
        }
        form = RequestForm(data=form_data)
        self.assertFalse(form.is_valid())
        
    def test_request_form_title_valid_length(self):
        """Test title với độ dài hợp lệ"""
        valid_title = 'x' * MAX_REQUEST_TITLE_LENGTH
        form_data = {
            'title': valid_title,
            'content': 'Valid content here'
        }
        form = RequestForm(data=form_data)
        self.assertTrue(form.is_valid())
        
    def test_request_form_strips_whitespace(self):
        """Test form tự động loại bỏ khoảng trắng"""
        form_data = {
            'title': '  Test Title  ',
            'content': '  Test content with spaces  '
        }
        form = RequestForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['title'], 'Test Title')
        self.assertEqual(form.cleaned_data['content'], 'Test content with spaces')
        
    def test_request_form_whitespace_only_title(self):
        """Test title chỉ có khoảng trắng"""
        form_data = {
            'title': '     ',
            'content': 'Valid content'
        }
        form = RequestForm(data=form_data)
        self.assertFalse(form.is_valid())
        
    def test_request_form_whitespace_only_content(self):
        """Test content chỉ có khoảng trắng"""
        form_data = {
            'title': 'Valid Title',
            'content': '     '
        }
        form = RequestForm(data=form_data)
        self.assertFalse(form.is_valid())
        
    def test_request_form_fields_required(self):
        """Test tất cả fields đều required"""
        form = RequestForm()
        for field_name, field in form.fields.items():
            self.assertTrue(field.required, f"Field {field_name} should be required")
            
    def test_request_form_widgets(self):
        """Test form widgets"""
        form = RequestForm()
        
        # Test title widget
        title_widget = form.fields['title'].widget
        self.assertEqual(title_widget.attrs['class'], 'form-control')
        self.assertIn('placeholder', title_widget.attrs)
        self.assertEqual(title_widget.attrs['maxlength'], str(MAX_REQUEST_TITLE_LENGTH))
        
        # Test content widget
        content_widget = form.fields['content'].widget
        self.assertEqual(content_widget.attrs['class'], 'form-control')
        self.assertEqual(content_widget.attrs['rows'], 6)
        
    def test_request_form_labels(self):
        """Test form labels"""
        form = RequestForm()
        self.assertEqual(str(form.fields['title'].label), 'Tiêu đề')
        self.assertEqual(str(form.fields['content'].label), 'Nội dung')
        
    def test_request_form_help_texts(self):
        """Test form help texts"""
        form = RequestForm()
        self.assertIn('Tóm tắt ngắn gọn', str(form.fields['title'].help_text))
        self.assertIn('Mô tả chi tiết', str(form.fields['content'].help_text))


class AdminRequestProcessFormTest(TestCase):
    def test_admin_form_valid_data(self):
        """Test admin form với dữ liệu hợp lệ"""
        form_data = {
            'admin_note': 'Request has been reviewed and processed successfully.'
        }
        form = AdminRequestProcessForm(data=form_data)
        self.assertTrue(form.is_valid())
        
    def test_admin_form_empty_data(self):
        """Test admin form với dữ liệu rỗng (hợp lệ vì admin_note không bắt buộc)"""
        form = AdminRequestProcessForm(data={})
        self.assertTrue(form.is_valid())
        
    def test_admin_form_empty_note(self):
        """Test admin form với admin_note rỗng"""
        form_data = {
            'admin_note': ''
        }
        form = AdminRequestProcessForm(data=form_data)
        self.assertTrue(form.is_valid())
        
    def test_admin_form_field_not_required(self):
        """Test admin_note field không bắt buộc"""
        form = AdminRequestProcessForm()
        self.assertFalse(form.fields['admin_note'].required)
        
    def test_admin_form_widget(self):
        """Test admin form widget"""
        form = AdminRequestProcessForm()
        
        admin_note_widget = form.fields['admin_note'].widget
        self.assertEqual(admin_note_widget.attrs['class'], 'form-control')
        self.assertEqual(admin_note_widget.attrs['rows'], 4)
        self.assertIn('placeholder', admin_note_widget.attrs)
        
    def test_admin_form_label(self):
        """Test admin form label"""
        form = AdminRequestProcessForm()
        self.assertEqual(str(form.fields['admin_note'].label), 'Ghi chú admin')
        
    def test_admin_form_help_text(self):
        """Test admin form help text"""
        form = AdminRequestProcessForm()
        self.assertIn('Phản hồi hoặc ghi chú', str(form.fields['admin_note'].help_text))
        
    def test_admin_form_long_note(self):
        """Test admin form với ghi chú dài"""
        long_note = 'x' * 1000  # Ghi chú rất dài
        form_data = {
            'admin_note': long_note
        }
        form = AdminRequestProcessForm(data=form_data)
        self.assertTrue(form.is_valid())
        
    def test_admin_form_special_characters(self):
        """Test admin form với ký tự đặc biệt"""
        form_data = {
            'admin_note': 'Note with special chars: @#$%^&*()_+={}[]|\\:";\'<>?,./'
        }
        form = AdminRequestProcessForm(data=form_data)
        self.assertTrue(form.is_valid())
        
    def test_admin_form_multiline_note(self):
        """Test admin form với ghi chú nhiều dòng"""
        form_data = {
            'admin_note': '''Line 1 of the note
Line 2 of the note
Line 3 of the note'''
        }
        form = AdminRequestProcessForm(data=form_data)
        self.assertTrue(form.is_valid())
