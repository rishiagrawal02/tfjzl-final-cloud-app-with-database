from django.contrib import admin
# Import all Models, including the newly created Question, Choice, and Submission
from .models import Course, Lesson, Instructor, Learner, Question, Choice, Submission


# ==============================================================================
# INLINE CLASSES
# Inlines allow us to add related objects directly on a parent object's admin page.
# ==============================================================================

# ChoiceInline allows adding or editing multiple choices directly from a Question's admin page
class ChoiceInline(admin.StackedInline):
    model = Choice
    extra = 4  # Displays 4 empty choice fields by default when creating a new question

# QuestionInline allows adding or editing questions directly from a Course's admin page
class QuestionInline(admin.StackedInline):
    model = Question
    extra = 2  # Displays 2 empty question fields by default when creating a new course

class LessonInline(admin.StackedInline):
    model = Lesson
    extra = 5


# ==============================================================================
# MODEL ADMIN CLASSES
# ModelAdmin classes customize how models are displayed and managed in the admin UI.
# ==============================================================================

class CourseAdmin(admin.ModelAdmin):
    # Added QuestionInline here so you can add Lessons and Questions on the same Course page
    inlines = [LessonInline, QuestionInline]
    list_display = ('name', 'pub_date')
    list_filter = ['pub_date']
    search_fields = ['name', 'description']

class LessonAdmin(admin.ModelAdmin):
    list_display = ['title']

# QuestionAdmin customizes the Question editor to include Choice inputs inside it
class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]          # Nests choices inside the question editor
    list_display = ['question_text']  # Shows the question text column in the admin list view


# ==============================================================================
# MODEL REGISTRATIONS
# Registering models makes them visible and editable in the Django Admin site.
# ==============================================================================

admin.site.register(Course, CourseAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Instructor)
admin.site.register(Learner)

# Register the new exam models
admin.site.register(Question, QuestionAdmin) # Registered with QuestionAdmin to apply the inlines
admin.site.register(Choice)
admin.site.register(Submission)