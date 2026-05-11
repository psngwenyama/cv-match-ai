from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'profiles', views.ProfileViewSet, basename='profile')
router.register(r'work-experiences', views.WorkExperienceViewSet, basename='work-experience')
router.register(r'education', views.EducationViewSet, basename='education')
router.register(r'skills', views.SkillViewSet, basename='skill')
router.register(r'projects', views.ProjectViewSet, basename='project')
router.register(r'certifications', views.CertificationViewSet, basename='certification')
router.register(r'languages', views.LanguageViewSet, basename='language')

urlpatterns = [
    path('', include(router.urls)),
    # Add explicit me endpoint
    path('profile/me/', views.ProfileViewSet.as_view({'get': 'me', 'put': 'me', 'patch': 'me'}), name='profile-me'),
]