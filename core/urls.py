from django.urls import path

from .views import *

app_name = 'core'

urlpatterns = [
    path('projects/', ProjectListView.as_view(), name='project-list'),
    path('<str:username>/<str:project_name>/', ProjectDetailView.as_view(), name='project-detail'),
    path('tasks/', TaskListView.as_view(), name='task-list'),
    path('<str:username>/<str:project_name>/<str:task_name>/', TaskDetailView.as_view(), name='task-detail'),
]