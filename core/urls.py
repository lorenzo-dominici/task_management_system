from django.urls import path

from .views import *

app_name = 'core'

urlpatterns = [
    path('users/', list_users, name='users-list'),
    path('projects/', list_projects, name='projects-list'),
    path('roles/', list_roles, name='roles-list'),
    path('tasks/', list_tasks, name='tasks-list'),

    path('<str:username>/', view_user, name='user-details'),
    path('<str:username>/<str:project_name>/', view_project, name='project-details'),
    path('<str:username>/<str:project_name>/<str:role_name>/', view_role, name='role-details'),
    path('<str:username>/<str:project_name>/<str:task_name>/', view_task, name='task-details'),

    path('projects/new/', edit_project, name='project-new'),
    path('<str:username>/<str:project_name>/new-role/', edit_role, name='role-new'),
    path('<str:username>/<str:project_name>/new-task/', edit_task, name='task-new'),

    path('<str:username>/<str:project_name>/edit/', edit_project, name='project-edit'),
    path('<str:username>/<str:project_name>/<str:role_name>/edit', edit_role, name='role-edit'),
    path('<str:username>/<str:project_name>/<str:task_name>/edit/', edit_task, name='task-edit'),
]