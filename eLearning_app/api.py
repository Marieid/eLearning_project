from rest_framework import viewsets, permissions
from .models import User, elearnUser, Course, Material, Feedback, StatusUpdate, ChatRoom, Enrollment
from .serializers import UserSerializer, ElearnUserSerializer, CourseListSerializer, MaterialSerializer, FeedbackSerializer, StatusUpdateSerializer, ChatRoomSerializer, EnrollmentSerializer

# Custom permission class to allow only owners to update or delete objects


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
          # Allow read-only access for all
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
    permission_classes = [permissions.IsAuthenticated]


class ElearnUserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = elearnUser.objects.all()
    serializer_class = ElearnUserSerializer
    permission_classes = [permissions.IsAuthenticated]


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

# Allows for full CRUD operations for teachers


class MaterialViewSet(viewsets.ModelViewSet):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [
                permissions.IsAuthenticated, IsOwnerOrReadOnly]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]


class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [
                permissions.IsAuthenticated, IsOwnerOrReadOnly]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]


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


class EnrollmentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]
