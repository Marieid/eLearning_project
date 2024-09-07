from rest_framework import viewsets, permissions, mixins, filters
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from eLearning_app.models import User, elearnUser, Course, Material, Feedback, StatusUpdate, ChatRoom, Enrollment, EnrollmentNotification, MaterialNotification, BlockNotification
from .serializers import UserSerializer, ElearnUserSerializer, CourseListSerializer, MaterialSerializer, FeedbackSerializer, StatusUpdateSerializer, ChatRoomSerializer, EnrollmentSerializer, EnrollmentNotificationSerializer, MaterialNotificationSerializer, BlockNotificationSerializer

# Custom permission class to allow only owners to update or delete objects


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        # Check if obj has a 'user' attribute before accessing it
        if hasattr(obj, 'user'):
            return obj.user == request.user
        else:
            return False

# Custom permission class to allow only owners or admin to retrieve user details


class IsSelfOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj == request.user or request.user.is_staff


class IsTeacherOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        # Checks if the user has an elearnUser object and is a teacher
        return hasattr(request.user, 'elearnuser') and request.user.elearnuser.user_type == 'teacher'


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == 'list':
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated, IsSelfOrAdmin]
        return [permission() for permission in permission_classes]


class ElearnUserViewSet(viewsets.ModelViewSet):
    queryset = elearnUser.objects.all()
    serializer_class = ElearnUserSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]


# Allows full CRUD for teachers, read-only for students
class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseListSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [
                permissions.IsAuthenticated, IsTeacherOrReadOnly]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        # Ensures that only teachers can create a course
        if hasattr(self.request.user, 'elearnuser') and self.request.user.elearnuser.user_type == 'teacher':
            serializer.save(teacher=self.request.user.elearnuser)
        else:
            raise PermissionDenied("Only teachers can create courses.")

    def get_queryset(self):
        if self.request.user.elearnuser.user_type == 'teacher':
            return Course.objects.filter(teacher=self.request.user.elearnuser)
        else:  # Student
            return Course.objects.filter(enrollment_status='open')

# Allows for full CRUD operations for all logged in users


class MaterialViewSet(viewsets.ModelViewSet):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        # Allows everyone to read, but restrict create/update/delete to owners
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [
                permissions.IsAuthenticated, IsOwnerOrReadOnly]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        # Automatically sets the user as the owner of the material
        serializer.save(uploader=self.request.user.elearnuser)

    def get_queryset(self):
        if self.request.user.elearnuser.user_type == 'teacher':
            return Material.objects.all()
        else:
            return Material.objects.filter(
                # Materials for courses the student is enrolled in
                Q(course__students=self.request.user.elearnuser) |
                # Materials uploaded by the student
                Q(uploader=self.request.user.elearnuser))


class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer

    def get_permissions(self):
        # Allows read-only access to teachers
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [
                permissions.IsAuthenticated, IsOwnerOrReadOnly]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        # Ensures that only students can create feedback
        if hasattr(self.request.user, 'elearnuser') and self.request.user.elearnuser.user_type == 'student':
            serializer.save(student=self.request.user.elearnuser)
        else:
            raise PermissionDenied("Only students can give feedback.")

    def perform_update(self, serializer):
        # Ensure that only the owner (and only if they are a student) can update feedback
        if hasattr(self.request.user, 'elearnuser') and self.request.user.elearnuser.user_type == 'student':
            serializer.save(student=self.request.user.elearnuser)
        else:
            raise PermissionDenied("Only students can edit their feedback.")

    def perform_destroy(self, instance):
        # Ensures that only the owner (and only if they are a student) can delete feedback
        if hasattr(self.request.user, 'elearnuser') and self.request.user.elearnuser.user_type == 'student':
            instance.delete()
        else:
            raise PermissionDenied("Only students can delete their feedback.")


class StatusUpdateViewSet(viewsets.ModelViewSet):
    queryset = StatusUpdate.objects.all()
    serializer_class = StatusUpdateSerializer
    # Only owners can update/delete
    permission_classes = [permissions.IsAuthenticated,
                          IsOwnerOrReadOnly]


class ChatRoomViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]


class EnrollmentViewSet(mixins.CreateModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.ListModelMixin,
                        viewsets.GenericViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        if self.request.user.elearnuser.user_type == 'teacher':
            raise PermissionDenied("Teachers cannot enroll in courses.")

        course_id = self.kwargs.get('course_pk')
        course = get_object_or_404(Course, pk=course_id)
        serializer.save(student=self.request.user.elearnuser, course=course)


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['name', 'code']
    search_fields = ['name']


class EnrollmentNotificationViewSet(viewsets.ModelViewSet):
    queryset = EnrollmentNotification.objects.all()
    serializer_class = EnrollmentNotificationSerializer
    permission_classes = [permissions.IsAuthenticated]


class MaterialNotificationViewSet(viewsets.ModelViewSet):
    queryset = MaterialNotification.objects.all()
    serializer_class = MaterialNotificationSerializer
    permission_classes = [permissions.IsAuthenticated]


class BlockNotificationViewSet(viewsets.ModelViewSet):
    queryset = BlockNotification.objects.all()
    serializer_class = BlockNotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
