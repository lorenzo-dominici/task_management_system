from django import forms
from django.contrib.auth import get_user_model
from django.contrib.admin.widgets import FilteredSelectMultiple
from .models import Project, Role, Task, JoinRequest

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'visibility', 'status']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = True

class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ['name', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = True

class TaskForm(forms.ModelForm):
    roles = forms.ModelMultipleChoiceField(queryset=Role.objects.none())

    class Meta:
        model = Task
        fields = ['name', 'description', 'visibility', 'roles']

    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project', None)
        super().__init__(*args, **kwargs)
        if kwargs['instance']:
            self.fields['roles'].initial = kwargs['instance'].roles
        if project:
            self.fields['roles'].queryset = Role.objects.filter(project=project)
        for field in self.fields.values():
            field.required = True

class JoinRequestForm(forms.ModelForm):
    class Meta:
        model = JoinRequest
        fields = ['receiver', 'description']

    def __init__(self, *args, **kwargs):
        role = kwargs.pop('role', None)
        super().__init__(*args, **kwargs)
        field_order = ['receiver', 'description']
        self.fields['receiver'] = forms.TypedChoiceField(choices = [(user.username, user.username) for user in get_user_model().objects.exclude(username__in = role.collaborators.values_list('username', flat=True)).exclude(username = role.project.owner.username)], coerce = JoinRequestForm.coerce)

    def coerce(choice):
        return get_user_model().objects.get(username=choice)