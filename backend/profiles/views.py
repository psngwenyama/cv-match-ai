from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .models import Profile, WorkExperience, Education, Skill, Project, Certification, Language
from .serializers import (
    ProfileSerializer, ProfileDetailSerializer, WorkExperienceSerializer,
    EducationSerializer, SkillSerializer, ProjectSerializer,
    CertificationSerializer, LanguageSerializer
)

class ProfileViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProfileSerializer

    def get_queryset(self):
        return Profile.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProfileDetailSerializer
        return ProfileSerializer

    def get_object(self):
        """Get or create profile for the current user"""
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        return profile

    def list(self, request):
        """GET /api/profiles/profile/ - Get user profile"""
        profile = self.get_object()
        serializer = self.get_serializer_class()(profile)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """GET /api/profiles/profile/<id>/ - Not typically used, but included for completeness"""
        profile = self.get_object()
        serializer = ProfileDetailSerializer(profile)
        return Response(serializer.data)

    def create(self, request):
        """POST /api/profiles/profile/ - Create profile (should be auto-created on first access)"""
        profile, created = Profile.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        """PUT /api/profiles/profile/<id>/ - Full update"""
        profile = self.get_object()
        serializer = self.get_serializer(profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        """PATCH /api/profiles/profile/<id>/ - Partial update (what we need)"""
        profile = self.get_object()
        serializer = self.get_serializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """DELETE /api/profiles/profile/<id>/ - Delete profile"""
        profile = self.get_object()
        profile.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get', 'put', 'patch'])
    def me(self, request):
        """Custom endpoint for current user's profile - supports GET, PUT, PATCH"""
        profile = self.get_object()
        
        if request.method == 'GET':
            serializer = ProfileDetailSerializer(profile)
            return Response(serializer.data)
        
        elif request.method in ['PUT', 'PATCH']:
            serializer = ProfileSerializer(profile, data=request.data, partial=(request.method == 'PATCH'))
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class WorkExperienceViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = WorkExperienceSerializer

    def get_queryset(self):
        profile = get_object_or_404(Profile, user=self.request.user)
        return WorkExperience.objects.filter(profile=profile)

    def perform_create(self, serializer):
        profile = get_object_or_404(Profile, user=self.request.user)
        serializer.save(profile=profile)

class EducationViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = EducationSerializer

    def get_queryset(self):
        profile = get_object_or_404(Profile, user=self.request.user)
        return Education.objects.filter(profile=profile)

    def perform_create(self, serializer):
        profile = get_object_or_404(Profile, user=self.request.user)
        serializer.save(profile=profile)

class SkillViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SkillSerializer

    def get_queryset(self):
        profile = get_object_or_404(Profile, user=self.request.user)
        return Skill.objects.filter(profile=profile)

    def perform_create(self, serializer):
        profile = get_object_or_404(Profile, user=self.request.user)
        serializer.save(profile=profile)

class ProjectViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProjectSerializer

    def get_queryset(self):
        profile = get_object_or_404(Profile, user=self.request.user)
        return Project.objects.filter(profile=profile)

    def perform_create(self, serializer):
        profile = get_object_or_404(Profile, user=self.request.user)
        serializer.save(profile=profile)

class CertificationViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CertificationSerializer

    def get_queryset(self):
        profile = get_object_or_404(Profile, user=self.request.user)
        return Certification.objects.filter(profile=profile)

    def perform_create(self, serializer):
        profile = get_object_or_404(Profile, user=self.request.user)
        serializer.save(profile=profile)

class LanguageViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LanguageSerializer

    def get_queryset(self):
        profile = get_object_or_404(Profile, user=self.request.user)
        return Language.objects.filter(profile=profile)

    def perform_create(self, serializer):
        profile = get_object_or_404(Profile, user=self.request.user)
        serializer.save(profile=profile)