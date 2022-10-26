from django.urls import include, path

from . import views
from api.urls_v1 import v1

urlpatterns = [
    path('v1/', include(v1.urls)),
    path('v1/auth/signup/', views.SignupView.as_view(), name="signup"),
    path('v1/auth/token/', views.RefreshTokenView.as_view(), name="token")
]
