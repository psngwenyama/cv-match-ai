from rest_framework import serializers
from .models import (
    Profile, WorkExperience, Education, Skill, 
    Project, Certification, Language
)
import re
from datetime import datetime

class WorkExperienceSerializer(serializers.ModelSerializer):
    # Use CharField instead of DateField to avoid automatic validation
    start_date = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    end_date = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = WorkExperience
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'profile')

    def validate_start_date(self, value):
        """Validate that start_date is in YYYY-MM format or empty"""
        if value:
            if not re.match(r'^\d{4}-\d{2}$', value):
                raise serializers.ValidationError("Start date must be in YYYY-MM format (e.g., 2024-02)")
        return value

    def validate_end_date(self, value):
        """Validate that end_date is in YYYY-MM format or empty"""
        if value:
            if not re.match(r'^\d{4}-\d{2}$', value):
                raise serializers.ValidationError("End date must be in YYYY-MM format (e.g., 2024-02)")
        return value

    def validate(self, data):
        """Additional validation"""
        # If current is True, end_date should be empty
        if data.get('current') and data.get('end_date'):
            raise serializers.ValidationError({"end_date": "End date should not be provided if current position"})
        return data

    def to_internal_value(self, data):
        """Convert incoming data before validation"""
        # Make a copy of data to avoid modifying original
        data = data.copy() if hasattr(data, 'copy') else dict(data)
        
        # Handle empty strings
        if 'start_date' in data and not data['start_date']:
            data['start_date'] = None
        if 'end_date' in data and not data['end_date']:
            data['end_date'] = None
            
        return super().to_internal_value(data)

    def create(self, validated_data):
        """Create work experience - convert YYYY-MM to YYYY-MM-01 for storage"""
        # Convert month format to full date (first day of month) for storage
        if validated_data.get('start_date'):
            try:
                # Parse YYYY-MM and create date object
                year, month = map(int, validated_data['start_date'].split('-'))
                validated_data['start_date'] = datetime(year, month, 1).date()
            except (ValueError, AttributeError):
                validated_data['start_date'] = None
        
        if validated_data.get('end_date'):
            try:
                year, month = map(int, validated_data['end_date'].split('-'))
                validated_data['end_date'] = datetime(year, month, 1).date()
            except (ValueError, AttributeError):
                validated_data['end_date'] = None
        
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Update work experience - convert YYYY-MM to YYYY-MM-01 for storage"""
        # Handle start_date
        if 'start_date' in validated_data:
            if validated_data['start_date']:
                try:
                    year, month = map(int, validated_data['start_date'].split('-'))
                    validated_data['start_date'] = datetime(year, month, 1).date()
                except (ValueError, AttributeError):
                    validated_data['start_date'] = None
            else:
                validated_data['start_date'] = None
        
        # Handle end_date
        if 'end_date' in validated_data:
            if validated_data['end_date']:
                try:
                    year, month = map(int, validated_data['end_date'].split('-'))
                    validated_data['end_date'] = datetime(year, month, 1).date()
                except (ValueError, AttributeError):
                    validated_data['end_date'] = None
            else:
                validated_data['end_date'] = None
        
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        """Convert back to YYYY-MM format when returning data to frontend"""
        data = super().to_representation(instance)
        
        # Convert stored full dates back to YYYY-MM format
        if instance.start_date and hasattr(instance.start_date, 'strftime'):
            data['start_date'] = instance.start_date.strftime('%Y-%m')
        else:
            data['start_date'] = ''
            
        if instance.end_date and hasattr(instance.end_date, 'strftime'):
            data['end_date'] = instance.end_date.strftime('%Y-%m')
        else:
            data['end_date'] = ''
        
        return data


class EducationSerializer(serializers.ModelSerializer):
    # Use CharField instead of DateField to avoid automatic validation
    start_date = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    end_date = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = Education
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'profile')

    def validate_start_date(self, value):
        """Validate that start_date is in YYYY-MM format or empty"""
        if value:
            if not re.match(r'^\d{4}-\d{2}$', value):
                raise serializers.ValidationError("Start date must be in YYYY-MM format (e.g., 2024-02)")
        return value

    def validate_end_date(self, value):
        """Validate that end_date is in YYYY-MM format or empty"""
        if value:
            if not re.match(r'^\d{4}-\d{2}$', value):
                raise serializers.ValidationError("End date must be in YYYY-MM format (e.g., 2024-02)")
        return value

    def validate(self, data):
        """Additional validation"""
        # If current is True, end_date should be empty
        if data.get('current') and data.get('end_date'):
            raise serializers.ValidationError({"end_date": "End date should not be provided if currently studying"})
        return data

    def to_internal_value(self, data):
        """Convert incoming data before validation"""
        # Make a copy of data to avoid modifying original
        data = data.copy() if hasattr(data, 'copy') else dict(data)
        
        # Handle empty strings
        if 'start_date' in data and not data['start_date']:
            data['start_date'] = None
        if 'end_date' in data and not data['end_date']:
            data['end_date'] = None
            
        return super().to_internal_value(data)

    def create(self, validated_data):
        """Create education - convert YYYY-MM to YYYY-MM-01 for storage"""
        # Handle start_date
        if validated_data.get('start_date'):
            try:
                year, month = map(int, validated_data['start_date'].split('-'))
                validated_data['start_date'] = datetime(year, month, 1).date()
            except (ValueError, AttributeError):
                validated_data['start_date'] = None
        
        # Handle end_date
        if validated_data.get('end_date'):
            try:
                year, month = map(int, validated_data['end_date'].split('-'))
                validated_data['end_date'] = datetime(year, month, 1).date()
            except (ValueError, AttributeError):
                validated_data['end_date'] = None
        
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Update education - convert YYYY-MM to YYYY-MM-01 for storage"""
        # Handle start_date
        if 'start_date' in validated_data:
            if validated_data['start_date']:
                try:
                    year, month = map(int, validated_data['start_date'].split('-'))
                    validated_data['start_date'] = datetime(year, month, 1).date()
                except (ValueError, AttributeError):
                    validated_data['start_date'] = None
            else:
                validated_data['start_date'] = None
        
        # Handle end_date
        if 'end_date' in validated_data:
            if validated_data['end_date']:
                try:
                    year, month = map(int, validated_data['end_date'].split('-'))
                    validated_data['end_date'] = datetime(year, month, 1).date()
                except (ValueError, AttributeError):
                    validated_data['end_date'] = None
            else:
                validated_data['end_date'] = None
        
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        """Convert back to YYYY-MM format when returning data to frontend"""
        data = super().to_representation(instance)
        
        # Convert stored full dates back to YYYY-MM format
        if instance.start_date and hasattr(instance.start_date, 'strftime'):
            data['start_date'] = instance.start_date.strftime('%Y-%m')
        else:
            data['start_date'] = ''
            
        if instance.end_date and hasattr(instance.end_date, 'strftime'):
            data['end_date'] = instance.end_date.strftime('%Y-%m')
        else:
            data['end_date'] = ''
        
        return data


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'profile')


