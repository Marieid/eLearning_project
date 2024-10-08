from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.urls import path, include
from rest_framework import permissions
from rest_framework.routers import DefaultRouter
from . import views

schema_view = get_schema_view(
    openapi.Info(
        title="Elearning App API",
        default_version='v1',
        description="CM3035 - Advanced web development -- Final project",
        terms_of_service="https://www.google.com/policies/terms/",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'elearnusers', views.ElearnUserViewSet)
router.register(r'courses', views.CourseViewSet)
router.register(r'materials', views.MaterialViewSet)
router.register(r'feedbacks', views.FeedbackViewSet)
router.register(r'statusupdates', views.StatusUpdateViewSet)
router.register(r'chatrooms', views.ChatRoomViewSet)
router.register(r'enrollments', views.EnrollmentViewSet)
router.register(r'enrollmentnotifications',
                views.EnrollmentNotificationViewSet)
router.register(r'materialnotifications', views.MaterialNotificationViewSet)
router.register(r'blocknotifications', views.BlockNotificationViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

# Swagger UI
urlpatterns += [
    path('swagger/', schema_view.with_ui('swagger',
         cache_timeout=0), name='schema-swagger-ui'),
]
