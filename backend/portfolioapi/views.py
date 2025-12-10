
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Project, Quest, Resume, Skill
from .serializers import ProjectSerializer, QuestSerializer, ResumeSerializer, SkillSerializer
# GET/POST /api/skills
from rest_framework import permissions
class SkillListCreateView(generics.ListCreateAPIView):
	queryset = Skill.objects.all().order_by('-created_at')
	serializer_class = SkillSerializer
	permission_classes = [permissions.AllowAny]
from django.core.mail import send_mail
from django.conf import settings
import requests

# GET /api/projects
class ProjectListView(generics.ListAPIView):
	queryset = Project.objects.all().order_by('-date_created')
	serializer_class = ProjectSerializer

# GET /api/quests
class QuestListView(generics.ListAPIView):
	queryset = Quest.objects.all()
	serializer_class = QuestSerializer

# POST /api/quests/vote
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

# POST /api/contact
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

class ContactView(APIView):
	throttle_classes = [AnonRateThrottle, UserRateThrottle]
	def post(self, request):
		name = request.data.get('name')
		email = request.data.get('email')
		message = request.data.get('message')
		recaptcha_token = request.data.get('recaptcha_token')
		# Verify reCAPTCHA
		url = 'https://www.google.com/recaptcha/api/siteverify'
		data = {
			'secret': settings.RECAPTCHA_SECRET_KEY,
			'response': recaptcha_token
		}
		recaptcha_response = requests.post(url, data=data)
		result = recaptcha_response.json()
		if not result.get('success', False):
			return Response({'error': 'reCAPTCHA verification failed.'}, status=status.HTTP_400_BAD_REQUEST)
		subject = f'Portfolio Contact from {name}'
		body = f'From: {name} <{email}>\n\nMessage:\n{message}'
		send_mail(
			subject,
			body,
			settings.DEFAULT_FROM_EMAIL,
			['emiliokamau35@gmail.com'],
			fail_silently=False,
		)
		# Send Slack notification
		slack_url = getattr(settings, 'SLACK_WEBHOOK_URL', None)
		if slack_url:
			slack_data = {
				"text": f"New contact form submission:\n*Name:* {name}\n*Email:* {email}\n*Message:* {message}"
			}
			try:
				requests.post(slack_url, json=slack_data)
			except Exception as e:
				pass  # Optionally log error
		return Response({'status': 'Message sent!'}, status=status.HTTP_200_OK)
