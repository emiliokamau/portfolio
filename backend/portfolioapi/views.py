
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Project, Quest, Resume, Skill, PortfolioProfile
from .serializers import ProjectSerializer, QuestSerializer, ResumeSerializer, SkillSerializer, PortfolioProfileSerializer
from .messaging import MessageService
from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
import logging
from django.conf import settings
from .serializers import CredentialRequestSerializer
from .models import CredentialDownloadRequest

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


class PortfolioProfileView(APIView):
	permission_classes = [permissions.AllowAny]

	def get(self, request):
		profile = PortfolioProfile.load()
		serializer = PortfolioProfileSerializer(profile)
		data = serializer.data
		if data.get('profile_photo'):
			data['profile_photo'] = request.build_absolute_uri(data['profile_photo'])
		return Response(data, status=status.HTTP_200_OK)


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
		channels = request.data.get('channels', ['email', 'whatsapp'])

		# Validation
		if not all([name, email, message]):
			return Response(
				{'error': 'Name, email, and message are required'},
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


class CredentialRequestView(APIView):
	"""Send requested credentials to visitor email and notify portfolio owner."""
	throttle_classes = [AnonRateThrottle, UserRateThrottle]

	def post(self, request):
		serializer = CredentialRequestSerializer(data=request.data)
		if not serializer.is_valid():
			return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

		validated = serializer.validated_data
		document_type = validated['document_type']
		doc = Resume.objects.filter(doc_type=document_type).order_by('-uploaded_at').first()
		if not doc or not doc.file:
			return Response(
				{'error': f'{document_type} is not available yet. Please upload it in admin first.'},
				status=status.HTTP_404_NOT_FOUND,
			)

		req = CredentialDownloadRequest.objects.create(
			full_name=validated.get('full_name', ''),
			email=validated['email'],
			document_type=document_type,
			consent_given=validated['consent_given'],
			ip_address=request.META.get('REMOTE_ADDR'),
			user_agent=(request.META.get('HTTP_USER_AGENT', '')[:255]),
		)

		doc_label = dict(Resume.DOCUMENT_TYPES).get(document_type, document_type)
		visitor_subject = f'Your requested {doc_label} from The Cloud Lab'
		visitor_body = (
			f"Hello {validated.get('full_name') or 'there'},\n\n"
			f"Attached is the {doc_label} you requested from Emilio Kamau's portfolio.\n"
			"Thank you for your interest.\n\n"
			"Regards,\nThe Cloud Lab"
		)
		visitor_result = MessageService.send_email_with_attachments(
			subject=visitor_subject,
			recipient=validated['email'],
			body=visitor_body,
			attachment_paths=[doc.file.path],
		)

		owner_email = getattr(settings, 'ADMIN_EMAIL', settings.DEFAULT_FROM_EMAIL)
		notify_subject = f'Credential download request: {doc_label}'
		notify_body = (
			"A portfolio visitor requested your credential document.\n\n"
			f"Name: {validated.get('full_name', 'Not provided')}\n"
			f"Email: {validated['email']}\n"
			f"Document: {doc_label}\n"
			f"Consent Given: {validated['consent_given']}\n"
		)
		notify_result = MessageService.send_email(
			subject=notify_subject,
			recipient=owner_email,
			body=notify_body,
		)

		if visitor_result.get('success'):
			req.status = 'sent'
			req.status_message = 'Credential sent to visitor email.'
			req.save(update_fields=['status', 'status_message'])
			return Response(
				{
					'status': 'success',
					'message': f'{doc_label} has been sent to {validated["email"]}.',
					'owner_notified': notify_result.get('success', False),
				},
				status=status.HTTP_200_OK,
			)

		req.status = 'failed'
		req.status_message = visitor_result.get('error', 'Failed to send credential email.')
		req.save(update_fields=['status', 'status_message'])
		return Response(
			{'error': 'Failed to send the requested document. Please try again later.'},
			status=status.HTTP_500_INTERNAL_SERVER_ERROR,
		)
