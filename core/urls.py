from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from .views import (
    ClientViewSet,
    ProjectViewSet,
    TaskViewSet,
    TimeEntryViewSet,
    health,
    register,
)

router = DefaultRouter()
router.register(r"clients", ClientViewSet)
router.register(r"projects", ProjectViewSet)
router.register(r"tasks", TaskViewSet)
router.register(r"time-entries", TimeEntryViewSet)

urlpatterns = [
    path("health/", health),
    path("auth/register/", register),
    path("auth/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("", include(router.urls)),
]
