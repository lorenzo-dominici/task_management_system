from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from .models import Project
from .models import Role
from .models import Task

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
    roles = forms.ModelMultipleChoiceField(queryset=Role.objects.none(), widget=FilteredSelectMultiple('Roles', is_stacked = False))

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