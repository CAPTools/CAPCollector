"""URL mapping for core module."""

__author__ = "Arkadii Yakovets (arcadiy@google.com)"

from core import views
from django.conf.urls import url


urlpatterns = [
    url(r"^$", views.IndexView.as_view()),
    url(r"^feed.(?P<feed_type>(html|xml))$", views.FeedView.as_view(),
        name="feed"),
    url(r"^feed/(?P<alert_id>.*).(?P<feed_type>(html|xml))$",
        views.FeedView.as_view(), name="alert"),
    url(r"^post/$", views.PostView.as_view(), name="post"),
    url(r"^template/(?P<template_type>(area|message))/$",
        views.AlertTemplateView.as_view(), name="template"),
]

