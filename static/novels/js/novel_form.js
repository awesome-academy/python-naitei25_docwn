// novel_form.js

$(document).ready(function() {
    // Initialize the form
    initializeForm();
});

function initializeForm() {
    initializeSelect2();
    setupFileInput();
    setupTextareaAutoResize();
    setupFormValidation();
    setupInputEventListeners();
    setupUnsavedChangesDetection();
    setupAuthorArtistHandlers();
}

/**
 * Initialize Select2 components
 */
function initializeSelect2() {
    if (typeof $.fn.select2 !== 'undefined') {
        // Author select2
        $('#id_author').select2({
            placeholder: $('#id_author').data('placeholder') || (window.gettext ? window.gettext("Chọn tác giả...") : "Chọn tác giả..."),
            allowClear: true,
            width: '100%'
        });

        // Artist select2
        $('#id_artist').select2({
            placeholder: $('#id_artist').data('placeholder') || (window.gettext ? window.gettext("Chọn họa sĩ...") : "Chọn họa sĩ..."),
            allowClear: true,
            width: '100%'
        });

        // Tags select2 (multiple)
        $('#id_tags').select2({
            placeholder: $('#id_tags').data('placeholder') || (window.gettext ? window.gettext("Chọn thẻ...") : "Chọn thẻ..."),
            allowClear: true,
            width: '100%'
        });

        // Handle Select2 focus events for better UX
        $('.select2-container').off('focus.select2Focus blur.select2Focus');
        $('.select2-container').on('focus.select2Focus', function() {
            $(this).addClass('select2-container--focus');
        }).on('blur.select2Focus', function() {
            $(this).removeClass('select2-container--focus');
        });
    }
}

/**
 * Setup file input display functionality
 */
function setupFileInput() {
    // Remove any existing event handlers to prevent duplication
    $('#id_image_file').off('change.imagePreview');
    
    $('#id_image_file').on('change.imagePreview', function() {
        const file = this.files[0];
        const $formInput = $(this).closest('.form-input');
        const $form = $('#novelForm');
        
        // Always remove existing preview first
        $formInput.find('.image-preview:not(#imagePreviewTemplate)').remove();
        
        if (file) {
            // Validate file type
            const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
            if (!allowedTypes.includes(file.type)) {
                const errorMsg = $form.data('file-type-error') || (window.gettext ? window.gettext('Vui lòng chọn một tệp hình ảnh hợp lệ (JPEG, PNG, GIF, WebP)') : 'Vui lòng chọn một tệp hình ảnh hợp lệ (JPEG, PNG, GIF, WebP)');
                alert(errorMsg); // Simple alert instead of notification
                this.value = '';
                return;
            }

            // Validate file size (max 5MB)
            const maxSize = 5 * 1024 * 1024; // 5MB in bytes
            if (file.size > maxSize) {
                const errorMsg = $form.data('file-size-error') || (window.gettext ? window.gettext('Dung lượng tệp phải nhỏ hơn 5MB') : 'Dung lượng tệp phải nhỏ hơn 5MB');
                alert(errorMsg); // Simple alert instead of notification
                this.value = '';
                return;
            }
            
            // Create image preview
            const reader = new FileReader();
            reader.onload = function(e) {
                // Clone the hidden template
                const $preview = $('#imagePreviewTemplate').clone();
                $preview.attr('id', 'activeImagePreview'); // Change ID to avoid conflicts
                $preview.removeClass('hidden').show(); // Remove hidden class and show
                
                // Update the template with actual data
                $preview.find('.preview-image').attr('src', e.target.result);
                $preview.find('.preview-file-name').text(file.name);
                $preview.find('.preview-file-size').text((file.size / 1024 / 1024).toFixed(2));
                
                // Append to form
                $formInput.append($preview);
            };
            reader.readAsDataURL(file);
        }
    });
}/**
 * Setup textarea auto-resize functionality
 */
function setupTextareaAutoResize() {
    function autoResize(textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 300) + 'px'; // Max height 300px
    }

    const summaryTextarea = document.getElementById('id_summary');
    if (summaryTextarea) {
        summaryTextarea.addEventListener('input', function() {
            autoResize(this);
        });
        
        // Initial resize
        autoResize(summaryTextarea);
    }
}

/**
 * Setup form validation and submission
 */
