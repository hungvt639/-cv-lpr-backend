from django.urls import path
from .views import cv
urlpatterns = [
    path("cv", cv.CVView.as_view()),
]
