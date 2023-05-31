import datetime
from django.db import IntegrityError, models
from django.conf import settings

class Project(models.Model):
    PUBLIC = '+'
    PRIVATE = '-'
    VISIBILITY = [
        (PUBLIC, 'public'),
        (PRIVATE, 'private')
    ]

    OPEN = '+'
    CLOSED = '-'
    STATUS = [
        (OPEN, 'open'),
        (CLOSED, 'closed')
    ]

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.RESTRICT, related_name='projects')
    name = models.CharField(max_length=256)
    description = models.TextField()
    visibility = models.CharField(max_length=1, choices=VISIBILITY, default=PRIVATE)
    status = models.CharField(max_length=1, choices=STATUS, default=OPEN)
    creation_date = models.DateTimeField(null=True, auto_now_add=True)
    closing_date = models.DateTimeField(null=True, default=None)

    
    class Meta:
        get_latest_by = 'start_date'
        constraints = [
            models.UniqueConstraint(fields=['owner', 'name'], name='unique_project')
        ]
    
    def __str__(self):
        return self.name
    
    def publish(self):
        self.visibility = self.PUBLIC
        self.save()

    def unpublish(self):
        self.visibility = self.PRIVATE
        self.save()

    def open(self):
        self.status = self.OPEN
        self.save()

    def close(self):
        self.visibility = self.CLOSED
        self.save()

    def is_deletable(self):
        return Collaboration.objects.filter(role__project = self).count() == 0

    @property
    def collaborators(self):
        return self.roles.collaborators.distinct()

class Role(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='roles')
    name = models.CharField(max_length=256)
    collaborators = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='roles', through='Collaboration')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['project', 'name'], name='unique_role')
        ]

    def __str__(self):
        return self.name
    
    def is_deletable(self):
        return Collaboration.objects.filter(role = self).count() == 0
    
class Collaboration(models.Model):
    collaborator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.RESTRICT)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    joining_date = models.DateTimeField(auto_now_add=True)
    dismissing_date = models.DateTimeField(null=True, default=None)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['collaborator', 'role'], name='unique_collaboration')
        ]

class Task(models.Model):
    PUBLIC = '+'
    PRIVATE = '-'
    VISIBILITY = [
        (PUBLIC, 'public'),
        (PRIVATE, 'private')
    ]

    CREATED = '_'
    ASSIGNED = '='
    STARTED = '>'
    SUSPENDED = '|'
    TO_APPROVE = '?'
    TERMINATED = 'X'
    STATUS = [
        (CREATED, 'created'),
        (ASSIGNED, 'assigned'),
        (STARTED, 'started'),
        (SUSPENDED, 'suspended'),
        (TO_APPROVE, 'to approve'),
        (TERMINATED, 'terminated')
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    name = models.CharField(max_length=256)
    description = models.TextField()
    priority = models.FloatField(default=0.5)
    visibility = models.CharField(max_length=1, choices=VISIBILITY, default=PRIVATE)
    status = models.CharField(max_length=1, choices=STATUS, default=CREATED)
    roles = models.ManyToManyField(Role, related_name='tasks', through='TaskRole')
    collaborators = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='tasks', through='Assignation')
    creation_date = models.DateTimeField(auto_now_add=True)
    start_date = models.DateTimeField(null=True, default=None)
    request_date = models.DateTimeField(null=True, default=None)
    end_date = models.DateTimeField(null=True, default=None)

    class Meta:
        get_latest_by = ['creation_date', 'start_date']
        constraints = [
            models.UniqueConstraint(fields=['project', 'name'], name='unique_task'),
            models.CheckConstraint(check=models.Q(priority__gte=0, priority__lte=1), name='priority_range')
        ]

    def __str__(self):
        return self.name
    
    def publish(self):
        self.visibility = self.PUBLIC
        self.save()

    def unpublish(self):
        self.visibility = self.PRIVATE
        self.save()

    def assign(self, collaborator):
        if self.status == self.CREATED:
            self.collaborators.add(collaborator)
            self.status = self.ASSIGNED
            self.save()

    def start(self):
        if self.status == self.ASSIGNED:
            self.status = self.STARTED
            self.start_date = datetime.now()
            self.save()

    def suspend(self):
        if self.status != self.TERMINATED:
            self.status = self.SUSPENDED
            self.save()

    def restore(self):
        if self.status == self.SUSPENDED:
            if self.collaborator is not None:
                if self.start_date is not None:
                    self.status = self.STARTED
                else:
                    self.status = self.ASSIGNED
            else:
                self.status = self.CREATED
            self.save()

    def request_approval(self):
        if self.status == self.STARTED:
            self.status = self.TO_APPROVE
            self.request_date = datetime.now()
            self.save()

    def refuse_approval(self):
        if self.status == self.TO_APPROVE:
            self.status = self.STARTED
            self.request_date = None
            self.save()

    def terminate(self):
        if self.status == self.TO_APPROVE:
            self.status = self.TERMINATED
            self.end_date = datetime.now()
            self.save()

    def is_deletable(self):
        return self.collaborators.count() == 0
    
class TaskRole(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['task', 'role'], name='unique_task_role'),
        ]

    def save(self, *args, **kwargs):
        if self.role.project == self.task.project:
            super().save(*args, **kwargs)
        else:
            raise IntegrityError('roles_task')
    
class Assignation(models.Model):

    ASSIGNED = '='
    REVOKED = 'X'
    FINISHED = 'O'

    STATUS = [
        (ASSIGNED, 'assigned'),
        (REVOKED, 'revoked'),
        (FINISHED, 'finished')
    ]

    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    collaborator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.RESTRICT)
    status = models.CharField(max_length=1, choices=STATUS, default=ASSIGNED)
    assignation_date = models.DateTimeField(auto_now_add=True)
    dismissing_date = models.DateTimeField(null=True, default=None)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['task', 'collaborator'], name='unique_assignation')
        ]