class ProjectSerializer(serializers.ModelSerializer):
    # Use CharField for dates to handle YYYY-MM format
    start_date = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    end_date = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'profile')

    def validate_start_date(self, value):
        if value and not re.match(r'^\d{4}-\d{2}$', value):
            raise serializers.ValidationError("Start date must be in YYYY-MM format")
        return value

    def validate_end_date(self, value):
        if value and not re.match(r'^\d{4}-\d{2}$', value):
            raise serializers.ValidationError("End date must be in YYYY-MM format")
        return value

    def to_internal_value(self, data):
        data = data.copy() if hasattr(data, 'copy') else dict(data)
        if 'start_date' in data and not data['start_date']:
            data['start_date'] = None
        if 'end_date' in data and not data['end_date']:
            data['end_date'] = None
        return super().to_internal_value(data)

    def create(self, validated_data):
        if validated_data.get('start_date'):
            try:
                year, month = map(int, validated_data['start_date'].split('-'))
                validated_data['start_date'] = datetime(year, month, 1).date()
            except:
                validated_data['start_date'] = None
        if validated_data.get('end_date'):
            try:
                year, month = map(int, validated_data['end_date'].split('-'))
                validated_data['end_date'] = datetime(year, month, 1).date()
            except:
                validated_data['end_date'] = None
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'start_date' in validated_data:
            if validated_data['start_date']:
                try:
                    year, month = map(int, validated_data['start_date'].split('-'))
                    validated_data['start_date'] = datetime(year, month, 1).date()
                except:
                    validated_data['start_date'] = None
            else:
                validated_data['start_date'] = None
        if 'end_date' in validated_data:
            if validated_data['end_date']:
                try:
                    year, month = map(int, validated_data['end_date'].split('-'))
                    validated_data['end_date'] = datetime(year, month, 1).date()
                except:
                    validated_data['end_date'] = None
            else:
                validated_data['end_date'] = None
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.start_date and hasattr(instance.start_date, 'strftime'):
            data['start_date'] = instance.start_date.strftime('%Y-%m')
        else:
            data['start_date'] = ''
        if instance.end_date and hasattr(instance.end_date, 'strftime'):
            data['end_date'] = instance.end_date.strftime('%Y-%m')
        else:
            data['end_date'] = ''
        return data


