from django.urls import path

from . import views

app_name = "user"

urlpatterns = [
  path("", views.hello_user, name="hello_user"),
  path("register/", views.register_view, name="register"),
  path("login/", views.login_view, name="login"),
  path("logout/", views.logout_view, name="logout"),
  path("profile/", views.profile_view, name="profile"),
]
