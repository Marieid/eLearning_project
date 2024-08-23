from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.contrib.auth.views import LogoutView
from rest_framework_simplejwt.views import TokenObtainPairView
from . import views
from . import api

router = DefaultRouter()
router.register(r'users', api.UserViewSet)
router.register(r'elearnusers', api.ElearnUserViewSet)
router.register(r'courses', api.CourseViewSet)
router.register(r'materials', api.MaterialViewSet)
router.register(r'feedbacks', api.FeedbackViewSet)
router.register(r'statusupdates', api.StatusUpdateViewSet)
router.register(r'chatrooms', api.ChatRoomViewSet)
router.register(r'enrollments', api.EnrollmentViewSet)

urlpatterns = [
    # Include the API URLs
    path('api/', include(router.urls)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # Elearning app site URLs
    path('', views.index, name='index'),
    path('register/student/', views.register_student, name='register_student'),
    path('register/teacher/', views.register_teacher, name='register_teacher'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('accounts/profile/', views.profile, name='profile'),
    path('course/create/', views.create_course, name='create_course'),
    path('course/<int:course_id>/edit/', views.edit_course, name='edit_course'),
    path('course/<int:course_id>/delete/',
         views.delete_course, name='delete_course'),
    path('courses/', views.course_list, name='course_list'),
    path('course/<int:course_id>/close_enrollment/',
         views.close_enrollment, name='close_enrollment'),
    path('course/<int:course_id>/open_enrollment/',
         views.open_enrollment, name='open_enrollment'),
    path('course/<int:course_id>/enroll/',
         views.enroll_in_course, name='enroll_in_course'),
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    path('course/<int:course_id>/add_material/',
         views.add_material, name='add_material'),
    path('course/<int:course_id>/edit_material/<int:material_id>/',
         views.edit_material, name='edit_material'),
    path('course/<int:course_id>/delete_material/<int:material_id>/',
         views.delete_material, name='delete_material'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('course/<int:course_id>/submit_feedback/',
         views.submit_feedback, name='submit_feedback'),
    path('post_status_update/', views.post_status_update,
         name='post_status_update'),
    path('status_update/<int:status_update_id>/edit/',
         views.edit_status_update, name='edit_status_update'),
    path('status_update/<int:status_update_id>/delete/',
         views.delete_status_update, name='delete_status_update'),
    path('chat-rooms/', views.chat_rooms, name='chat_rooms'),
    path('chat/<str:room_name>/', views.chat_room_detail, name='chat_room_detail'),
    path('notification/<int:notification_id>/mark_as_read/',
         views.mark_notification_as_read, name='mark_notification_as_read'),
]
