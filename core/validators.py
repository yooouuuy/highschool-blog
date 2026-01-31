import os
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

def validate_file_size(value):
    limit = 10 * 1024 * 1024  # 10 MB
    if value.size > limit:
        raise ValidationError(_('File too large. Size should not exceed 10 MB.'))

def validate_pdf_extension(value):
    ext = os.path.splitext(value.name)[1]
    if not ext.lower() in ['.pdf']:
        raise ValidationError(_('Unsupported file extension. Please upload a PDF file.'))

def validate_image_extension(value):
    ext = os.path.splitext(value.name)[1]
    if not ext.lower() in ['.jpg', '.jpeg', '.png']:
        raise ValidationError(_('Unsupported file extension. Please upload an image (JPG, JPEG, PNG).'))
