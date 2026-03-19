
from django.db import models

class Skill(models.Model):
	name = models.CharField(max_length=100, unique=True)
	icon = models.CharField(max_length=100, default='default.svg')  # store icon filename or class
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.name


class PortfolioProfile(models.Model):
	profile_photo = models.ImageField(upload_to='profile/', blank=True, null=True)
	updated_at = models.DateTimeField(auto_now=True)

	def save(self, *args, **kwargs):
		# Keep this model as a single editable profile record in admin.
		self.pk = 1
		super().save(*args, **kwargs)

	@classmethod
	def load(cls):
		obj, _ = cls.objects.get_or_create(pk=1)
		return obj

	def __str__(self):
		return 'Portfolio Profile'

class Project(models.Model):
	title = models.CharField(max_length=200)
	description = models.TextField()
	tech_stack = models.JSONField(default=list)
	thumbnail_image = models.ImageField(upload_to='projects/thumbnails/')
	image_two = models.ImageField(upload_to='projects/gallery/', blank=True, null=True)
	image_three = models.ImageField(upload_to='projects/gallery/', blank=True, null=True)
	video_url = models.URLField(blank=True, null=True)
	live_demo_link = models.URLField(blank=True, null=True)
	github_link = models.URLField(blank=True, null=True)
	date_created = models.DateField(auto_now_add=True)

	def __str__(self):
		return self.title

class Quest(models.Model):
	STATUS_CHOICES = [
		('Hypothesis', 'Hypothesis'),
		('In-Lab', 'In-Lab'),
		('Published', 'Published'),
	]
	task_name = models.CharField(max_length=200)
	status = models.CharField(max_length=20, choices=STATUS_CHOICES)
	description = models.TextField(blank=True)
	upvotes = models.PositiveIntegerField(default=0)

	def __str__(self):
		return self.task_name

class Resume(models.Model):
	DOCUMENT_TYPES = [
		('cv', 'CV'),
		('resume', 'Resume'),
		('cover_letter', 'Cover Letter'),
	]
	title = models.CharField(max_length=120, blank=True)
	doc_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES, default='resume')
	file = models.FileField(upload_to='credentials/')
	uploaded_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		label = dict(self.DOCUMENT_TYPES).get(self.doc_type, self.doc_type)
		return f"{label} uploaded at {self.uploaded_at}"


class CredentialDownloadRequest(models.Model):
	STATUS_CHOICES = [
		('pending', 'Pending'),
		('sent', 'Sent'),
		('failed', 'Failed'),
	]

	full_name = models.CharField(max_length=120, blank=True)
	email = models.EmailField()
	document_type = models.CharField(max_length=20, choices=Resume.DOCUMENT_TYPES)
	consent_given = models.BooleanField(default=False)
	ip_address = models.GenericIPAddressField(blank=True, null=True)
	user_agent = models.CharField(max_length=255, blank=True)
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
	status_message = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.email} requested {self.document_type} ({self.status})"
