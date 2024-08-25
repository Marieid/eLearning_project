from rest_framework import viewsets, permissions, mixins
from rest_framework.exceptions import PermissionDenied
from .models import User, elearnUser, Course, Material, Feedback, StatusUpdate, ChatRoom, Enrollment
from .serializers import UserSerializer, ElearnUserSerializer, CourseListSerializer, MaterialSerializer, FeedbackSerializer, StatusUpdateSerializer, ChatRoomSerializer, EnrollmentSerializer

# Custom permission class to allow only owners to update or delete objects


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Allow read-only access for everyone
        if request.method in permissions.SAFE_METHODS:
            return True
        # Allow write access only to the owner
        return obj.user == request.user


class IsTeacherOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        # Check if the user has an elearnUser object and is a teacher
        return hasattr(request.user, 'elearnuser') and request.user.elearnuser.user_type == 'teacher'


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]


class ElearnUserViewSet(viewsets.ModelViewSet):
    queryset = elearnUser.objects.all()
    serializer_class = ElearnUserSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]


# Allow full CRUD for teachers, read-only for students
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
        # Ensure that only teachers can create a course
        if hasattr(self.request.user, 'elearnuser') and self.request.user.elearnuser.user_type == 'teacher':
            serializer.save(teacher=self.request.user.elearnuser)
        else:
            raise PermissionDenied("Only teachers can create courses.")


# Allows for full CRUD operations for all logged in users


class MaterialViewSet(viewsets.ModelViewSet):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer

    def get_permissions(self):
        # Allow everyone to read, but restrict create/update/delete to owners
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [
                permissions.IsAuthenticated, IsOwnerOrReadOnly]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        # Automatically set the user as the owner of the material
        serializer.save(user=self.request.user)


class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer

    def get_permissions(self):
        # Allow read-only access to teachers
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [
                permissions.IsAuthenticated, IsOwnerOrReadOnly]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        # Ensure that only students can create feedback
        if hasattr(self.request.user, 'elearnuser') and self.request.user.elearnuser.user_type == 'student':
            serializer.save(user=self.request.user)
        else:
            raise PermissionDenied("Only students can give feedback.")

    def perform_update(self, serializer):
        # Ensure that only the owner (and only if they are a student) can update feedback
        if hasattr(self.request.user, 'elearnuser') and self.request.user.elearnuser.user_type == 'student':
            serializer.save()
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
        # Prevent teachers from enrolling in courses
        if hasattr(self.request.user, 'elearnuser') and self.request.user.elearnuser.user_type == 'teacher':
            raise PermissionDenied("Teachers cannot enroll in courses.")
            # Assuming you're getting course_pk from URL
            course_id = self.kwargs.get('course_pk')
            course = get_object_or_404(Course, pk=course_id)
            serializer.save(
                student=self.request.user.elearnuser, course=course)
