from django.db import models
from django.conf import settings
from profiles.models import Profile

class Template(models.Model):
    """
    Model for CV templates that users can upload and use
    """
    TEMPLATE_TYPES = [
        ('html', 'HTML/CSS'),
        ('docx', 'Microsoft Word'),
        ('pdf', 'PDF Form'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    template_type = models.CharField(max_length=10, choices=TEMPLATE_TYPES, default='html')
    
    # Template files based on type
    html_file = models.FileField(upload_to='templates/html/', blank=True, null=True, help_text='Upload HTML template file')
    css_file = models.FileField(upload_to='templates/css/', blank=True, null=True, help_text='Optional CSS file for HTML templates')
    docx_file = models.FileField(upload_to='templates/docx/', blank=True, null=True, help_text='Upload Word template file')
    pdf_file = models.FileField(upload_to='templates/pdf/', blank=True, null=True, help_text='Upload PDF template file')
    
    # Images
    thumbnail = models.ImageField(upload_to='templates/thumbnails/', null=True, blank=True)
    preview_image = models.ImageField(upload_to='templates/previews/', null=True, blank=True)
    
    # Template metadata
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True, help_text='Public templates are available to all users')
    
    # Ownership (if users can upload private templates)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
                                   null=True, blank=True, related_name='uploaded_templates')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_default', 'name']
        db_table = 'templates'
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # Ensure only one default template
        if self.is_default:
            Template.objects.filter(is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)
    
    @property
    def template_file(self):
        """Get the appropriate template file based on type"""
        if self.template_type == 'html':
            return self.html_file
        elif self.template_type == 'docx':
            return self.docx_file
        elif self.template_type == 'pdf':
            return self.pdf_file
        return None
    
    @property
    def file_url(self):
        """Get the URL of the template file"""
        if self.template_file:
            return self.template_file.url
        return None


class UserTemplate(models.Model):
    """
    Junction model for users to save/favorite templates
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorite_templates')
    template = models.ForeignKey(Template, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'template']
        db_table = 'user_templates'
    
    def __str__(self):
        return f"{self.user.email} - {self.template.name}"


class CV(models.Model):
    STATUS_CHOICES = [
        ('generated', 'Generated'),
        ('applied', 'Applied'),
        ('interviewing', 'Interviewing'),
        ('rejected', 'Rejected'),
        ('offer', 'Offer Received'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cvs')
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='cvs')
    title = models.CharField(max_length=200)
    job_title = models.CharField(max_length=200)
    company = models.CharField(max_length=200, blank=True)
    job_description = models.TextField()
    job_description_url = models.URLField(blank=True)
    
    # Content
    content = models.JSONField(default=dict)
    template = models.ForeignKey(Template, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='cvs', help_text='The template used for this CV')
    
    # Template snapshot - for HTML templates, store the rendered HTML
    template_snapshot = models.TextField(
        blank=True, 
        null=True,
        default='',
        help_text='Snapshot of template HTML when CV was generated (for HTML templates only)'
    )
    
    # For binary template data (DOCX/PDF) - store the path or reference
    template_binary_path = models.CharField(
        max_length=500, 
        blank=True, 
        null=True,
        help_text='Path to generated binary file (for DOCX/PDF templates)'
    )
    
    # AI Analysis
    ai_analysis = models.JSONField(default=dict, blank=True)
    match_score = models.IntegerField(default=0)
    keywords_matched = models.JSONField(default=list, blank=True)
    missing_keywords = models.JSONField(default=list, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='generated')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    downloaded_at = models.DateTimeField(null=True, blank=True)
    applied_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.job_title} - {self.created_at.date()}"

    class Meta:
        db_table = 'cvs'
        ordering = ['-created_at']


class CVVersion(models.Model):
    cv = models.ForeignKey(CV, on_delete=models.CASCADE, related_name='versions')
    version_number = models.IntegerField()
    content = models.JSONField(default=dict)
    changes_summary = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.cv.title} - v{self.version_number}"

    class Meta:
        db_table = 'cv_versions'
        ordering = ['-version_number']
        unique_together = ['cv', 'version_number']


class CVApplication(models.Model):
    cv = models.ForeignKey(CV, on_delete=models.CASCADE, related_name='applications')
    company = models.CharField(max_length=200)
    position = models.CharField(max_length=200)
    applied_date = models.DateTimeField(auto_now_add=True)
    application_url = models.URLField(blank=True)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=50, default='applied')
    response_received = models.BooleanField(default=False)
    response_date = models.DateTimeField(null=True, blank=True)
    interview_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.company} - {self.position}"

    class Meta:
        db_table = 'cv_applications'
        ordering = ['-applied_date']