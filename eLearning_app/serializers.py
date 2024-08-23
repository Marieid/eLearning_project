from rest_framework import serializers
from .models import User, elearnUser, Course, Material, Feedback, StatusUpdate, ChatRoom, Enrollment, EnrollmentNotification, MaterialNotification


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name',
                  'last_name', 'email', 'profile_picture']


class ElearnUserSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = elearnUser
        fields = ['user', 'user_type']


class CourseListSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(
        source='teacher.user.get_full_name', read_only=True)

    class Meta:
        model = Course
        # Adjust fields as needed
        fields = ['id', 'code', 'name', 'teacher_name']


class StatusUpdateSerializer(serializers.ModelSerializer):
    user = UserSerializer()  # Include user information in the serialized output

    class Meta:
        model = StatusUpdate
        fields = ['id', 'user', 'content', 'timestamp']


class ChatRoomSerializer(serializers.ModelSerializer):
    admin = UserSerializer()
    members = UserSerializer(many=True)  # Serialize the list of members

    class Meta:
        model = ChatRoom
        fields = ['id', 'chat_name', 'admin', 'members', 'chat_log']


class EnrollmentSerializer(serializers.ModelSerializer):
    student = ElearnUserSerializer()
    course = CourseListSerializer()

    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'course']


class EnrollmentNotificationSerializer(serializers.ModelSerializer):
    course = CourseListSerializer()
    student = ElearnUserSerializer()
    teacher = ElearnUserSerializer()

    class Meta:
        model = EnrollmentNotification
        fields = ['id', 'course', 'student', 'teacher', 'read']

# Get student's full name
class FeedbackSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(
        source='student.user.get_full_name', read_only=True)  

    class Meta:
        model = Feedback
        fields = ['id', 'student_name', 'rating',
                  'comment'] 

class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = ['id', 'name', 'description', 'file',
                  'upload_date', 'file_type']


class MaterialNotificationSerializer(serializers.ModelSerializer):
    material = MaterialSerializer()
    student = ElearnUserSerializer()

    class Meta:
        model = MaterialNotification
        fields = ['id', 'material', 'student', 'read']
