from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from .models import *
from .forms import *

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

@login_required
def list_requests(request):
    join_requests = JoinRequest.objects.filter(status = JoinRequest.PENDING, sender = request.user)
    join_requests = join_requests.union(JoinRequest.objects.filter(status = JoinRequest.PENDING, receiver = request.user))
    return render(request, 'core/requests-list.html', {'join_requests': join_requests})

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
    collaborators = task.active_collaborators
    competence = task.is_competent(request.user)
    competent_collaborators = task.project.collaborators.filter(roles__in = task.roles.all()).distinct().exclude(username__in = collaborators.values_list('username', flat = True))
    return render(request, 'core/task-details.html', {'task': task, 'collaborators': collaborators, 'competence': competence, 'competent_collaborators': competent_collaborators})

@login_required
def view_request(request, request_id):
    join_request = get_object_or_404(JoinRequest, id = request_id)
    if join_request.status != JoinRequest.PENDING or (request.user != join_request.sender and request.user != join_request.receiver):
        raise PermissionDenied
    return render(request, 'core/request-details.html', {'join_request': join_request})

@login_required
def edit_project(request, username = None, project_name = None):
    if username and request.user.username != username:
        raise PermissionDenied
    project = get_object_or_404(Project, name = project_name, owner = request.user) if username and project_name else None
    form = ProjectForm(request.POST or None, instance = project)
    if project:
        form.fields.pop('name', None)
    else:
        form.fields.pop('status', None)
    if request.method == 'POST' and form.is_valid():
        project = form.save(commit=False)
        project.owner = request.user
        project.save()
        return redirect('core:project-details', username = project.owner.username, project_name = project.name)
    return render(request, 'core/project-edit.html', {'form': form, 'edit': project is not None})

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
        return redirect('core:role-details', username = role.project.owner.username, project_name = role.project.name, role_name = role.name)
    return render(request, 'core/role-edit.html', {'form': form, 'edit': role is not None})

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
        if form.cleaned_data['roles']:
            task.roles.add(form.cleaned_data['roles'].get().id)
        return redirect('core:task-details', username = task.project.owner.username, project_name = task.project.name, task_name = task.name)
    return render(request, 'core/task-edit.html', {'form': form, 'edit': task is not None})

@login_required
def edit_request(request, username, project_name, role_name):
    role = get_object_or_404(Role, name = role_name, project__name = project_name, project__owner__username = username)
    form = JoinRequestForm(request.POST or None, role = role)
    if request.user == role.project.owner:
        if request.method == 'POST' and form.is_valid():
            join_request = form.save(commit=False)
            join_request.sender = request.user
            join_request.role = role
            join_request.save()
            return redirect('core:request-details', request_id = join_request.id)
        return render(request, 'core/request-edit.html', {'form': form, 'edit': False})
    else:
        form.fields.pop('receiver', None)
        if role.project.visibility == Project.PUBLIC:
            if request.method == 'POST' and form.is_valid():
                join_request = form.save(commit=False)
                join_request.sender = request.user
                join_request.receiver = role.project.owner
                join_request.role = role
                join_request.save()
                return redirect('core:request-details', request_id = join_request.id)
        return render(request, 'core/request-edit.html', {'form': form, 'edit': False})
        raise PermissionDenied

@login_required
def join_task(request, username, project_name, task_name):
    task = get_object_or_404(Task, name = task_name, project__name = project_name, project__owner__username = username)
    if request.user not in task.project.collaborators or task.active_collaborators.filter(username = request.user.username).exists():
        raise PermissionDenied
    task.collaborators.add(request.user)
    if task.status == Task.CREATED or task.status == Task.ASSIGNED:
        task.status = Task.ASSIGNED
        task.save()
    return redirect('core:task-details', username = task.project.owner.username, project_name = task.project.name, task_name = task.name)

@login_required
def leave_task(request, username, project_name, task_name):
    task = get_object_or_404(Task, name = task_name, project__name = project_name, project__owner__username = username)
    if request.user in task.active_collaborators:
        assignation = get_object_or_404(Assignation, task = task, collaborator = request.user)
        assignation.dismissing_date = timezone.now()
        assignation.save()
    return redirect('core:task-details', username = task.project.owner.username, project_name = task.project.name, task_name = task.name)

@login_required
def assign_task(request, username, project_name, task_name, collaborator):
    task = get_object_or_404(Task, name = task_name, project__name = project_name, project__owner__username = username)
    collaborator = get_object_or_404(get_user_model(), username = collaborator)
    if request.user != task.project.owner or not task.project.collaborators.filter(username = collaborator.username).exists() or not task.is_competent(collaborator):
        raise PermissionDenied
    if task.status == Task.CREATED or task.status == Task.ASSIGNED:
        task.status = Task.ASSIGNED
        task.collaborators.add(collaborator)
        task.save()
    return redirect('core:task-details', username = task.project.owner.username, project_name = task.project.name, task_name = task.name)

