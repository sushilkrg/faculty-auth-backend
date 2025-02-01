# api/urls.py

from django.urls import path
from .views import FacultyList, FacultyDetail, FaceAuthenticationView

urlpatterns = [
    path('faculties/', FacultyList.as_view(), name='faculty-list'),
    path('faculties/<str:pk>/', FacultyDetail.as_view(), name='faculty-detail'),
    path('authenticate/', FaceAuthenticationView.as_view(), name='face-authenticate'),
]
