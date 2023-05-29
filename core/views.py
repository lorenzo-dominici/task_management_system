from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.views.generic import ListView
from django.views.generic import DetailView
from .models import Project
from .models import Task

class ProjectListView(ListView):
    template_name = 'core/project-list.html'
    context_object_name = 'projects'

    def get_queryset(self):
        projects = Project.objects.filter(visibility = Project.PUBLIC)
        if self.request.user.is_authenticated:
            projects = projects.union(Project.objects.filter(owner = self.request.user))
            projects = projects.union(Project.objects.filter(collaborators__in = [self.request.user]).distinct())
        return projects

class ProjectDetailView(DetailView):
    template_name = 'core/project-detail.html'
    context_object_name = 'project'

    def get_queryset(self):
        try:
            project = Project.objects.get(name = self.kwargs['project_name'], owner = self.kwargs['username'])
        except Project.DoesNotExist:
            return Project.objects.none()
        if project.visibility != Project.PUBLIC:
            if self.request.user.is_authenticated and (self.request.user == project.owner or self.request.user in project.collaborators):
                return project
            else:
                raise PermissionDenied
        else:
            return project

class TaskListView(LoginRequiredMixin, ListView):
    template_name = 'core/task-list.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        tasks = Task.objects.filter(project__in = Project.objects.filter(owner = self.request.user))
        tasks = tasks.union(Task.objects.filter(collaborator__in = [self.request.user]).distinct())
        tasks = tasks.union(Task.objects.filter(project__in = Project.object.filter(collaborators__in = [self.request.user]).distinct()))

class TaskDetailView(LoginRequiredMixin, DetailView):
    template_name = 'core/task-detail.html'
    context_object_name = 'task'

    def get_queryset(self):
        try:
            task = Task.objects.get(name = self.kwargs['task_name'], project = Project.objects.get(name = self.kwargs['project_name'], owner = self.kwargs['username']))
            owned = task.filter(project__name = self.request.user)
            assigned = task.filter(collaborator = self.request.user)
            available = task.filter(visibility = Task.PUBLIC, roles__collaborators__in = [self.request.user]).distinct()
            task = task.union(owned).union(assigned).union(available)
            if task.count() == 0:
                raise PermissionDenied
        except Task.DoesNotExist:
            return Task.objects.none()
        return task