
from django.db import models

class Skill(models.Model):
	name = models.CharField(max_length=100, unique=True)
	icon = models.CharField(max_length=100, default='default.svg')  # store icon filename or class
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.name


from django.db import models

class Project(models.Model):
	title = models.CharField(max_length=200)
	description = models.TextField()
	tech_stack = models.JSONField(default=list)
	thumbnail_image = models.ImageField(upload_to='projects/thumbnails/')
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
	file = models.FileField(upload_to='resume/')
	uploaded_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"Resume uploaded at {self.uploaded_at}"
