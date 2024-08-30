from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'elearnusers', views.ElearnUserViewSet)
router.register(r'courses', views.CourseViewSet)
router.register(r'materials', views.MaterialViewSet)
router.register(r'feedbacks', views.FeedbackViewSet)
router.register(r'statusupdates', views.StatusUpdateViewSet)
router.register(r'chatrooms', views.ChatRoomViewSet)
router.register(r'enrollments', views.EnrollmentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
