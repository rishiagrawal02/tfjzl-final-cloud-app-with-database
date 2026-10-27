import sys
from django.utils.timezone import now
try:
    from django.db import models
except Exception:
    print("There was an error loading django modules. Do you have django installed?")
    sys.exit()

from django.conf import settings
import uuid


# Instructor model
class Instructor(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    full_time = models.BooleanField(default=True)
    total_learners = models.IntegerField()

    def __str__(self):
        return self.user.username


# Learner model
class Learner(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    STUDENT = 'student'
    DEVELOPER = 'developer'
    DATA_SCIENTIST = 'data_scientist'
    DATABASE_ADMIN = 'dba'
    OCCUPATION_CHOICES = [
        (STUDENT, 'Student'),
        (DEVELOPER, 'Developer'),
        (DATA_SCIENTIST, 'Data Scientist'),
        (DATABASE_ADMIN, 'Database Admin')
    ]
    occupation = models.CharField(
        null=False,
        max_length=20,
        choices=OCCUPATION_CHOICES,
        default=STUDENT
    )
    social_link = models.URLField(max_length=200)

    def __str__(self):
        return self.user.username + "," + \
               self.occupation


# Course model
class Course(models.Model):
    name = models.CharField(null=False, max_length=30, default='online course')
    image = models.ImageField(upload_to='course_images/')
    description = models.CharField(max_length=1000)
    pub_date = models.DateField(null=True)
    instructors = models.ManyToManyField(Instructor)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Enrollment')
    total_enrollment = models.IntegerField(default=0)
    is_enrolled = False

    def __str__(self):
        return "Name: " + self.name + "," + \
               "Description: " + self.description


# Lesson model
class Lesson(models.Model):
    title = models.CharField(max_length=200, default="title")
    order = models.IntegerField(default=0)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    content = models.TextField()


# Enrollment model
# Once a user enrolled a class, an enrollment entry should be created between the user and course
# And we could use the enrollment to track information such as exam submissions
class Enrollment(models.Model):
    AUDIT = 'audit'
    HONOR = 'honor'
    BETA = 'BETA'
    COURSE_MODES = [
        (AUDIT, 'Audit'),
        (HONOR, 'Honor'),
        (BETA, 'BETA')
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date_enrolled = models.DateField(default=now)
    mode = models.CharField(max_length=5, choices=COURSE_MODES, default=AUDIT)
    rating = models.FloatField(default=5.0)


# ==============================================================================
# NEW MODELS FOR EXAM FEATURE (TASK 1)
# ==============================================================================

# Question Model: Stores questions related to a specific course
class Question(models.Model):
    # Many-to-One relationship: Many questions belong to one course.
    # on_delete=models.CASCADE means if the course is deleted, its questions are deleted too.
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    
    # The actual text of the question
    question_text = models.TextField()

    # The point value of this question, defaults to 1 points
    grade = models.IntegerField(default=1) 

    # Method to calculate if the learner got the correct score for this question
    def is_get_score(self, selected_ids):
        # Counts how many choices for this question are actually correct
        all_answers = self.choice_set.filter(is_correct=True).count()
        # Counts how many of the correct choices the user actually selected
        selected_correct = self.choice_set.filter(is_correct=True, id__in=selected_ids).count()
        
        # If the user selected all the correct choices, return True (they get the points)
        if all_answers == selected_correct:
            return True
        else:
            return False

    # Displays the question text in the Django Admin site
    def __str__(self):
        return self.question_text


# Choice Model: Stores the multiple-choice options for a given question
class Choice(models.Model):
    # Many-to-One relationship: Many choices belong to one specific Question.
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    
    # The text of the choice (e.g., "A. True", "B. False")
    choice_text = models.CharField(max_length=100)
    
    # Boolean flag to indicate if this choice is the correct answer
    is_correct = models.BooleanField(default=False)

    # Displays the choice text in the Django Admin site
    def __str__(self):
        return self.choice_text


# Submission Model: Tracks an individual learner's exam attempt
class Submission(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    choices = models.ManyToManyField(Choice)

    def __str__(self):
        return f"Submission {self.id} for enrollment {self.enrollment.id}"