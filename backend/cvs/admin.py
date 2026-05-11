from django.contrib import admin
from django.utils.html import format_html
from .models import CV, CVVersion, CVApplication, Template, UserTemplate

class CVVersionInline(admin.TabularInline):
    model = CVVersion
    extra = 0
    fields = ('version_number', 'created_at', 'changes_summary')
    readonly_fields = ('created_at',)
    ordering = ('-version_number',)

class CVApplicationInline(admin.TabularInline):
    model = CVApplication
    extra = 0
    fields = ('company', 'position', 'applied_date', 'status', 'response_received')
    readonly_fields = ('applied_date',)
    ordering = ('-applied_date',)


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'template_type', 'is_default', 'is_public', 'is_active', 'created_by', 'created_at')
    list_filter = ('template_type', 'is_default', 'is_public', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at', 'template_preview', 'file_links')
    
    fieldsets = (
        ('Template Information', {
            'fields': ('name', 'description', 'template_type', 'is_default', 'is_public', 'is_active')
        }),
        ('Template Files', {
            'fields': ('html_file', 'css_file', 'docx_file', 'pdf_file')
        }),
        ('Images', {
            'fields': ('thumbnail', 'preview_image')
        }),
        ('Ownership', {
            'fields': ('created_by',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'template_preview', 'file_links'),
            'classes': ('collapse',)
        }),
    )
    
    def template_preview(self, obj):
        if obj.thumbnail:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 200px;" />', obj.thumbnail.url)
        return "No thumbnail"
    template_preview.short_description = 'Preview'
    
    def file_links(self, obj):
        links = []
        if obj.html_file:
            links.append(f'<a href="{obj.html_file.url}" target="_blank">HTML File</a>')
        if obj.css_file:
            links.append(f'<a href="{obj.css_file.url}" target="_blank">CSS File</a>')
        if obj.docx_file:
            links.append(f'<a href="{obj.docx_file.url}" target="_blank">Word File</a>')
        if obj.pdf_file:
            links.append(f'<a href="{obj.pdf_file.url}" target="_blank">PDF File</a>')
        return format_html("<br>".join(links)) if links else "No files"
    file_links.short_description = 'Files'


@admin.register(UserTemplate)
class UserTemplateAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'template', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'template__name')


