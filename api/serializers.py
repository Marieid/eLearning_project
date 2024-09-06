from rest_framework import serializers
from eLearning_app.models import User, elearnUser, Course, Material, Feedback, StatusUpdate, ChatRoom, Enrollment, EnrollmentNotification, MaterialNotification


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model, including basic user information."""
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name',
                  'last_name', 'email', 'profile_picture']


class ElearnUserSerializer(serializers.ModelSerializer):
    """Serializer for the elearnUser model, including nested UserSerializer for user details."""
    user = UserSerializer()

    class Meta:
        model = elearnUser
        fields = ['user', 'user_type']


class CourseListSerializer(serializers.ModelSerializer):
    """Serializer for listing courses, including teacher name and description."""
    teacher_name = serializers.CharField(
        source='teacher.user.get_full_name', read_only=True)
    description = serializers.CharField(
        read_only=True)  # Provide course description

    class Meta:
        model = Course
        fields = ['id', 'code', 'name', 'teacher_name',
                  'description', 'start_date', 'end_date']


class CourseDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed course view, including teacher and student details."""
    teacher = ElearnUserSerializer(read_only=True)
    students = ElearnUserSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'code', 'name', 'description', 'teacher',
                  'students', 'start_date', 'end_date', 'enrollment_status']


class StatusUpdateSerializer(serializers.ModelSerializer):
    """Serializer for status updates, including user details."""
    user = UserSerializer()

    class Meta:
        model = StatusUpdate
        fields = ['id', 'user', 'content', 'timestamp']


class ChatRoomSerializer(serializers.ModelSerializer):
    """Serializer for chat rooms, including admin and members."""
    admin = UserSerializer()
    members = UserSerializer(many=True)

    class Meta:
        model = ChatRoom
        fields = ['id', 'chat_name', 'admin', 'members']


class EnrollmentSerializer(serializers.ModelSerializer):
    """Serializer for course enrollments, linking students and courses."""
    student = serializers.PrimaryKeyRelatedField(
        queryset=elearnUser.objects.all())
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())

    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'course']


class EnrollmentNotificationSerializer(serializers.ModelSerializer):
    """Serializer for enrollment notifications, including course and user details."""
    course = CourseListSerializer()
    student = ElearnUserSerializer()
    teacher = ElearnUserSerializer()

    class Meta:
        model = EnrollmentNotification
        fields = ['id', 'course', 'student', 'teacher', 'read']


class FeedbackSerializer(serializers.ModelSerializer):
    """Serializer for feedback, including student name and course name."""
    student_name = serializers.CharField(
        source='student.user.get_full_name', read_only=True)
    course_name = serializers.SerializerMethodField()

    class Meta:
        model = Feedback
        fields = ['id', 'student_name', 'course_name', 'rating', 'comment']

    def get_course_name(self, obj):
        """Retrieve the name of the course for feedback."""
        return obj.course.name


class MaterialSerializer(serializers.ModelSerializer):
    """Serializer for materials, including course name and uploader details."""
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
    """Serializer for material notifications, including material and student details."""
    material = MaterialSerializer()
    student = ElearnUserSerializer()

    class Meta:
        model = MaterialNotification
        fields = ['id', 'material', 'student', 'read']
