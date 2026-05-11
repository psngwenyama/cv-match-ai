from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.conf import settings
from django.db import models
from django.http import FileResponse
from profiles.models import Profile
from ai_services.services import CVGenerationService
from .models import CV, CVVersion, CVApplication, Template, UserTemplate
from .serializers import (
    CVSerializer, CVDetailSerializer, CVCreateSerializer,
    CVAnalyzeSerializer, CVVersionSerializer, CVApplicationSerializer,
    TemplateSerializer, TemplateDetailSerializer, TemplateUploadSerializer
)
from .utils import download_cv_response, render_cv_with_template
import logging
import os
import zipfile
from io import BytesIO

logger = logging.getLogger(__name__)


class TemplateViewSet(viewsets.ModelViewSet):
    """
    ViewSet for template operations including upload, download, and management
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = TemplateSerializer
    
    def get_queryset(self):
        queryset = Template.objects.filter(is_active=True)
        
        # Filter by public/private
        if self.request.user.is_authenticated:
            # Show public templates + user's own private templates
            queryset = queryset.filter(
                models.Q(is_public=True) | 
                models.Q(created_by=self.request.user)
            )
        else:
            # Anonymous users see only public templates
            queryset = queryset.filter(is_public=True)
        
        # Filter by favorites
        if self.request.query_params.get('favorites') == 'true':
            if self.request.user.is_authenticated:
                queryset = queryset.filter(favorited_by__user=self.request.user)
        
        return queryset.distinct()
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TemplateDetailSerializer
        elif self.action == 'create':
            return TemplateUploadSerializer
        return TemplateSerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user if self.request.user.is_authenticated else None)
    
    @action(detail=True, methods=['post'])
    def favorite(self, request, pk=None):
        """Add template to user's favorites"""
        template = self.get_object()
        favorite, created = UserTemplate.objects.get_or_create(
            user=request.user,
            template=template
        )
        if created:
            return Response({'status': 'favorited'}, status=status.HTTP_201_CREATED)
        return Response({'status': 'already favorited'}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def unfavorite(self, request, pk=None):
        """Remove template from user's favorites"""
        template = self.get_object()
        deleted = UserTemplate.objects.filter(user=request.user, template=template).delete()
        if deleted[0] > 0:
            return Response({'status': 'unfavorited'}, status=status.HTTP_200_OK)
        return Response({'status': 'not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Download template files as a zip"""
        template = self.get_object()
        
        # Create a zip file containing template files
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            # Add appropriate file based on template type
            if template.template_type == 'html' and template.html_file and template.html_file.path:
                try:
                    html_path = template.html_file.path
                    zip_file.write(html_path, os.path.basename(html_path))
                    
                    # Add CSS file if exists
                    if template.css_file and template.css_file.path:
                        css_path = template.css_file.path
                        zip_file.write(css_path, os.path.basename(css_path))
                except Exception as e:
                    logger.error(f"Error adding HTML file to zip: {e}")
            
            elif template.template_type == 'docx' and template.docx_file and template.docx_file.path:
                try:
                    docx_path = template.docx_file.path
                    zip_file.write(docx_path, os.path.basename(docx_path))
                except Exception as e:
                    logger.error(f"Error adding DOCX file to zip: {e}")
            
            elif template.template_type == 'pdf' and template.pdf_file and template.pdf_file.path:
                try:
                    pdf_path = template.pdf_file.path
                    zip_file.write(pdf_path, os.path.basename(pdf_path))
                except Exception as e:
                    logger.error(f"Error adding PDF file to zip: {e}")
        
        zip_buffer.seek(0)
        response = FileResponse(zip_buffer, content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="{template.name}_template.zip"'
        return response
    
    @action(detail=False, methods=['get'])
    def defaults(self, request):
        """Get default templates (pre-installed)"""
        default_templates = Template.objects.filter(is_default=True, is_active=True)
        serializer = self.get_serializer(default_templates, many=True)
        return Response(serializer.data)


class CVViewSet(viewsets.ModelViewSet):
    """
    ViewSet for CV operations including generate, analyze, download, etc.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CVSerializer

    def get_queryset(self):
        """Return CVs belonging to the current user"""
        return CV.objects.filter(user=self.request.user).order_by('-created_at')

    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action == 'retrieve':
            return CVDetailSerializer
        return CVSerializer

    def perform_create(self, serializer):
        """Set the user when creating a CV"""
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'])
    def analyze(self, request):
        """
        Analyze job description without generating CV
        Accepts optional 'provider' parameter to choose AI service
        """
        serializer = CVAnalyzeSerializer(data=request.data)
        if serializer.is_valid():
            job_description = serializer.validated_data['job_description']
            
            # Get provider from request or use default
            provider = request.data.get('provider', settings.AI_PROVIDER)
            
            # Validate provider
            if provider not in ['gemini', 'openai']:
                provider = settings.AI_PROVIDER
            
            try:
                # Get AI analysis
                ai_service = CVGenerationService(provider=provider)
                analysis = ai_service.analyze_job_description(job_description)
                
                # Add provider info to response
                analysis['provider_used'] = provider
                
                return Response(analysis, status=status.HTTP_200_OK)
            except Exception as e:
                logger.error(f"AI analysis error: {str(e)}")
                return Response(
                    {'error': f'AI service error: {str(e)}', 'provider': provider},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def generate(self, request):
        """
        Generate a new CV based on job description
        Accepts optional 'provider' parameter to choose AI service
        """
        serializer = CVCreateSerializer(data=request.data)
        if serializer.is_valid():
            # Get user's profile
            profile = get_object_or_404(Profile, user=request.user)
            
            # Check if profile has enough data
            if not profile.work_experiences.exists() and not profile.education.exists():
                return Response(
                    {'error': 'Please complete your profile with work experience and education first'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get selected template
            template_id = request.data.get('template_id')
            template = None
            if template_id:
                try:
                    template = Template.objects.get(id=template_id, is_active=True)
                except Template.DoesNotExist:
                    template = Template.objects.filter(is_default=True).first()
            else:
                template = Template.objects.filter(is_default=True).first()
            
            # Get provider from request or use default
            provider = request.data.get('provider', settings.AI_PROVIDER)
            
            # Validate provider
            if provider not in ['gemini', 'openai']:
                provider = settings.AI_PROVIDER
            
            try:
                # Generate CV using AI with selected provider
                ai_service = CVGenerationService(provider=provider)
                cv_content, analysis = ai_service.generate_cv(
                    profile=profile,
                    job_description=serializer.validated_data['job_description']
                )
                
                # Render template snapshot if template selected and is HTML
                template_snapshot = ''
                if template and template.template_type == 'html':
                    try:
                        template_snapshot = render_cv_with_template(cv_content, template)
                    except Exception as e:
                        logger.error(f"Template rendering error: {e}")
                        template_snapshot = ''
                
                # Create CV record - ensure template_snapshot is never None
                cv = CV.objects.create(
                    user=request.user,
                    profile=profile,
                    title=f"CV for {serializer.validated_data.get('job_title', 'New Position')}",
                    job_title=serializer.validated_data.get('job_title', ''),
                    company=serializer.validated_data.get('company', ''),
                    job_description=serializer.validated_data['job_description'],
                    template=template,
                    template_snapshot=template_snapshot or '',  # Ensure it's never None
                    content=cv_content,
                    ai_analysis=analysis,
                    match_score=analysis.get('match_score', 0),
                    keywords_matched=analysis.get('matched_skills', []),
                    missing_keywords=analysis.get('missing_skills', [])
                )
                
                # Create initial version
                CVVersion.objects.create(
                    cv=cv,
                    version_number=1,
                    content=cv_content,
                    changes_summary="Initial generation"
                )
                
                response_data = CVDetailSerializer(cv).data
                response_data['provider_used'] = provider
                
                return Response(response_data, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                logger.error(f"CV generation error: {str(e)}")
                import traceback
                traceback.print_exc()
                return Response(
                    {'error': f'CV generation failed: {str(e)}', 'provider': provider},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Duplicate an existing CV"""
        original = self.get_object()
        
        # Create new CV based on original
        new_cv = CV.objects.create(
            user=request.user,
            profile=original.profile,
            title=f"{original.title} (Copy)",
            job_title=original.job_title,
            company=original.company,
            job_description=original.job_description,
            template=original.template,
            content=original.content,
            ai_analysis=original.ai_analysis,
            match_score=original.match_score,
            keywords_matched=original.keywords_matched,
            missing_keywords=original.missing_keywords,
            status='generated'
        )
        
        return Response(CVSerializer(new_cv).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Download CV as PDF"""
        cv = self.get_object()
        
        try:
            # Update download timestamp
            cv.downloaded_at = timezone.now()
            cv.save(update_fields=['downloaded_at'])
            
            # Generate and return PDF
            return download_cv_response(cv)
            
        except Exception as e:
            logger.error(f"PDF Generation Error for CV {cv.id}: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response(
                {'error': f'Failed to generate PDF: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def mark_applied(self, request, pk=None):
        """Mark CV as applied to a job"""
        cv = self.get_object()
        cv.status = 'applied'
        cv.applied_at = timezone.now()
        cv.save()
        
        # Create application record
        application_data = {
            'cv': cv.id,
            'company': request.data.get('company', cv.company),
            'position': request.data.get('position', cv.job_title),
            'application_url': request.data.get('application_url', ''),
            'notes': request.data.get('notes', '')
        }
        
        application_serializer = CVApplicationSerializer(data=application_data)
        if application_serializer.is_valid():
            application_serializer.save(cv=cv)
        else:
            # Log error but don't fail the request
            logger.error(f"Failed to create application record: {application_serializer.errors}")
        
        return Response(CVDetailSerializer(cv).data)

    @action(detail=True, methods=['get'])
    def versions(self, request, pk=None):
        """Get all versions of a CV"""
        cv = self.get_object()
        versions = CVVersion.objects.filter(cv=cv).order_by('-version_number')
        serializer = CVVersionSerializer(versions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def create_version(self, request, pk=None):
        """Create a new version of the CV"""
        cv = self.get_object()
        
        # Get the latest version number
        latest_version = cv.versions.order_by('-version_number').first()
        new_version_number = (latest_version.version_number + 1) if latest_version else 1
        
        version = CVVersion.objects.create(
            cv=cv,
            version_number=new_version_number,
            content=request.data.get('content', cv.content),
            changes_summary=request.data.get('changes_summary', '')
        )
        
        # Update CV content if provided
        if 'content' in request.data:
            cv.content = request.data['content']
            cv.save()
        
        serializer = CVVersionSerializer(version)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """Get statistics for a CV"""
        cv = self.get_object()
        
        # Get applications count
        applications_count = cv.applications.count()
        
        # Get versions count
        versions_count = cv.versions.count()
        
        # Calculate days since creation
        days_since_creation = (timezone.now() - cv.created_at).days
        
        stats_data = {
            'applications_count': applications_count,
            'versions_count': versions_count,
            'days_since_creation': days_since_creation,
            'download_count': 1 if cv.downloaded_at else 0,
            'match_score': cv.match_score,
            'created_at': cv.created_at,
            'last_updated': cv.updated_at,
            'last_downloaded': cv.downloaded_at,
            'last_applied': cv.applied_at,
        }
        
        return Response(stats_data)


class CVVersionViewSet(viewsets.ModelViewSet):
    """ViewSet for CV version operations"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CVVersionSerializer

    def get_queryset(self):
        cv_id = self.kwargs.get('cv_pk')
        return CVVersion.objects.filter(cv_id=cv_id, cv__user=self.request.user).order_by('-version_number')

    def perform_create(self, serializer):
        cv = get_object_or_404(CV, id=self.kwargs.get('cv_pk'), user=self.request.user)
        version_number = cv.versions.count() + 1
        serializer.save(cv=cv, version_number=version_number)

    @action(detail=True, methods=['post'])
    def restore(self, request, cv_pk=None, pk=None):
        """Restore a previous version of the CV"""
        version = self.get_object()
        cv = version.cv
        
        # Update CV content to this version
        cv.content = version.content
        cv.save()
        
        # Create a new version record for the restore
        new_version = CVVersion.objects.create(
            cv=cv,
            version_number=cv.versions.count() + 1,
            content=version.content,
            changes_summary=f"Restored from version {version.version_number}"
        )
        
        return Response(CVVersionSerializer(new_version).data)


class CVApplicationViewSet(viewsets.ModelViewSet):
    """ViewSet for CV application operations"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CVApplicationSerializer

    def get_queryset(self):
        cv_id = self.kwargs.get('cv_pk')
        return CVApplication.objects.filter(cv_id=cv_id, cv__user=self.request.user).order_by('-applied_date')

    def perform_create(self, serializer):
        cv = get_object_or_404(CV, id=self.kwargs.get('cv_pk'), user=self.request.user)
        serializer.save(cv=cv)

    @action(detail=True, methods=['post'])
    def update_status(self, request, cv_pk=None, pk=None):
        """Update application status"""
        application = self.get_object()
        new_status = request.data.get('status')
        
        if new_status:
            application.status = new_status
            if new_status == 'interviewing' and not application.interview_date:
                application.interview_date = timezone.now()
            elif new_status == 'offer' and not application.response_date:
                application.response_date = timezone.now()
            
            application.save()
            
            # Update CV status if application status changes
            cv = application.cv
            cv.status = new_status
            cv.save()
        
        serializer = self.get_serializer(application)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_note(self, request, cv_pk=None, pk=None):
        """Add a note to the application"""
        application = self.get_object()
        note = request.data.get('note', '')
        
        if note:
            # Append note to existing notes or create new
            timestamp = timezone.now().strftime('%Y-%m-%d %H:%M')
            if application.notes:
                application.notes += f"\n\n{timestamp}: {note}"
            else:
                application.notes = f"{timestamp}: {note}"
            
            application.save()
        
        serializer = self.get_serializer(application)
        return Response(serializer.data)


class CVStatsViewSet(viewsets.ViewSet):
    """ViewSet for CV statistics"""
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        """Get overall CV statistics for the user"""
        cvs = CV.objects.filter(user=request.user)
        
        total_cvs = cvs.count()
        applied_cvs = cvs.filter(status='applied').count()
        interviewing_cvs = cvs.filter(status='interviewing').count()
        offers_received = cvs.filter(status='offer').count()
        
        # Calculate average match score
        cvs_with_scores = cvs.exclude(match_score__isnull=True).exclude(match_score=0)
        avg_match_score = cvs_with_scores.aggregate(avg=models.Avg('match_score'))['avg'] or 0
        
        # Get most common missing skills
        all_missing_skills = []
        for cv in cvs:
            if cv.missing_keywords:
                all_missing_skills.extend(cv.missing_keywords)
        
        from collections import Counter
        common_missing = Counter(all_missing_skills).most_common(5)
        
        stats_data = {
            'total_cvs': total_cvs,
            'applied_cvs': applied_cvs,
            'interviewing_cvs': interviewing_cvs,
            'offers_received': offers_received,
            'success_rate': round((offers_received / total_cvs * 100) if total_cvs > 0 else 0, 1),
            'average_match_score': round(avg_match_score, 1),
            'common_missing_skills': [skill for skill, count in common_missing],
        }
        
        return Response(stats_data)