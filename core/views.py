from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from .models import Project, Task, Role
from .forms import ProjectForm, RoleForm, TaskForm

#TODO: implement pagination
#TODO: implement search/filters

def list_users(request):
    users = get_user_model().objects.exclude(username = request.user.username).annotate(assignations_count = Count('tasks')).order_by('-assignations_count')
    return render(request, 'core/users-list.html', {'users': users})

def list_projects(request):
    projects = Project.objects.filter(visibility = Project.PUBLIC)
    if request.user.is_authenticated:
        projects = projects.union(Project.objects.filter(owner = request.user))
        projects = projects.union(Project.objects.filter(roles__collaborators__in = [request.user]).distinct())
    return render(request, 'core/projects-list.html', {'projects': projects})

@login_required
def list_roles(request):
    roles = Role.objects.filter(project__in = Project.objects.filter(owner = request.user))
    roles = roles.union(Role.objects.filter(project__in = Project.objects.filter(roles__collaborators__in = [request.user]).distinct()))
    return render(request, 'core/roles-list.html', {'roles': roles})

@login_required
def list_tasks(request):
    tasks = Task.objects.filter(project__in = Project.objects.filter(owner = request.user))
    tasks = tasks.union(Task.objects.filter(roles__collaborators__in = [request.user]).distinct())
    tasks = tasks.union(Task.objects.filter(project__in = Project.objects.filter(roles__collaborators__in = [request.user]).distinct()))
    return render(request, 'core/tasks-list.html', {'tasks': tasks})

def view_user(request, username):
    user = get_object_or_404(get_user_model(), username = username)
    return render(request, 'core/user-details.html', {'user': user})

def view_project(request, project_name, username):
    project = get_object_or_404(Project, name = project_name, owner__username = username)
    if project.visibility != Project.PUBLIC:
        if request.user.is_authenticated and (request.user == project.owner or request.user in project.collaborators):
            return render(request, 'core/project-details.html', {'project': project})
        raise PermissionDenied
    return render(request, 'core/project-details.html', {'project': project})
    
def view_role(request, username, project_name, role_name):
    role = get_object_or_404(Role, name = role_name, project__name = project_name, project__owner__username = username)
    if role.project.visibility != Project.PUBLIC:
        if request.user.is_authenticated and (request.user == role.project.owner or request.user in role.project.collaborators):
            return render(request, 'core/role-details.html', {'role': role})
        raise PermissionDenied
    return render(request, 'core/role-details.html', {'role': role})

@login_required
def view_task(request, task_name, username, project_name):
    task = get_object_or_404(Task, name = task_name, project__name = project_name, project__owner__username = username)
    if not (request.user in task.project.collaborators and task.visibility == Task.PUBLIC) and request.user != task.project.owner:
        raise PermissionDenied
    render(request, 'core/task-details.html', {'task': task})

@login_required
def edit_project(request, username = None, project_name = None):
    if username and request.user.username != username:
        raise PermissionDenied
    project = get_object_or_404(Project, name = project_name, owner = request.user) if username and project_name else None
    form = ProjectForm(request.POST or None, instance = project)
    if project:
        form.fields.pop('name', None)
    if request.method == 'POST' and form.is_valid():
        project = form.save(commit=False)
        project.owner = request.user
        project.save()
        return redirect('core:project-details', username = username, project_name = project_name)
    return render(request, 'core/project-edit.html', {'form': form})

@login_required
def edit_role(request, username = None, project_name = None, role_name = None):
    if username and request.user.username != username:
        raise PermissionDenied
    project = get_object_or_404(Project, name = project_name, owner = request.user) if username and project_name else None
    role = get_object_or_404(Role, name = role_name, project = project) if project and role_name else None
    form = RoleForm(request.POST or None, instance = role)
    if role:
        form.fields.pop('name', None)
    if request.method == 'POST' and form.is_valid():
        role = form.save(commit=False)
        role.project = project
        role.save()
        return redirect('core:role-details', username = username, project_name = project_name)
    return render(request, 'core/role-edit.html', {'form': form})

@login_required
def edit_task(request, username = None, project_name = None, task_name = None):
    if username and request.user.username != username:
        raise PermissionDenied
    project = get_object_or_404(Project, name = project_name, owner = request.user) if username and project_name else None
    task = get_object_or_404(Task, name = task_name, project = project) if project and task_name else None
    form = TaskForm(request.POST or None, instance = task, project = project)
    if task:
        form.fields.pop('name', None)
    if request.method == 'POST' and form.is_valid():
        task = form.save(commit=False)
        task.project = project
        task.save()
        task.save_m2m()
        return redirect('core:project-details', username = username, project_name = project_name)
    return render(request, 'core/project-edit.html', {'form': form})