function setupFormValidation() {
    // Remove any existing submit handlers to prevent duplication
    $('#novelForm').off('submit.validation');
    
    $('#novelForm').on('submit.validation', function(e) {
        // Check if this is a draft save
        const isDraftSave = $(this).find('input[name="save_as_draft"]').length > 0;
        
        if (!isDraftSave) {
            // Only validate for regular submissions, not drafts
            const isValid = validateForm();
            
            if (!isValid) {
                e.preventDefault(); // Only prevent if validation fails
                showValidationErrors();
                return false;
            }
        }

        // If valid or draft save, allow form submission
        showLoadingState();
        
        // Allow the form to submit normally
        return true;
    });
}

/**
 * Validate form fields
 */
function validateForm() {
    let isValid = true;
    const errors = [];

    // Required fields validation
    const requiredFields = [
    { id: '#id_name', name: 'Tên truyện', label: $('#id_name').data('label') || (window.gettext ? window.gettext('Tên truyện') : 'Tên truyện')},
    { id: '#id_summary', name: 'Tóm tắt', label: $('#id_summary').data('label') || (window.gettext ? window.gettext('Tóm tắt') : 'Tóm tắt')}
    ];

    requiredFields.forEach(function(field) {
        const $field = $(field.id);
        const value = $field.val();
        
        if (!value || !value.trim()) {
            $field.addClass('error');
            const requiredMsg = $field.data('required-msg') || (window.gettext ? window.gettext(`${field.label} là bắt buộc`) : `${field.label} là bắt buộc`);
            errors.push(requiredMsg);
            isValid = false;
        } else {
            $field.removeClass('error');
        }
    });

    // Validate novel name length
    const nameValue = $('#id_name').val();
    if (nameValue && nameValue.trim().length < 3) {
        $('#id_name').addClass('error');
    const minLengthMsg = $('#id_name').data('min-length-msg') || (window.gettext ? window.gettext('Tên truyện phải có ít nhất 3 ký tự') : 'Tên truyện phải có ít nhất 3 ký tự');
        errors.push(minLengthMsg);
        isValid = false;
    }

    // Validate summary length
    const summaryValue = $('#id_summary').val();
    if (summaryValue && summaryValue.trim().length < 10) {
        $('#id_summary').addClass('error');
    const minLengthMsg = $('#id_summary').data('min-length-msg') || (window.gettext ? window.gettext('Tóm tắt phải có ít nhất 10 ký tự') : 'Tóm tắt phải có ít nhất 10 ký tự');
        errors.push(minLengthMsg);
        isValid = false;
    }

    // Store errors for display
    if (errors.length > 0) {
        sessionStorage.setItem('formErrors', JSON.stringify(errors));
    }

    return isValid;
}

/**
 * Show validation errors
 */
function showValidationErrors() {
    const errors = JSON.parse(sessionStorage.getItem('formErrors') || '[]');
    
    if (errors.length > 0) {
    const errorPrefix = $('#novelForm').data('error-prefix') || (window.gettext ? window.gettext('Vui lòng sửa các lỗi sau:') : 'Vui lòng sửa các lỗi sau:');
        const errorMessage = errorPrefix + '\n\n' + errors.join('\n');
        alert(errorMessage);
        
        // Focus on first error field
        const firstErrorField = $('.form-input .error').first();
        if (firstErrorField.length) {
            firstErrorField.focus();
            
            // Scroll to field
            $('html, body').animate({
                scrollTop: firstErrorField.closest('.form-group').offset().top - 100
            }, 500);
        }
    }
    
    sessionStorage.removeItem('formErrors');
}

/**
 * Show loading state during form submission
 */
function showLoadingState() {
    const $form = $('#novelForm');
    const $submitBtn = $('.submit-btn');
    
    $form.addClass('form-loading');
    const loadingText = $submitBtn.data('loading-text') || (window.gettext ? window.gettext('Đang tạo...') : 'Đang tạo...');
    $submitBtn.prop('disabled', true).text(loadingText);
}

/**
 * Hide loading state
 */
function hideLoadingState() {
    const $form = $('#novelForm');
    const $submitBtn = $('.submit-btn');
    
    $form.removeClass('form-loading');
    const defaultText = $submitBtn.data('default-text') || (window.gettext ? window.gettext('Gửi') : 'Gửi');
    $submitBtn.prop('disabled', false).text(defaultText);
}

/**
 * Setup input event listeners
 */
