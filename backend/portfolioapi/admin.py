
from django.contrib import admin
from .models import Project, Quest, Resume, Skill, CredentialDownloadRequest, PortfolioProfile

admin.site.register(Project)
admin.site.register(Quest)
admin.site.register(Resume)
admin.site.register(Skill)
admin.site.register(CredentialDownloadRequest)


@admin.register(PortfolioProfile)
class PortfolioProfileAdmin(admin.ModelAdmin):
	list_display = ('updated_at',)

	def has_add_permission(self, request):
		# Keep only one profile row editable from admin.
		exists = PortfolioProfile.objects.exists()
		if exists:
			return False
		return super().has_add_permission(request)
