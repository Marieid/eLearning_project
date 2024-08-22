from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from .models import Course, Enrollment, Material
from .forms import StudentRegistrationForm, TeacherRegistrationForm, CourseCreationForm,  UserProfileUpdateForm, MaterialForm
from django.contrib.auth.decorators import permission_required
from django.db import transaction
from django.db.models import Q


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

        elif request.user.elearnuser.user_type == 'teacher':
            courses_taught = Course.objects.filter(
                teacher=request.user.elearnuser)
            context['courses_taught'] = courses_taught

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


@login_required
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


@ login_required
@ permission_required('eLearning_app.delete_course')
def delete_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if course.teacher != request.user.elearnuser:
        messages.error(
            request, "You are not authorized to delete this course.")
        return redirect('course_detail', course_id=course.id)


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

    return render(request, 'eLearning_app/delete_material.html', {'material': material})
