from django.shortcuts import render
from django.http import HttpResponseRedirect
# Added Question, Choice, and Submission models to the import list
from .models import Course, Enrollment, Question, Choice, Submission
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth import login, logout, authenticate
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

# Create your views here.

def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'onlinecourse/user_registration_bootstrap.html', context)
    elif request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("onlinecourse:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'onlinecourse/user_registration_bootstrap.html', context)


def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('onlinecourse:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'onlinecourse/user_login_bootstrap.html', context)
    else:
        return render(request, 'onlinecourse/user_login_bootstrap.html', context)


def logout_request(request):
    logout(request)
    return redirect('onlinecourse:index')


def check_if_enrolled(user, course):
    is_enrolled = False
    if user.id is not None:
        # Check if user enrolled
        num_results = Enrollment.objects.filter(user=user, course=course).count()
        if num_results > 0:
            is_enrolled = True
    return is_enrolled


# CourseListView
class CourseListView(generic.ListView):
    template_name = 'onlinecourse/course_list_bootstrap.html'
    context_object_name = 'course_list'

    def get_queryset(self):
        user = self.request.user
        courses = Course.objects.order_by('-total_enrollment')[:10]
        for course in courses:
            if user.is_authenticated:
                course.is_enrolled = check_if_enrolled(user, course)
        return courses


class CourseDetailView(generic.DetailView):
    model = Course
    template_name = 'onlinecourse/course_details_bootstrap.html'


def enroll(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user

    is_enrolled = check_if_enrolled(user, course)
    if not is_enrolled and user.is_authenticated:
        # Create an enrollment
        Enrollment.objects.create(user=user, course=course, mode='honor')
        course.total_enrollment += 1
        course.save()

    return HttpResponseRedirect(reverse(viewname='onlinecourse:course_details', args=(course.id,)))


# ==============================================================================
# NEW EXAM VIEWS (TASK 5)
# ==============================================================================

# View to handle the exam form submission when the user clicks 'Submit Exam'
def submit(request, course_id):
    # Fetch the exact course by its ID
    course = get_object_or_404(Course, pk=course_id)
    
    # Retrieve the active enrollment record for this specific user and course
    enrollment = get_object_or_404(Enrollment, user=request.user, course=course)
    
    # Create a new, empty exam submission linked to the user's enrollment
    submission = Submission.objects.create(enrollment=enrollment)
    
    if request.method == 'POST':
        # Loop through all the data submitted in the HTML form
        for key, value in request.POST.items():
            # Find the checkboxes representing the user's chosen answers (they start with 'choice_')
            if key.startswith('choice_'):
                # Extract the ID of the choice
                choice_id = int(request.POST[key])
                # Find the choice object in the database
                choice = Choice.objects.get(pk=choice_id)
                # Link the chosen answer to the user's submission record
                submission.choices.add(choice)
        
        # Save the finalized submission to the database
        submission.save()
        
        # Redirect the user to the results page, passing along the IDs needed to show their score
        return redirect('onlinecourse:show_exam_result', course_id=course_id, submission_id=submission.id)

# View to calculate and display the user's final exam score
def show_exam_result(request, course_id, submission_id):
    course = get_object_or_404(Course, pk=course_id)

    submission = get_object_or_404(
        Submission,
        pk=submission_id,
        enrollment__course=course
    )

    # Get the IDs of the choices selected by the user
    selected_ids = list(
        submission.choices.values_list('id', flat=True)
    )

    # Calculate the marks obtained and the possible score
    grade = 0
    possible_score = 0

    for question in course.question_set.all():
        possible_score += question.grade

        if question.is_get_score(selected_ids):
            grade += question.grade

    # Calculate the percentage
    percentage = (
        (grade / possible_score) * 100
        if possible_score > 0 else 0
    )

    # Prepare question results with their correct answers
    exam_results = []

    for question in course.question_set.all():
        correct_answers = question.choice_set.filter(is_correct=True)

        exam_results.append({
            'question': question,
            'correct_answers': correct_answers,
        })

    # Pass all required values to the result template
    context = {
        'course': course,
        'submission': submission,
        'grade': grade,
        'total_marks': possible_score,
        'possible_score': possible_score,
        'possible': possible_score,
        'selected_ids': selected_ids,
        'exam_results': exam_results,
        'percentage': round(percentage, 2),
        'passed': percentage >= 80,
    }

    return render(
        request,
        'onlinecourse/exam_result_bootstrap.html',
        context
    )