@login_required
def revoke_task(request, username, project_name, task_name, collaborator):
    task = get_object_or_404(Task, name = task_name, project__name = project_name, project__owner__username = username)
    collaborator = get_user_model().objects.get(username = collaborator)
    if request.user != task.project.owner or task.status == Task.TERMINATED or task.project.collaborators.filter(username = collaborator.username).exists():
        raise PermissionDenied
    assignation = get_object_or_404(Assignation, task = task, collaborator = collaborator).dismissing_date = timezone.now()
    assignation.save()
    if Assignation.objects.filter(task = task, dismissing_date__isnull = True).exists():
        task.request_date = None
        task.status = Task.CREATED
        task.save()
    return redirect('core:task-details', username = task.project.owner.username, project_name = task.project.name, task_name = task.name)

@login_required
def start_task(request, username, project_name, task_name):
    task = get_object_or_404(Task, name = task_name, project__name = project_name, project__owner__username = username)
    if request.user not in task.active_collaborators or task.status != Task.ASSIGNED:
        raise PermissionDenied
    task.status = Task.STARTED
    task.start_date = timezone.now()
    task.save()
    return redirect('core:task-details', username = task.project.owner.username, project_name = task.project.name, task_name = task.name)

@login_required
def end_task(request, username, project_name, task_name):
    task = get_object_or_404(Task, name = task_name, project__name = project_name, project__owner__username = username)
    if request.user not in task.active_collaborators or task.status != Task.STARTED:
        raise PermissionDenied
    task.status = Task.TO_APPROVE
    task.request_date = timezone.now()
    task.save()
    return redirect('core:task-details', username = task.project.owner.username, project_name = task.project.name, task_name = task.name)

@login_required
def approve_task(request, username, project_name, task_name):
    task = get_object_or_404(Task, name = task_name, project__name = project_name, project__owner__username = username)
    if request.user != task.project.owner:
        raise PermissionDenied
    task.status = Task.TERMINATED
    task.end_date = timezone.now()
    task.save()
    return redirect('core:task-details', username = task.project.owner.username, project_name = task.project.name, task_name = task.name)

@login_required
def reject_task(request, username, project_name, task_name):
    task = get_object_or_404(Task, name = task_name, project__name = project_name, project__owner__username = username)
    if request.user != task.project.owner:
        raise PermissionDenied
    task.status = Task.STARTED
    task.request_date = None
    task.save()
    return redirect('core:task-details', username = task.project.owner.username, project_name = task.project.name, task_name = task.name)

@login_required
def accept_request(request, request_id):
    join_request = get_object_or_404(JoinRequest, id = request_id)
    if join_request.status != JoinRequest.PENDING or request.user != join_request.receiver:
        raise PermissionDenied
    if request.user == join_request.role.project.owner:
        join_request.role.collaborators.add(join_request.sender)
    else:
        join_request.role.collaborators.add(join_request.receiver)
    join_request.status = JoinRequest.ACCEPTED
    join_request.save()
    return redirect('core:project-details', username = join_request.role.project.owner.username, project_name = join_request.role.project.name)

@login_required
def reject_request(request, request_id):
    join_request = get_object_or_404(JoinRequest, id = request_id)
    if join_request.state != JoinRequest.PENDING or request.user != join_request.receiver:
        raise PermissionDenied
    join_request.status = JoinRequest.REJECTED
    join_request.save()
    return redirect('core:project-details', username = join_request.role.project.owner.username, project_name = join_request.role.project.name)

@login_required
def revoke_request(request, request_id):
    join_request = get_object_or_404(JoinRequest, id = request_id)
    if join_request.status != JoinRequest.PENDING or request.user != join_request.sender:
        raise PermissionDenied
    join_request.delete()
    return redirect('core:project-details', username = join_request.role.project.owner.username, project_name = join_request.role.project.name)

@login_required
def dismiss_role(request, username, project_name, role_name, collaborator):
    role = get_object_or_404(Role, name = role_name, project__name = project_name, project__owner__username = username)
    if request.user != role.project.owner:
        raise PermissionDenied
    collaborator = get_object_or_404(get_user_model(), username = collaborator)
    collaboration = get_object_or_404(Collaboration, role = role, collaborator = collaborator)
    if collaboration.dismissing_date is not None:
        raise PermissionDenied
    collaboration.dismissing_date = timezone.now()
    collaboration.save()
    return redirect('core:role-details', username = role.project.owner.username, project_name = role.project.name, role_name = role.name)