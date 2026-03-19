# API URLs for portfolioapi
from django.urls import path

from .views import ProjectListView, QuestListView, QuestUpvoteView, ContactView, SkillListCreateView, CredentialRequestView, PortfolioProfileView

urlpatterns = [
    path('projects', ProjectListView.as_view(), name='project-list'),
    path('quests', QuestListView.as_view(), name='quest-list'),
    path('quests/vote', QuestUpvoteView.as_view(), name='quest-upvote'),
    path('contact', ContactView.as_view(), name='contact'),
    path('skills', SkillListCreateView.as_view(), name='skill-list-create'),
    path('profile', PortfolioProfileView.as_view(), name='profile'),
    path('credentials/request', CredentialRequestView.as_view(), name='credential-request'),
]
