from rest_framework import serializers
from .models import CV, CVVersion, CVApplication, Template, UserTemplate

class TemplateSerializer(serializers.ModelSerializer):
    """Serializer for listing templates"""
    thumbnail_url = serializers.SerializerMethodField()
    preview_url = serializers.SerializerMethodField()
    file_url = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    
    class Meta:
        model = Template
        fields = ['id', 'name', 'description', 'template_type', 'thumbnail_url', 
                  'preview_url', 'file_url', 'is_default', 'is_public', 
                  'is_favorited', 'created_at']
    
    def get_thumbnail_url(self, obj):
        if obj.thumbnail:
            return obj.thumbnail.url
        return None
    
    def get_preview_url(self, obj):
        if obj.preview_image:
            return obj.preview_image.url
        return None
    
    def get_file_url(self, obj):
        if obj.template_type == 'html' and obj.html_file:
            return obj.html_file.url
        elif obj.template_type == 'docx' and obj.docx_file:
            return obj.docx_file.url
        elif obj.template_type == 'pdf' and obj.pdf_file:
            return obj.pdf_file.url
        return None
    
    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return UserTemplate.objects.filter(user=request.user, template=obj).exists()
        return False


class TemplateDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for single template view"""
    thumbnail_url = serializers.SerializerMethodField()
    preview_url = serializers.SerializerMethodField()
    html_url = serializers.SerializerMethodField()
    css_url = serializers.SerializerMethodField()
    docx_url = serializers.SerializerMethodField()
    pdf_url = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    
    class Meta:
        model = Template
        fields = ['id', 'name', 'description', 'template_type', 'thumbnail_url', 
                  'preview_url', 'html_url', 'css_url', 'docx_url', 'pdf_url',
                  'is_default', 'is_public', 'created_by_name', 'is_favorited', 
                  'created_at', 'updated_at']
    
    def get_thumbnail_url(self, obj):
        if obj.thumbnail:
            return obj.thumbnail.url
        return None
    
    def get_preview_url(self, obj):
        if obj.preview_image:
            return obj.preview_image.url
        return None
    
    def get_html_url(self, obj):
        if obj.html_file:
            return obj.html_file.url
        return None
    
    def get_css_url(self, obj):
        if obj.css_file:
            return obj.css_file.url
        return None
    
    def get_docx_url(self, obj):
        if obj.docx_file:
            return obj.docx_file.url
        return None
    
    def get_pdf_url(self, obj):
        if obj.pdf_file:
            return obj.pdf_file.url
        return None
    
    def get_created_by_name(self, obj):
        if obj.created_by:
            return obj.created_by.username
        return 'System'
    
    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return UserTemplate.objects.filter(user=request.user, template=obj).exists()
        return False


class TemplateUploadSerializer(serializers.ModelSerializer):
    """Serializer for uploading new templates"""
    class Meta:
        model = Template
        fields = ['name', 'description', 'template_type', 'thumbnail', 
                  'html_file', 'css_file', 'docx_file', 'pdf_file', 
                  'preview_image', 'is_public']
    
    def validate(self, data):
        template_type = data.get('template_type', 'html')
        
        # Validate required file based on type
        if template_type == 'html' and not data.get('html_file'):
            raise serializers.ValidationError({"html_file": "HTML file is required for HTML templates"})
        elif template_type == 'docx' and not data.get('docx_file'):
            raise serializers.ValidationError({"docx_file": "Word file is required for DOCX templates"})
        elif template_type == 'pdf' and not data.get('pdf_file'):
            raise serializers.ValidationError({"pdf_file": "PDF file is required for PDF templates"})
        
        return data
    
    def validate_html_file(self, value):
        if value and not value.name.endswith('.html'):
            raise serializers.ValidationError("File must be an HTML file")
        return value
    
    def validate_css_file(self, value):
        if value and not value.name.endswith('.css'):
            raise serializers.ValidationError("File must be a CSS file")
        return value
    
    def validate_docx_file(self, value):
        if value and not value.name.endswith(('.docx', '.doc')):
            raise serializers.ValidationError("File must be a Word document")
        return value
    
    def validate_pdf_file(self, value):
        if value and not value.name.endswith('.pdf'):
            raise serializers.ValidationError("File must be a PDF file")
        return value


class CVSerializer(serializers.ModelSerializer):
    template_name = serializers.CharField(source='template.name', read_only=True)
    template_type = serializers.CharField(source='template.template_type', read_only=True)
    
    class Meta:
        model = CV
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'user')


class CVDetailSerializer(serializers.ModelSerializer):
    applications = serializers.SerializerMethodField()
    versions_count = serializers.SerializerMethodField()
    template_details = TemplateSerializer(source='template', read_only=True)
    
    class Meta:
        model = CV
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'user')

    def get_applications(self, obj):
        return CVApplicationSerializer(obj.applications.all(), many=True).data

    def get_versions_count(self, obj):
        return obj.versions.count()


class CVCreateSerializer(serializers.Serializer):
    job_description = serializers.CharField()
    template_id = serializers.IntegerField(required=False, allow_null=True)
    company = serializers.CharField(required=False, allow_blank=True)
    job_title = serializers.CharField(required=False, allow_blank=True)
    provider = serializers.CharField(required=False, default='gemini')


class CVAnalyzeSerializer(serializers.Serializer):
    job_description = serializers.CharField()
    provider = serializers.CharField(required=False, default='gemini')


class CVVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CVVersion
        fields = '__all__'
        read_only_fields = ('id', 'created_at')


class CVApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CVApplication
        fields = '__all__'
        read_only_fields = ('id', 'applied_date', 'cv')