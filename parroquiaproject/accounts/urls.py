from django.urls import path
from .views import SignUpView, activate

app_name = "accounts"

urlpatterns = [
    path("signup/", SignUpView.as_view(), name="signup"),
    path("activate/<uidb64>/<token>/", activate, name="activate"),
]