function setupInputEventListeners() {
    // Remove existing event handlers to prevent duplication
    $('input, textarea, select').off('input.validation change.validation');
    
    // Reset error styles on input
    $('input, textarea, select').on('input.validation change.validation', function() {
        $(this).removeClass('error');
        
        // Real-time validation feedback
        const $field = $(this);
        const fieldId = $field.attr('id');
        
        // Name field validation
        if (fieldId === 'id_name') {
            const value = $field.val().trim();
            if (value.length > 0 && value.length < 3) {
                $field.addClass('error');
            }
        }
        
        // Summary field validation
        if (fieldId === 'id_summary') {
            const value = $field.val().trim();
            if (value.length > 0 && value.length < 10) {
                $field.addClass('error');
            }
        }
    });

    // Character counter for summary field
    const $summaryField = $('#id_summary');
    if ($summaryField.length) {
        // Check if counter already exists to avoid duplication
        let $charCounter = $summaryField.next('.char-counter');
        if (!$charCounter.length) {
            $charCounter = $('<div class="char-counter"></div>');
            $summaryField.after($charCounter);
        }
        
        // Remove existing input handler and add with namespace
        $summaryField.off('input.charCounter');
        $summaryField.on('input.charCounter', function() {
            const length = $(this).val().length;
            const maxLength = $(this).data('max-length') || 2000;
            const counterTemplate = $(this).data('counter-template') || (window.gettext ? window.gettext('{current}/{max} ký tự') : '{current}/{max} ký tự');
            
            const counterText = counterTemplate.replace('{current}', length).replace('{max}', maxLength);
            $charCounter.text(counterText);
            
            if (length > maxLength) {
                $charCounter.addClass('error');
                $(this).addClass('error');
            } else {
                $charCounter.removeClass('error');
            }
        });
        
        // Initial character count
        $summaryField.trigger('input');
    }

    // Prevent form submission on Enter key in text inputs (except textarea)
    $('input[type="text"]').off('keydown.enterPrevent');
    $('input[type="text"]').on('keydown.enterPrevent', function(e) {
        if (e.keyCode === 13) {
            e.preventDefault();
            // Move to next input field
            const inputs = $('input[type="text"], textarea, select').not(':disabled');
            const currentIndex = inputs.index(this);
            if (currentIndex < inputs.length - 1) {
                inputs.eq(currentIndex + 1).focus();
            }
        }
    });
}

// Reset form to initial state
function resetForm() {
    $('#novelForm')[0].reset();
    $('.select2').val(null).trigger('change');
    $('.error').removeClass('error');
    
    // Remove image preview (but keep the template)
    $('.image-preview:not(#imagePreviewTemplate)').remove();
    
    // Reset character counter
    const $summaryField = $('#id_summary');
    if ($summaryField.length) {
        $summaryField.trigger('input'); // This will update the counter properly
    }
}

// Export functions for global access if needed
window.NovelForm = {
    reset: resetForm,
    validate: validateForm,
    showModal: showSaveDraftModal
};

/**
 * Setup unsaved changes detection
 */
