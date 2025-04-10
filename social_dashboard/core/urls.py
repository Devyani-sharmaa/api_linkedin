from django.urls import path
from . import views

urlpatterns = [
    path('linkedin/login/', views.linkedin_login),
    path('linkedin/callback/', views.linkedin_callback),
    path('linkedin/profile/', views.fetch_linkedin_profile),
    path('linkedin/post/', views.post_on_linkedin),
]
