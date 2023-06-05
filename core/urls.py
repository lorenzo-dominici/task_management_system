from django.urls import path

from .views import *

app_name = 'core'

urlpatterns = [
    path('users/', list_users, name='users-list'),
    path('projects/', list_projects, name='projects-list'),
    path('roles/', list_roles, name='roles-list'),
    path('tasks/', list_tasks, name='tasks-list'),
    path('requests/', list_requests, name='requests-list'),

    path('requests/<int:request_id>/', view_request, name='request-details'),
    path('requests/<int:request_id>/accept', accept_request, name='request-accept'),
    path('requests/<int:request_id>/reject', reject_request, name='request-reject'),
    path('requests/<int:request_id>/revoke', revoke_request, name='request-revoke'),

    path('projects/new/', edit_project, name='project-new'),
    path('<str:username>/<str:project_name>/new-role/', edit_role, name='role-new'),
    path('<str:username>/<str:project_name>/new-task/', edit_task, name='task-new'),

    path('<str:username>/<str:project_name>/edit/', edit_project, name='project-edit'),
    path('<str:username>/<str:project_name>/roles/<str:role_name>/request/', edit_request, name='request-new'),
    path('<str:username>/<str:project_name>/roles/<str:role_name>/edit/', edit_role, name='role-edit'),
    path('<str:username>/<str:project_name>/tasks/<str:task_name>/edit/', edit_task, name='task-edit'),
    path('<str:username>/<str:project_name>/<str:task_name>/join', join_task, name='task-join'),
    path('<str:username>/<str:project_name>/<str:task_name>/leave', leave_task, name='task-leave'),
    path('<str:username>/<str:project_name>/<str:task_name>/start', start_task, name='task-start'),
    path('<str:username>/<str:project_name>/<str:task_name>/end', end_task, name='task-end'),
    path('<str:username>/<str:project_name>/<str:task_name>/approve', approve_task, name='task-approve'),
    path('<str:username>/<str:project_name>/<str:task_name>/reject', reject_task, name='task-reject'),
    path('<str:username>/<str:project_name>/<str:task_name>/assign/<str:collaborator>', assign_task, name='task-assign'),
    path('<str:username>/<str:project_name>/<str:task_name>/revoke/<str:collaborator>', revoke_task, name='task-revoke'),


    path('<str:username>/', view_user, name='user-details'),
    path('<str:username>/<str:project_name>/', view_project, name='project-details'),
    path('<str:username>/<str:project_name>/roles/<str:role_name>/', view_role, name='role-details'),
    path('<str:username>/<str:project_name>/tasks/<str:task_name>/', view_task, name='task-details'),
]