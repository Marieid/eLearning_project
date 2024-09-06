from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from .models import User, elearnUser, Course, Enrollment, Material, StatusUpdate, ChatRoom, Message, EnrollmentNotification, MaterialNotification
from .forms import StudentRegistrationForm, TeacherRegistrationForm, CourseCreationForm, UserProfileUpdateForm, MaterialForm, FeedbackForm, StatusUpdateForm, ChatRoomForm
from django.contrib.auth.decorators import permission_required
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.template.loader import render_to_string


def index(request):
    return render(request, 'eLearning_app/index.html')


def register_student(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            messages.success(
                request, "Registration successful! Please log in.")
            return redirect('login')
    else:
        form = StudentRegistrationForm()
    return render(request, 'eLearning_app/register_student.html', {'form': form})


def register_teacher(request):
    if request.method == 'POST':
        form = TeacherRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            messages.success(
                request, "Registration successful! Please log in.")
            return redirect('login')

    else:
        form = TeacherRegistrationForm()
    return render(request, 'eLearning_app/register_teacher.html', {'form': form})


class CustomLoginView(LoginView):
    template_name = 'eLearning_app/login.html'


@login_required
def profile(request):
    context = {'user': request.user}

    if hasattr(request.user, 'elearnuser'):
        if request.user.elearnuser.user_type == 'student':
            enrolled_courses = request.user.elearnuser.enrolled_courses.all()
            context['enrolled_courses'] = enrolled_courses
         # Fetch unread enrollment and material notifications for the student user
            enrollment_notifications = EnrollmentNotification.objects.filter(
                student=request.user.elearnuser, read=False)
            material_notifications = MaterialNotification.objects.filter(
                student=request.user.elearnuser, read=False)
            context['enrollment_notifications'] = enrollment_notifications
            context['material_notifications'] = material_notifications
        elif request.user.elearnuser.user_type == 'teacher':
            courses_taught = Course.objects.filter(
                teacher=request.user.elearnuser)
            context['courses_taught'] = courses_taught
            # Fetch unread enrollment notifications for the teacher user
            enrollment_notifications = EnrollmentNotification.objects.filter(
                teacher=request.user.elearnuser, read=False)
            context['enrollment_notifications'] = enrollment_notifications

    context['chat_rooms'] = ChatRoom.objects.filter(members=request.user)
    context['status_update_form'] = StatusUpdateForm()
    return render(request, 'eLearning_app/profile.html', context)


@ login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserProfileUpdateForm(
            request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
   # Redirect back to the profile page
    else:
        form = UserProfileUpdateForm(instance=request.user)
    return render(request, 'eLearning_app/edit_profile.html', {'form': form})


@ permission_required('eLearning_app.add_course')
def create_course(request):
    print('user: ' + str(request.user.elearnuser.user_type))
    if not hasattr(request.user, 'elearnuser') or request.user.elearnuser.user_type != 'teacher':
        messages.error(request, "Only teachers can create courses.")

        return redirect('index')

    if request.method == 'POST':
        form = CourseCreationForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.teacher = request.user.elearnuser
            course.save()
            messages.success(request, "Course created successfully!")

            return redirect('course_detail', course_id=course.id)
    else:
        form = CourseCreationForm()
    return render(request, 'eLearning_app/create_course.html', {'form': form})


def course_list(request):
    courses = Course.objects.filter(enrollment_status='open')
    if request.user.is_authenticated and hasattr(request.user, 'elearnuser') and request.user.elearnuser.user_type == 'student':
        enrolled_courses = request.user.elearnuser.enrolled_courses.all()
        print('course list, enrolled students: ' + str(enrolled_courses))
    else:
        enrolled_courses = []

    return render(request, 'eLearning_app/course_list.html', {'courses': courses, 'enrolled_courses': enrolled_courses})


def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if hasattr(request.user, 'elearnuser'):
        if request.user.elearnuser.user_type == 'teacher':
            materials = Material.objects.filter(course=course)
        else:  # Student
            materials = Material.objects.filter(Q(course=course, uploader=course.teacher) | Q(
                course=course, uploader=request.user.elearnuser))
    else:  # User has no elearnuser object
        # Only show teacher-uploaded materials
        materials = Material.objects.filter(
            course=course, uploader=course.teacher)
    # Check if enrollment just happened
    if request.method == 'POST' and 'enroll' in request.POST:
        # Call enroll_in_course view to handle enrollment
        enroll_in_course(request, course_id)

    # Fetch enrolled students and add to context
    enrolled_students = course.students.all()
    print('enrolled students: ' + str(enrolled_students))

    context = {
        'course': course,
        'materials': materials,
        'enrolled_students': enrolled_students,
        'feedback_form': FeedbackForm(),
        'teacher': course.teacher,  # Add this line
    }
    return render(request, 'eLearning_app/course_detail.html', context)


@login_required
@permission_required('eLearning_app.change_course')
def edit_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if course.teacher != request.user.elearnuser:
        messages.error(request, "You are not authorized to edit this course.")
        return redirect('course_detail', course_id=course.id)

    if request.method == 'POST':
        form = CourseCreationForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, "Course updated successfully!")
            return redirect('course_detail', course_id=course.id)
    else:
        form = CourseCreationForm(instance=course)
        return render(request, 'eLearning_app/edit_course.html', {'form': form, 'course': course})


@login_required
@permission_required('eLearning_app.delete_course')
def delete_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    # Checks if the user is the teacher of the course
    if course.teacher != request.user.elearnuser:
        messages.error(
            request, "You are not authorized to delete this course.")
        return redirect('course_detail', course_id=course.id)

    if request.method == 'POST':
        course.delete()
        messages.success(request, 'Course deleted successfully!')
        # Redirect to course list
        return redirect('course_list')

    # If GET request, render confirmation page
    return render(request, 'eLearning_app/delete_course.html', {'course': course})


@ permission_required('eLearning_app.view_course')
def enroll_in_course(request, course_id):
    if not request.user.is_authenticated:
        return redirect(f'/login/?next=/course/{course_id}/enroll/')
    if not request.user.elearnuser.user_type == 'student':
        messages.error(request, "Only students can enroll in courses.")
        return redirect('profile')
    try:
        course = Course.objects.get(id=course_id, enrollment_status='open')

    except Course.DoesNotExist:
        messages.error(request, "Course not found or enrollment is closed.")
        return redirect('course_list')

    # Use elearnUser for student
    print('user: ' + str(request.user.elearnuser))
    print('course: ' + str(course))

    enrollment = Enrollment.objects.create(
        student=request.user.elearnuser, course=course)

    def update_course_students():
        # Refresh the course's students ManyToManyField
        course.students.add(request.user.elearnuser)

     # Execute after the transaction is committed
    transaction.on_commit(update_course_students)
    messages.success(request, "Enrolled in course successfully!")
    return redirect('course_detail', course_id=course.id)


@login_required
@permission_required('eLearning_app.change_course')
def close_enrollment(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if course.teacher != request.user.elearnuser:
        messages.error(
            request, "You are not authorized to close enrollment for this course.")
        return redirect('course_detail', course_id=course.id)

    if request.method == 'POST':
        course.enrollment_status = 'closed'
        course.save()
        messages.success(request, "Enrollment closed for this course.")
        return redirect('course_detail', course_id=course.id)
    else:
        return render(request, 'eLearning_app/close_enrollment.html', {'course': course})


@ login_required
@ permission_required('eLearning_app.change_course')
def open_enrollment(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if course.teacher != request.user.elearnuser:
        messages.error(
            request, "You are not authorized to open enrollment for this course.")
        return redirect('course_detail', course_id=course.id)

    if request.method == 'POST':
        course.enrollment_status = 'open'
        course.save()
        messages.success(request, "Enrollment reopened for this course.")
        return redirect('course_detail', course_id=course.id)
    return render(request, 'eLearning_app/open_enrollment.html', {'course': course})


@login_required
@permission_required('eLearning_app.add_material')
def add_material(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == 'POST':
        form = MaterialForm(request.POST, request.FILES)
        if form.is_valid():
            material = form.save(commit=False)
            material.course = course
            material.uploader = request.user.elearnuser
            print('Uploader: ' + str(material.uploader))
            material.save()
            messages.success(request, 'Material added successfully!')
            return redirect('course_detail', course_id=course_id)
    else:
        form = MaterialForm(initial={'uploader': request.user.elearnuser})

    return render(request, 'eLearning_app/add_material.html', {'form': form, 'course': course})


@login_required
@permission_required('eLearning_app.change_material')
def edit_material(request, course_id, material_id):
    material = get_object_or_404(Material, id=material_id, course_id=course_id)

    if request.method == 'POST':
        form = MaterialForm(request.POST, request.FILES,
                            instance=material)
        if form.is_valid():
            material.uploader = request.user.elearnuser
            form.save()
            messages.success(request, 'Material updated successfully!')
            return redirect('course_detail', course_id=course_id)
    else:
        form = MaterialForm(instance=material)

    return render(request, 'eLearning_app/edit_material.html', {'form': form, 'course': material.course})


@login_required
@permission_required('eLearning_app.delete_material')
def delete_material(request, course_id, material_id):
    material = get_object_or_404(Material, id=material_id, course_id=course_id)

    if request.method == 'POST':
        material.delete()
        messages.success(request, 'Material deleted successfully!')
        return redirect('course_detail', course_id=course_id)

    return render(request, 'eLearning_app/delete_material.html', {'material': material, 'course_id': course_id})


@login_required
# Student can add feedback
@permission_required('eLearning_app.add_feedback')
def submit_feedback(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if not request.user.elearnuser.user_type == 'student':
        messages.error(request, "Only students can submit feedback.")
        return redirect('course_detail', course_id=course_id)

    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.student = request.user.elearnuser

            feedback.course = course
            feedback.save()
            messages.success(request, 'Feedback submitted successfully!')
            # Redirect back to the course detail page
            return redirect('course_detail', course_id=course_id)
    else:
        form = FeedbackForm()

    return render(request, 'eLearning_app/submit_feedback.html', {'form': form, 'course': course})


@login_required
def post_status_update(request):
    if request.method == 'POST':
        print("POST request received")  # Check if POST data is received
        form = StatusUpdateForm(request.POST)
        if form.is_valid():
            status_update = form.save(commit=False)
            status_update.user = request.user
            status_update.save()

            rendered_status_update = render_to_string(
                'eLearning_app/status_update.html',
                {'status_update': status_update}
            )

            return JsonResponse({'html': rendered_status_update}, status=200)
        else:
            # Debug invalid form
            print("Form is invalid")
            return JsonResponse({'error': 'Invalid form data'}, status=400)
            # Debug non-POST requests
    print("Invalid request method")
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def edit_status_update(request, status_update_id):
    status_update = get_object_or_404(StatusUpdate, id=status_update_id)

    if status_update.user != request.user:
        messages.error(
            request, "You are not authorized to edit this status update.")
        return redirect('profile')

    if request.method == 'POST':
        form = StatusUpdateForm(request.POST, instance=status_update)
        if form.is_valid():
            form.save()
            messages.success(request, 'Status update edited successfully!')
            return redirect('profile')
    else:
        form = StatusUpdateForm(instance=status_update)

    return render(request, 'eLearning_app/edit_status_update.html', {'form': form, 'status_update': status_update})


@login_required
def delete_status_update(request, status_update_id):
    status_update = get_object_or_404(StatusUpdate, id=status_update_id)

    if status_update.user != request.user:
        messages.error(
            request, "You are not authorized to delete this status update.")
        return redirect('profile')

    if request.method == 'POST':
        status_update.delete()
        messages.success(request, 'Status update deleted successfully!')
        return redirect('profile')

    return render(request, 'eLearning_app/delete_status_update.html', {'status_update': status_update})


def chat_room_detail(request, room_name):
    chat_room = get_object_or_404(ChatRoom, chat_name=room_name)
    messages = Message.objects.filter(
        chat_room=chat_room).order_by('timestamp')
    return render(request, 'eLearning_app/chat_room_detail.html', {
        'room_name': room_name,
        'messages': messages,
        'chat_room': chat_room
    })


@login_required
def edit_chatroom(request, pk):
    chatroom = get_object_or_404(ChatRoom, pk=pk)

    if request.user != chatroom.admin:
        messages.error(
            request, "You are not authorized to edit this chat room.")
        return redirect('chat_rooms')

    if request.method == 'POST':
        form = ChatRoomForm(request.POST, instance=chatroom)
        if form.is_valid():
            form.save()
            messages.success(request, "Chat room updated successfully.")
            return redirect('chat_rooms')
    else:
        form = ChatRoomForm(instance=chatroom)

    return render(request, 'eLearning_app/edit_chatroom.html', {'form': form})


@login_required
def delete_chatroom(request, pk):
    chatroom = get_object_or_404(ChatRoom, pk=pk)

    if request.user != chatroom.admin:
        messages.error(
            request, "You are not authorized to delete this chat room.")
        return redirect('chat_rooms')

    if request.method == 'POST':
        chatroom.delete()
        messages.success(request, "Chat room deleted successfully.")
        return redirect('chat_rooms')

    return render(request, 'eLearning_app/delete_chatroom.html', {'chatroom': chatroom})


@login_required
def chat_rooms(request):
    if request.method == 'POST':
        form = ChatRoomForm(request.POST)
        if form.is_valid():
            chat_room = form.save(commit=False)
            chat_room.admin = request.user
            chat_room.save()
            chat_room.members.add(request.user)
            return redirect('chat_room_detail', room_name=chat_room.chat_name)
        else:
            # Print form errors for debugging
            print(form.errors)
    else:
        form = ChatRoomForm()

    chat_rooms = ChatRoom.objects.all()
    return render(request, 'eLearning_app/chat_rooms.html', {
        'chat_rooms': chat_rooms,
        'form': form
    })


@login_required
def mark_notification_as_read(request, notification_id):
    try:
        # Try to get EnrollmentNotification first
        notification = EnrollmentNotification.objects.get(
            id=notification_id, teacher=request.user.elearnuser)
    except EnrollmentNotification.DoesNotExist:
        # If not found, try to get MaterialNotification
        try:
            notification = MaterialNotification.objects.get(
                id=notification_id, student=request.user.elearnuser)
        except MaterialNotification.DoesNotExist:
            messages.error(request, 'Notification not found.')
            return redirect('profile')

    notification.read = True
    notification.save()
    messages.success(request, 'Notification marked as read.')
    return redirect('profile')


@login_required
def search_users(request):
    query = request.GET.get('q')
    if query:
        users = User.objects.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )

        # Also search within elearnUser (case-insensitive)
        elearn_users = elearnUser.objects.filter(
            # Case-insensitive search on username
            Q(user__username__iexact=query) |
            Q(user__first_name__iexact=query) |
            Q(user__last_name__iexact=query)
        )

        # Combines results and remove duplicates
        users = list(users) + [eu.user for eu in elearn_users]
        users = list({u.id: u for u in users}.values())
    else:
        users = []

    return render(request, 'eLearning_app/search_results.html', {'users': users})


def view_other_user_profile(request, user_id):
    user = get_object_or_404(User, id=user_id)

    context = {'profile_user': user}

    if hasattr(user, 'elearnuser'):
        if user.elearnuser.user_type == 'student':
            enrolled_courses = user.elearnuser.enrolled_courses.all()
            context['enrolled_courses'] = enrolled_courses

        elif user.elearnuser.user_type == 'teacher':
            courses_taught = Course.objects.filter(teacher=user.elearnuser)
            context['courses_taught'] = courses_taught

    return render(request, 'eLearning_app/other_user_profile.html', context)


@login_required
def user_profile_detail(request, user_id):
    user = get_object_or_404(User, id=user_id)
    context = {'profile_user': user}

    if hasattr(user, 'elearnuser'):
        if user.elearnuser.user_type == 'student':
            # Fetch and add enrolled courses to the context
            enrolled_courses = user.elearnuser.enrolled_courses.all()
            context['enrolled_courses'] = enrolled_courses

        elif user.elearnuser.user_type == 'teacher':
            # Fetch and add courses taught to the context
            courses_taught = Course.objects.filter(teacher=user.elearnuser)
            context['courses_taught'] = courses_taught

    return render(request, 'eLearning_app/profile.html', context)