class CertificationSerializer(serializers.ModelSerializer):
    # Use CharField for dates to handle YYYY-MM format
    date_obtained = serializers.CharField(required=True)
    expiration_date = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = Certification
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'profile')

    def validate_date_obtained(self, value):
        if value and not re.match(r'^\d{4}-\d{2}$', value):
            raise serializers.ValidationError("Date must be in YYYY-MM format")
        return value

    def validate_expiration_date(self, value):
        if value and not re.match(r'^\d{4}-\d{2}$', value):
            raise serializers.ValidationError("Date must be in YYYY-MM format")
        return value

    def to_internal_value(self, data):
        data = data.copy() if hasattr(data, 'copy') else dict(data)
        if 'date_obtained' in data and not data['date_obtained']:
            data['date_obtained'] = None
        if 'expiration_date' in data and not data['expiration_date']:
            data['expiration_date'] = None
        return super().to_internal_value(data)

    def create(self, validated_data):
        if validated_data.get('date_obtained'):
            try:
                year, month = map(int, validated_data['date_obtained'].split('-'))
                validated_data['date_obtained'] = datetime(year, month, 1).date()
            except:
                validated_data['date_obtained'] = None
        if validated_data.get('expiration_date'):
            try:
                year, month = map(int, validated_data['expiration_date'].split('-'))
                validated_data['expiration_date'] = datetime(year, month, 1).date()
            except:
                validated_data['expiration_date'] = None
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'date_obtained' in validated_data:
            if validated_data['date_obtained']:
                try:
                    year, month = map(int, validated_data['date_obtained'].split('-'))
                    validated_data['date_obtained'] = datetime(year, month, 1).date()
                except:
                    validated_data['date_obtained'] = None
            else:
                validated_data['date_obtained'] = None
        if 'expiration_date' in validated_data:
            if validated_data['expiration_date']:
                try:
                    year, month = map(int, validated_data['expiration_date'].split('-'))
                    validated_data['expiration_date'] = datetime(year, month, 1).date()
                except:
                    validated_data['expiration_date'] = None
            else:
                validated_data['expiration_date'] = None
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.date_obtained and hasattr(instance.date_obtained, 'strftime'):
            data['date_obtained'] = instance.date_obtained.strftime('%Y-%m')
        else:
            data['date_obtained'] = ''
        if instance.expiration_date and hasattr(instance.expiration_date, 'strftime'):
            data['expiration_date'] = instance.expiration_date.strftime('%Y-%m')
        else:
            data['expiration_date'] = ''
        return data


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'profile')


class ProfileSerializer(serializers.ModelSerializer):
    work_experiences = WorkExperienceSerializer(many=True, read_only=True)
    education = EducationSerializer(many=True, read_only=True)
    skills = SkillSerializer(many=True, read_only=True)
    projects = ProjectSerializer(many=True, read_only=True)
    certifications = CertificationSerializer(many=True, read_only=True)
    languages = LanguageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Profile
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'user')


class ProfileDetailSerializer(serializers.ModelSerializer):
    work_experiences = WorkExperienceSerializer(many=True)
    education = EducationSerializer(many=True)
    skills = SkillSerializer(many=True)
    projects = ProjectSerializer(many=True)
    certifications = CertificationSerializer(many=True)
    languages = LanguageSerializer(many=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)

    class Meta:
        model = Profile
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'user')