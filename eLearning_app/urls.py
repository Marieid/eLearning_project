from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
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
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
]