function setupUnsavedChangesDetection() {
    let hasUnsavedChanges = false;
    let isSubmitting = false;
    let initialFormData = new FormData($('#novelForm')[0]);
    
    // Remove existing event handlers to prevent duplication
    $('#novelForm').off('input.unsaved change.unsaved submit.unsaved');
    $('#id_author, #id_artist, #id_tags').off('select2:select.unsaved select2:unselect.unsaved select2:clear.unsaved');
    $('#id_image_file').off('change.unsaved');
    $(document).off('click.unsaved');
    
    // Track form changes
    $('#novelForm').on('input.unsaved change.unsaved', 'input, textarea, select', function() {
        if (!isSubmitting) {
            hasUnsavedChanges = true;
        }
    });
    
    // Handle Select2 changes specifically
    $('#id_author, #id_artist, #id_tags').on('select2:select.unsaved select2:unselect.unsaved select2:clear.unsaved', function() {
        if (!isSubmitting) {
            hasUnsavedChanges = true;
        }
    });
    
    // Handle file input changes separately
    $('#id_image_file').on('change.unsaved', function() {
        if (!isSubmitting) {
            hasUnsavedChanges = true;
        }
    });
    
    // Reset unsaved changes flag when form is submitted
    $('#novelForm').on('submit.unsaved', function() {
        isSubmitting = true;
        hasUnsavedChanges = false;
    });
    
    // Check if form has meaningful data
    function hasFormData() {
        const name = $('#id_name').val() ? $('#id_name').val().trim() : '';
        const summary = $('#id_summary').val() ? $('#id_summary').val().trim() : '';
        const otherNames = $('#id_other_names').val() ? $('#id_other_names').val().trim() : '';
        const author = $('#id_author').val();
        const artist = $('#id_artist').val();
        const tags = $('#id_tags').val();
        const imageFile = $('#id_image_file')[0] ? $('#id_image_file')[0].files.length > 0 : false;
        
        const hasData = name || summary || otherNames || 
               (author && author !== '') || 
               (artist && artist !== '') || 
               (tags && tags.length > 0) || 
               imageFile;
        
        return hasData;
    }
    
    // Handle navigation within the site
    $(document).on('click.unsaved', 'a[href]:not([href^="#"]):not([href^="javascript:"]):not([target="_blank"])', function(e) {
        const $this = $(this);
        const href = $this.attr('href');
        
        if (hasUnsavedChanges && hasFormData() && !isSubmitting) {
            e.preventDefault();
            e.stopPropagation();
            showSaveDraftModal(href);
            return false;
        }
    });
    
    // Also handle button clicks that might navigate
    $(document).on('click.unsaved', 'button[data-href], .btn[data-href]', function(e) {
        const $this = $(this);
        const href = $this.data('href');
        
        if (hasUnsavedChanges && hasFormData() && !isSubmitting) {
            e.preventDefault();
            e.stopPropagation();
            showSaveDraftModal(href);
            return false;
        }
    });
    
    // Reset changes flag when user makes a choice
    window.resetUnsavedChanges = function() {
        hasUnsavedChanges = false;
        isSubmitting = true;
    };
}

/**
 * Show save draft confirmation modal
 */
function showSaveDraftModal(redirectUrl) {
    // Show the existing modal by removing hidden class and setting display
    $('#saveDraftModal').removeClass('hidden').css('display', 'flex');
    
    // Remove any existing event handlers to prevent duplication
    $('#discardBtn, #saveDraftBtn').off('click.saveDraftModal');
    
    // Handle button clicks
    $('#discardBtn').on('click.saveDraftModal', function() {
        discardChanges(redirectUrl);
    });
    
    $('#saveDraftBtn').on('click.saveDraftModal', function() {
        saveAsDraft();
    });
    
    // Handle background click to close modal
    $('#saveDraftModal').off('click.saveDraftModal').on('click.saveDraftModal', function(e) {
        if (e.target === this) {
            $(this).addClass('hidden').css('display', 'none');
        }
    });
    
    // Handle ESC key
    $(document).off('keydown.saveDraftModal').on('keydown.saveDraftModal', function(e) {
        if (e.keyCode === 27) { // ESC key
            $('#saveDraftModal').addClass('hidden').css('display', 'none');
            $(document).off('keydown.saveDraftModal');
        }
    });
    
    // Prevent modal content clicks from closing modal
    $('.save-draft-modal-content').off('click.saveDraftModal').on('click.saveDraftModal', function(e) {
        e.stopPropagation();
    });
}

/**
 * Save form as draft
 */
function saveAsDraft() {
    // Add a hidden field to indicate this is a draft save
    const existingDraftInput = $('#novelForm input[name="save_as_draft"]');
    if (existingDraftInput.length === 0) {
        $('#novelForm').append('<input type="hidden" name="save_as_draft" value="true">');
    }
    
    // Reset the unsaved changes flag
    window.resetUnsavedChanges();
    
    // Hide modal
    $('#saveDraftModal').addClass('hidden').css('display', 'none');
    $(document).off('keydown.saveDraftModal');
    
    // Submit the form
    $('#novelForm').submit();
}

/**
 * Discard changes and navigate away
 */
function discardChanges(redirectUrl) {
    // Reset the unsaved changes flag
    window.resetUnsavedChanges();
    
    // Hide modal
    $('#saveDraftModal').addClass('hidden').css('display', 'none');
    $(document).off('keydown.saveDraftModal');
    
    // Navigate to the intended destination
    if (redirectUrl === 'back') {
        window.history.back();
    } else if (redirectUrl && redirectUrl !== 'undefined' && redirectUrl !== 'null') {
        window.location.href = redirectUrl;
    } else {
        window.history.back();
    }
}

