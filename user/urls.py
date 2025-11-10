from django.urls import path
from . import views

app_name = "user"

urlpatterns = [
  path("", views.hello_user, name="hello_user"),
]
