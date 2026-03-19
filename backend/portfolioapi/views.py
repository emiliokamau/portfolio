
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Project, Quest, Resume, Skill
from .serializers import ProjectSerializer, QuestSerializer, ResumeSerializer, SkillSerializer
from .messaging import MessageService
from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from django.conf import settings
import requests
import logging

logger = logging.getLogger(__name__)


class AdminWriteReadOnly(permissions.BasePermission):
	"""Allow public reads; restrict writes to authenticated staff users."""

	def has_permission(self, request, view):
		if request.method in SAFE_METHODS:
			return True
		return bool(request.user and request.user.is_authenticated and request.user.is_staff)


class SkillListCreateView(generics.ListCreateAPIView):
	queryset = Skill.objects.all().order_by('-created_at')
	serializer_class = SkillSerializer
	permission_classes = [permissions.AllowAny]


class ProjectListView(generics.ListCreateAPIView):
	queryset = Project.objects.all().order_by('-date_created')
	serializer_class = ProjectSerializer
	permission_classes = [AdminWriteReadOnly]
	parser_classes = [MultiPartParser, FormParser, JSONParser]


class QuestListView(generics.ListAPIView):
	queryset = Quest.objects.all()
	serializer_class = QuestSerializer


class QuestUpvoteView(APIView):
	def post(self, request):
		quest_id = request.data.get('id')
		try:
			quest = Quest.objects.get(id=quest_id)
			quest.upvotes += 1
			quest.save()
			return Response({'upvotes': quest.upvotes}, status=status.HTTP_200_OK)
		except Quest.DoesNotExist:
			return Response({'error': 'Quest not found'}, status=status.HTTP_404_NOT_FOUND)


class ContactView(APIView):
	"""
	Handle contact form submissions with multi-channel messaging.
	Supports: Email (SendGrid), WhatsApp (Twilio), SMS (Twilio)
	"""
	throttle_classes = [AnonRateThrottle, UserRateThrottle]

	def post(self, request):
		# Extract form data
		name = request.data.get('name', '').strip()
		email = request.data.get('email', '').strip()
		phone = request.data.get('phone', '').strip()
		message = request.data.get('message', '').strip()
		recaptcha_token = request.data.get('recaptcha_token', '')
		channels = request.data.get('channels', ['email', 'whatsapp'])

		# Validation
		if not all([name, email, message]):
			return Response(
				{'error': 'Name, email, and message are required'},
				status=status.HTTP_400_BAD_REQUEST
			)

		# Verify reCAPTCHA
		if not self._verify_recaptcha(recaptcha_token):
			return Response(
				{'error': 'reCAPTCHA verification failed'},
				status=status.HTTP_400_BAD_REQUEST
			)

		# Validate channels
		valid_channels = ['email', 'whatsapp', 'sms']
		if not isinstance(channels, list):
			channels = ['email', 'whatsapp']
		channels = [ch for ch in channels if ch in valid_channels]
		if not channels:
			channels = ['email', 'whatsapp']

		# Validate phone only for SMS to visitor
		if 'sms' in channels and not phone:
			return Response(
				{'error': 'Phone number required for SMS notifications'},
				status=status.HTTP_400_BAD_REQUEST
			)

		try:
			# Send messages through unified service
			result = MessageService.send_contact_notification(
				name=name,
				email=email,
				phone=phone,
				message=message,
				channels=channels
			)

			# Check if at least one channel succeeded
			success = any(
				res.get('success', False)
				for res in result['channels'].values()
				if isinstance(res, dict)
			)

			if not success:
				logger.error(f'All message channels failed for {name}')
				return Response(
					{'error': 'Failed to send message through all channels'},
					status=status.HTTP_500_INTERNAL_SERVER_ERROR
				)

			response_msg = f'Message sent via: {", ".join(channels)}'
			logger.info(f'Contact form submitted by {name} ({email}) via {channels}')

			return Response(
				{
					'status': 'success',
					'message': response_msg,
					'channels': result['channels']
				},
				status=status.HTTP_200_OK
			)

		except Exception as e:
			logger.error(f'Contact form error: {str(e)}')
			return Response(
				{'error': 'An error occurred processing your request'},
				status=status.HTTP_500_INTERNAL_SERVER_ERROR
			)

	@staticmethod
	def _verify_recaptcha(token: str) -> bool:
		"""
		Verify reCAPTCHA token with Google.

		Args:
			token: reCAPTCHA response token

		Returns:
			True if verification succeeds, False otherwise
		"""
		if not token:
			return False

		if not settings.RECAPTCHA_SECRET_KEY:
			logger.warning("reCAPTCHA secret key not configured")
			return False

		try:
			url = 'https://www.google.com/recaptcha/api/siteverify'
			data = {
				'secret': settings.RECAPTCHA_SECRET_KEY,
				'response': token
			}
			response = requests.post(url, data=data, timeout=5)
			result = response.json()
			return result.get('success', False)
		except Exception as e:
			logger.error(f'reCAPTCHA verification error: {str(e)}')
			return False
