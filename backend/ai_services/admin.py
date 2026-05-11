from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.urls import path, re_path
from django.utils.html import format_html

# Note: AI Services app doesn't have models, but we'll create a simple admin interface
# for monitoring AI usage if needed in the future

# Simple admin views for monitoring
@staff_member_required
def ai_usage_stats(request):
    """Simple view to show AI usage statistics"""
    # In production, you'd track API calls in a model
    context = {
        'title': 'AI Service Usage Statistics',
        # Add your stats here
    }
    return render(request, 'admin/ai_services/usage.html', context)

@staff_member_required
def prompt_templates(request):
    """View to show current prompt templates"""
    try:
        from ..ai_services.prompts import (
            JOB_ANALYSIS_PROMPT,
            CV_GENERATION_PROMPT,
            SKILL_EXTRACTION_PROMPT,
            CONTENT_IMPROVEMENT_PROMPT
        )
        
        context = {
            'title': 'AI Prompt Templates',
            'prompts': [
                {'name': 'Job Analysis', 'template': JOB_ANALYSIS_PROMPT},
                {'name': 'CV Generation', 'template': CV_GENERATION_PROMPT},
                {'name': 'Skill Extraction', 'template': SKILL_EXTRACTION_PROMPT},
                {'name': 'Content Improvement', 'template': CONTENT_IMPROVEMENT_PROMPT},
            ]
        }
    except ImportError:
        # Fallback if prompts module not found
        context = {
            'title': 'AI Prompt Templates',
            'prompts': [
                {'name': 'Job Analysis', 'template': 'Prompt template not available'},
                {'name': 'CV Generation', 'template': 'Prompt template not available'},
                {'name': 'Skill Extraction', 'template': 'Prompt template not available'},
                {'name': 'Content Improvement', 'template': 'Prompt template not available'},
            ]
        }
    return render(request, 'admin/ai_services/prompts.html', context)

# Add URLs for the custom views
urlpatterns = [
    re_path(r'^ai_services/usage/$', ai_usage_stats, name='ai_usage_stats'),
    re_path(r'^ai_services/prompts/$', prompt_templates, name='ai_prompts'),
]

# Monkey patch the admin site to include our URLs
original_get_urls = admin.site.get_urls

def get_urls():
    urls = original_get_urls()
    urls += urlpatterns
    return urls

admin.site.get_urls = get_urls