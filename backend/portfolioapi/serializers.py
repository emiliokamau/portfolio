# Serializers for Project, Quest, Resume, Skill, and Contact
from rest_framework import serializers
from .models import Project, Quest, Resume, Skill


class SkillSerializer(serializers.ModelSerializer):
	class Meta:
		model = Skill
		fields = '__all__'


class ProjectSerializer(serializers.ModelSerializer):
	class Meta:
		model = Project
		fields = '__all__'


class QuestSerializer(serializers.ModelSerializer):
	class Meta:
		model = Quest
		fields = '__all__'


class ResumeSerializer(serializers.ModelSerializer):
	class Meta:
		model = Resume
		fields = '__all__'


class ContactSerializer(serializers.Serializer):
	"""
	Serializer for contact form submissions.
	Supports multi-channel messaging: email, WhatsApp, SMS
	"""
	name = serializers.CharField(
		max_length=200,
		required=True,
		error_messages={'required': 'Name is required'}
	)
	email = serializers.EmailField(
		required=True,
		error_messages={'required': 'Email is required', 'invalid': 'Invalid email format'}
	)
	phone = serializers.CharField(
		max_length=20,
		required=False,
		allow_blank=True,
		help_text="Phone number in format: +1234567890 (required for WhatsApp/SMS)"
	)
	message = serializers.CharField(
		required=True,
		error_messages={'required': 'Message is required'}
	)
	channels = serializers.ListField(
		child=serializers.CharField(max_length=20),
		required=False,
		default=['email'],
		help_text="Channels to use: 'email', 'whatsapp', 'sms'"
	)

	def validate_phone(self, value):
		"""Validate phone number format."""
		if value and not value.startswith('+'):
			raise serializers.ValidationError(
				"Phone number must start with '+' (e.g., +1234567890)"
			)
		return value

	def validate_channels(self, value):
		"""Validate channel selection."""
		valid_channels = {'email', 'whatsapp', 'sms'}
		invalid = set(value) - valid_channels
		if invalid:
			raise serializers.ValidationError(
				f"Invalid channels: {', '.join(invalid)}. Valid options: email, whatsapp, sms"
			)
		return value
