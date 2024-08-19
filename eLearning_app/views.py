from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from .models import Course, Enrollment, Material
from .forms import StudentRegistrationForm, TeacherRegistrationForm, CourseCreationForm
from django.contrib.auth.decorators import permission_required


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
    # Fetch user profile data and render the profile template
    return render(request, 'eLearning_app/profile.html', {'user': request.user})


@login_required
# Teacher can add course
def create_course(request):
    if not request.user.is_teacher:
        messages.error(request, "Only teachers can create courses.")
        # Or redirect to a suitable page
        return redirect('index')

    if request.method == 'POST':
        form = CourseCreationForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            # Associate the course with the current teacher
            course.teacher = request.user.teacher
            course.save()
            messages.success(request, "Course created successfully!")
            # Redirect to the course detail page
            return redirect('course_detail', course_id=course.id)
    else:
        form = CourseCreationForm()
    return render(request, 'eLearning_app/create_course.html', {'form': form})


@login_required
def course_list(request):
    # Filter for open courses
    courses = Course.objects.filter(enrollment_status='open')
    return render(request, 'eLearning_app/course_list.html', {'courses': courses})


def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    materials = Material.objects.filter(course=course)
    enrolled_students = course.students.all()

    context = {
        'course': course,
        'materials': materials,
        'enrolled_students': enrolled_students,
    }
    return render(request, 'eLearning_app/course_detail.html', context)


@login_required
# Teacher can change course
@permission_required('eLearning_app.change_course')
def edit_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if course.teacher != request.user.teacher:
        messages.error(request, "You are not authorized to edit this course.")
        return redirect('course_detail', course_id=course.id)

    if request.method == 'POST':
        form = CourseCreationForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, "Course updated successfully!")
            return redirect('course_detail',
                            course_id=course.id)
    else:
        form = CourseCreationForm(instance=course)
    return render(request, 'eLearning_app/edit_course.html', {'form': form, 'course': course})


@login_required
# Teacher can delete course
@permission_required('eLearning_app.delete_course')
def delete_course(request, course_id):
    course = get_object_or_404(Course,
                               id=course_id)
    if course.teacher != request.user.teacher:
        messages.error(
            request, "You are not authorized to delete this course.")
        return redirect('course_detail', course_id=course.id)

    if request.method == 'POST':
        course.delete()
        messages.success(request, "Course deleted successfully!")
        return redirect('course_list')
    return render(request,
                  'eLearning_app/delete_course.html', {'course': course})


# Student can view course to enroll
def enroll_in_course(request, course_id):
    if not request.user.is_authenticated:
        # Redirect to login page with 'next' parameter
        return redirect(f'/login/?next=/course/{course_id}/enroll/')
    if not request.user.is_student:
        messages.error(request, "Only students can enroll in courses.")
        return redirect('profile')

    try:
        course = Course.objects.get(id=course_id, enrollment_status='open')
        print("Object created: " + str(course))
    except Course.DoesNotExist:
        messages.error(request, "Course not found or enrollment is closed.")
        return redirect('course_list')

    Enrollment.objects.create(student=request.user.student, course=course)
    messages.success(request, "Enrolled in course successfully!")
    return redirect('course_detail', course_id=course.id)


@login_required
# Teacher can change course (to close enrollment)
@permission_required('eLearning_app.change_course')
def close_enrollment(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if course.teacher != request.user.teacher:
        messages.error(
            request, "You are not authorized to close enrollment for this course.")
        return redirect('course_detail', course_id=course.id)

    if request.method == 'POST':
        course.enrollment_status = 'closed'
        course.save()
        messages.success(request, "Enrollment closed for this course.")
        return redirect('course_detail', course_id=course.id)
    return render(request, 'eLearning_app/close_enrollment.html', {'course': course})