/**
 * Setup handlers for author and artist create new options
 */
function setupAuthorArtistHandlers() {
    // Handle author selection
    $('#id_author').on('change', function() {
        const selectedValue = $(this).val();
        if (selectedValue === 'create_new_author') {
            handleCreateNewAuthor();
        }
    });

    // Handle artist selection
    $('#id_artist').on('change', function() {
        const selectedValue = $(this).val();
        if (selectedValue === 'create_new_artist') {
            handleCreateNewArtist();
        }
    });
}

/**
 * Handle create new author
 */
function handleCreateNewAuthor() {
    const authorCreateUrl = '/novels/requests/author/create/';
    
    // Open in a new window/tab
    const newWindow = window.open(authorCreateUrl, '_blank', 'width=800,height=600,scrollbars=yes,resizable=yes');
    
    if (newWindow) {
        // Reset the select to previous value
        $('#id_author').val('').trigger('change');
        
        // Listen for messages from the new window
        const messageHandler = function(event) {
            if (event.origin !== window.location.origin) return;
            
            if (event.data && event.data.type === 'authorRequestCreated') {
                // Add the new option to the select
                const newOption = new Option(
                    event.data.name + ' (Chờ duyệt)', 
                    'author_request_' + event.data.id, 
                    true, 
                    true
                );
                $('#id_author').append(newOption).trigger('change');
                
                // Remove the event listener
                window.removeEventListener('message', messageHandler);
                
                // Close the popup if still open
                if (!newWindow.closed) {
                    newWindow.close();
                }
                
                // Show success message
                if (typeof showNotification === 'function') {
                    showNotification(window.gettext ? window.gettext('Yêu cầu thêm tác giả đã được tạo thành công!') : 'yêu cầu thêm tác giả đã được tạo thành công!', 'success');
                } else {
                    alert(window.gettext ? window.gettext('Yêu cầu thêm tác giả đã được tạo thành công!') : 'yêu cầu thêm tác giả đã được tạo thành công!');
                }
            }
        };
        
        window.addEventListener('message', messageHandler);
        
        // Clean up if window is closed manually
        const checkClosed = setInterval(function() {
            if (newWindow.closed) {
                window.removeEventListener('message', messageHandler);
                clearInterval(checkClosed);
            }
        }, 1000);
    } else {
        // Popup blocked, redirect to the page
        window.location.href = authorCreateUrl;
    }
}

/**
 * Handle create new artist
 */
function handleCreateNewArtist() {
    const artistCreateUrl = '/novels/requests/artist/create/';
    
    // Open in a new window/tab
    const newWindow = window.open(artistCreateUrl, '_blank', 'width=800,height=600,scrollbars=yes,resizable=yes');
    
    if (newWindow) {
        // Reset the select to previous value
        $('#id_artist').val('').trigger('change');
        
        // Listen for messages from the new window
        const messageHandler = function(event) {
            if (event.origin !== window.location.origin) return;
            
            if (event.data && event.data.type === 'artistRequestCreated') {
                // Add the new option to the select
                const newOption = new Option(
                    event.data.name + ' (Chờ duyệt)', 
                    'artist_request_' + event.data.id, 
                    true, 
                    true
                );
                $('#id_artist').append(newOption).trigger('change');
                
                // Remove the event listener
                window.removeEventListener('message', messageHandler);
                
                // Close the popup if still open
                if (!newWindow.closed) {
                    newWindow.close();
                }
                
                // Show success message
                if (typeof showNotification === 'function') {
                    showNotification(window.gettext ? window.gettext('yêu cầu thêm họa sĩ đã được tạo thành công!') : 'yêu cầu thêm họa sĩ đã được tạo thành công!', 'success');
                } else {
                    alert(window.gettext ? window.gettext('yêu cầu thêm họa sĩ đã được tạo thành công!') : 'yêu cầu thêm họa sĩ đã được tạo thành công!');
                }
            }
        };
        
        window.addEventListener('message', messageHandler);
        
        // Clean up if window is closed manually
        const checkClosed = setInterval(function() {
            if (newWindow.closed) {
                window.removeEventListener('message', messageHandler);
                clearInterval(checkClosed);
            }
        }, 1000);
    } else {
        // Popup blocked, redirect to the page
        window.location.href = artistCreateUrl;
    }
}
