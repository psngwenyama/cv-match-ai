from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Profile, WorkExperience, Education, Skill, 
    Project, Certification, Language
)

class WorkExperienceInline(admin.TabularInline):
    model = WorkExperience
    extra = 0
    fields = ('title', 'company', 'start_date', 'end_date', 'current')
    readonly_fields = ('created_at', 'updated_at')

class EducationInline(admin.TabularInline):
    model = Education
    extra = 0
    fields = ('degree', 'institution', 'start_date', 'end_date', 'current')
    readonly_fields = ('created_at', 'updated_at')

class SkillInline(admin.TabularInline):
    model = Skill
    extra = 0
    fields = ('name', 'level', 'years_experience')
    readonly_fields = ('created_at', 'updated_at')

class ProjectInline(admin.TabularInline):
    model = Project
    extra = 0
    fields = ('name', 'technologies', 'url')
    readonly_fields = ('created_at', 'updated_at')

class CertificationInline(admin.TabularInline):
    model = Certification
    extra = 0
    fields = ('name', 'issuer', 'date_obtained')
    readonly_fields = ('created_at', 'updated_at')

class LanguageInline(admin.TabularInline):
    model = Language
    extra = 0
    fields = ('name', 'proficiency')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_email', 'user_username', 'title', 'location', 'phone', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__email', 'user__username', 'title', 'location', 'summary')
    readonly_fields = ('created_at', 'updated_at', 'profile_preview')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Professional Information', {
            'fields': ('title', 'summary', 'phone', 'location')
        }),
        ('Links', {
            'fields': ('website', 'linkedin', 'github'),
            'classes': ('wide',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'profile_preview'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [
        WorkExperienceInline,
        EducationInline,
        SkillInline,
        ProjectInline,
        CertificationInline,
        LanguageInline
    ]
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'
    user_email.admin_order_field = 'user__email'
    
    def user_username(self, obj):
        return obj.user.username
    user_username.short_description = 'Username'
    user_username.admin_order_field = 'user__username'
    
    def profile_preview(self, obj):
        if obj.id:
            return format_html(
                '<a href="/admin/profiles/profile/{}/change/" target="_blank">View Profile</a>',
                obj.id
            )
        return "Not saved yet"
    profile_preview.short_description = 'Profile Link'

@admin.register(WorkExperience)
class WorkExperienceAdmin(admin.ModelAdmin):
    list_display = ('id', 'profile_link', 'title', 'company', 'location', 'start_date', 'end_date', 'current', 'created_at')
    list_filter = ('current', 'created_at', 'start_date')
    search_fields = ('title', 'company', 'location', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Profile Information', {
            'fields': ('profile',)
        }),
        ('Experience Details', {
            'fields': ('title', 'company', 'location', 'start_date', 'end_date', 'current')
        }),
        ('Description', {
            'fields': ('description', 'achievements', 'technologies')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def profile_link(self, obj):
        return format_html(
            '<a href="/admin/profiles/profile/{}/change/">{}</a>',
            obj.profile.id,
            obj.profile.user.email
        )
    profile_link.short_description = 'Profile'

@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ('id', 'profile_link', 'degree', 'institution', 'location', 'start_date', 'end_date', 'current', 'gpa')
    list_filter = ('current', 'created_at', 'start_date')
    search_fields = ('degree', 'institution', 'location', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Profile Information', {
            'fields': ('profile',)
        }),
        ('Education Details', {
            'fields': ('degree', 'institution', 'location', 'start_date', 'end_date', 'current')
        }),
        ('Additional Information', {
            'fields': ('description', 'gpa', 'achievements')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def profile_link(self, obj):
        return format_html(
            '<a href="/admin/profiles/profile/{}/change/">{}</a>',
            obj.profile.id,
            obj.profile.user.email
        )
    profile_link.short_description = 'Profile'

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('id', 'profile_link', 'name', 'level', 'years_experience', 'created_at')
    list_filter = ('level', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Profile Information', {
            'fields': ('profile',)
        }),
        ('Skill Details', {
            'fields': ('name', 'level', 'years_experience')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def profile_link(self, obj):
        return format_html(
            '<a href="/admin/profiles/profile/{}/change/">{}</a>',
            obj.profile.id,
            obj.profile.user.email
        )
    profile_link.short_description = 'Profile'

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'profile_link', 'name', 'technologies_list', 'url', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'description', 'technologies')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Profile Information', {
            'fields': ('profile',)
        }),
        ('Project Details', {
            'fields': ('name', 'description', 'technologies', 'url', 'github_url')
        }),
        ('Timeline', {
            'fields': ('start_date', 'end_date')
        }),
        ('Highlights', {
            'fields': ('highlights',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def profile_link(self, obj):
        return format_html(
            '<a href="/admin/profiles/profile/{}/change/">{}</a>',
            obj.profile.id,
            obj.profile.user.email
        )
    profile_link.short_description = 'Profile'
    
    def technologies_list(self, obj):
        if obj.technologies:
            return ", ".join(obj.technologies)
        return "-"
    technologies_list.short_description = 'Technologies'

@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'profile_link', 'name', 'issuer', 'date_obtained', 'expiration_date')
    list_filter = ('date_obtained', 'expiration_date')
    search_fields = ('name', 'issuer', 'credential_id')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Profile Information', {
            'fields': ('profile',)
        }),
        ('Certification Details', {
            'fields': ('name', 'issuer', 'date_obtained', 'expiration_date')
        }),
        ('Credential Information', {
            'fields': ('credential_id', 'credential_url')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def profile_link(self, obj):
        return format_html(
            '<a href="/admin/profiles/profile/{}/change/">{}</a>',
            obj.profile.id,
            obj.profile.user.email
        )
    profile_link.short_description = 'Profile'

@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('id', 'profile_link', 'name', 'proficiency', 'created_at')
    list_filter = ('proficiency', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Profile Information', {
            'fields': ('profile',)
        }),
        ('Language Details', {
            'fields': ('name', 'proficiency')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def profile_link(self, obj):
        return format_html(
            '<a href="/admin/profiles/profile/{}/change/">{}</a>',
            obj.profile.id,
            obj.profile.user.email
        )
    profile_link.short_description = 'Profile'