@admin.register(CV)
class CVAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_email', 'job_title', 'company', 'template_name', 'match_score', 'status', 'created_at', 'download_count')
    list_filter = ('status', 'match_score', 'created_at', 'template')
    search_fields = ('user__email', 'job_title', 'company', 'job_description')
    readonly_fields = ('created_at', 'updated_at', 'downloaded_at', 'applied_at', 'cv_preview', 'content_preview')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'profile')
        }),
        ('Job Information', {
            'fields': ('title', 'job_title', 'company', 'job_description', 'job_description_url')
        }),
        ('CV Content', {
            'fields': ('content', 'template', 'template_snapshot', 'content_preview')
        }),
        ('AI Analysis', {
            'fields': ('ai_analysis', 'match_score', 'keywords_matched', 'missing_keywords')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'downloaded_at', 'applied_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [CVVersionInline, CVApplicationInline]
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User'
    user_email.admin_order_field = 'user__email'
    
    def template_name(self, obj):
        return obj.template.name if obj.template else 'None'
    template_name.short_description = 'Template'
    
    def download_count(self, obj):
        return 1 if obj.downloaded_at else 0
    download_count.short_description = 'Downloads'
    
    def cv_preview(self, obj):
        if obj.id:
            return format_html(
                '<a href="/admin/cvs/cv/{}/change/" target="_blank">View CV</a>',
                obj.id
            )
        return "Not saved yet"
    cv_preview.short_description = 'CV Link'
    
    def content_preview(self, obj):
        if obj.content and isinstance(obj.content, dict):
            preview = "<div style='max-height: 300px; overflow-y: auto; padding: 10px; background: #f8f9fa;'>"
            
            if 'summary' in obj.content:
                preview += f"<strong>Summary:</strong> {obj.content['summary'][:200]}...<br><br>"
            
            if 'work_experience' in obj.content and obj.content['work_experience']:
                preview += "<strong>Work Experience:</strong><br>"
                for exp in obj.content['work_experience'][:2]:
                    preview += f"• {exp.get('title', '')} at {exp.get('company', '')}<br>"
            
            if 'skills' in obj.content and obj.content['skills']:
                preview += f"<br><strong>Skills:</strong> {', '.join(obj.content['skills'][:5])}"
            
            preview += "</div>"
            return format_html(preview)
        return "No content available"
    content_preview.short_description = 'Content Preview'
    
    actions = ['mark_as_applied', 'mark_as_interviewing', 'mark_as_offer']

    def mark_as_applied(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='applied', applied_at=timezone.now())
    mark_as_applied.short_description = "Mark selected CVs as Applied"

    def mark_as_interviewing(self, request, queryset):
        queryset.update(status='interviewing')
    mark_as_interviewing.short_description = "Mark selected CVs as Interviewing"

    def mark_as_offer(self, request, queryset):
        queryset.update(status='offer')
    mark_as_offer.short_description = "Mark selected CVs as Offer Received"


@admin.register(CVVersion)
class CVVersionAdmin(admin.ModelAdmin):
    list_display = ('id', 'cv_link', 'version_number', 'created_at', 'changes_summary_short')
    list_filter = ('created_at',)
    search_fields = ('cv__job_title', 'changes_summary')
    readonly_fields = ('created_at', 'content_preview')
    
    fieldsets = (
        ('Version Information', {
            'fields': ('cv', 'version_number')
        }),
        ('Content', {
            'fields': ('content', 'content_preview', 'changes_summary')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def cv_link(self, obj):
        return format_html(
            '<a href="/admin/cvs/cv/{}/change/">{}</a>',
            obj.cv.id,
            obj.cv.job_title
        )
    cv_link.short_description = 'CV'
    
    def changes_summary_short(self, obj):
        if obj.changes_summary:
            return obj.changes_summary[:50] + "..." if len(obj.changes_summary) > 50 else obj.changes_summary
        return "-"
    changes_summary_short.short_description = 'Changes'
    
    def content_preview(self, obj):
        if obj.content and isinstance(obj.content, dict):
            preview = "<div style='max-height: 200px; overflow-y: auto; padding: 10px; background: #f8f9fa;'>"
            
            if 'summary' in obj.content:
                preview += f"<strong>Summary:</strong> {obj.content['summary'][:150]}...<br>"
            
            preview += "</div>"
            return format_html(preview)
        return "No content available"
    content_preview.short_description = 'Preview'


@admin.register(CVApplication)
class CVApplicationAdmin(admin.ModelAdmin):
    list_display = ('id', 'cv_link', 'company', 'position', 'applied_date', 'status', 'response_received', 'interview_date')
    list_filter = ('status', 'response_received', 'applied_date')
    search_fields = ('cv__job_title', 'company', 'position', 'notes')
    readonly_fields = ('applied_date',)
    
    fieldsets = (
        ('Application Information', {
            'fields': ('cv', 'company', 'position')
        }),
        ('Application Details', {
            'fields': ('application_url', 'applied_date', 'status', 'notes')
        }),
        ('Response Information', {
            'fields': ('response_received', 'response_date', 'interview_date')
        }),
    )
    
    def cv_link(self, obj):
        return format_html(
            '<a href="/admin/cvs/cv/{}/change/">{}</a>',
            obj.cv.id,
            obj.cv.job_title
        )
    cv_link.short_description = 'CV'
    
    actions = ['mark_response_received', 'mark_interview_scheduled']

    def mark_response_received(self, request, queryset):
        from django.utils import timezone
        queryset.update(response_received=True, response_date=timezone.now())
    mark_response_received.short_description = "Mark response received"

    def mark_interview_scheduled(self, request, queryset):
        from django.utils import timezone
        queryset.update(interview_date=timezone.now())
    mark_interview_scheduled.short_description = "Mark interview scheduled (now)"