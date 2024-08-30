from rest_framework import serializers
from eLearning_app.models import User, elearnUser, Course, Material, Feedback, StatusUpdate, ChatRoom, Enrollment, EnrollmentNotification, MaterialNotification


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
    # Include description for more context
    description = serializers.CharField(read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'code', 'name', 'teacher_name',
                  'description', 'start_date', 'end_date']


class CourseDetailSerializer(serializers.ModelSerializer):
    teacher = ElearnUserSerializer(read_only=True)
    students = ElearnUserSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'code', 'name', 'description', 'teacher',
                  'students', 'start_date', 'end_date', 'enrollment_status']


class StatusUpdateSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = StatusUpdate
        fields = ['id', 'user', 'content', 'timestamp']


class ChatRoomSerializer(serializers.ModelSerializer):
    admin = UserSerializer()
    members = UserSerializer(many=True)

    class Meta:
        model = ChatRoom
        fields = ['id', 'chat_name', 'admin', 'members']


class EnrollmentSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(
        queryset=elearnUser.objects.all())
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())

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


class FeedbackSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(
        source='student.user.get_full_name', read_only=True)
    course_name = serializers.SerializerMethodField()

    class Meta:
        model = Feedback
        fields = ['id', 'student_name', 'course_name',
                  'rating', 'comment']

    def get_course_name(self, obj):
        return obj.course.name


class MaterialSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(
        source='course.name', read_only=True)  # Include course name
    uploader_name = serializers.CharField(
        source='uploader.user.get_full_name', read_only=True)
    uploader_type = serializers.CharField(
        source='uploader.user_type', read_only=True)

    class Meta:
        model = Material
        fields = ['id', 'name', 'description', 'file', 'upload_date',
                  'file_type', 'course_name', 'uploader_name', 'uploader_type']


class MaterialNotificationSerializer(serializers.ModelSerializer):
    material = MaterialSerializer()
    student = ElearnUserSerializer()

    class Meta:
        model = MaterialNotification
        fields = ['id', 'material', 'student', 'read']
