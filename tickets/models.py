from django.db import models
from django.conf import settings
from datetime import date

# Create your models here.

class Department(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Drawing(models.Model):
    name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Priority(models.Model):
    name = models.CharField(max_length=50)
    priority_weight = models.FloatField(default=1.0)
    priority_primary_points = models.FloatField(default=0)


class Ticket(models.Model):
    #STATUS_NAMES = [
    #    ('0', 'Wysłano'),
    #    ('1', 'Przypisany'),
    #    ('2',  'W trakcie'),
    #    ('9',  'Zamknięty'),
    #    ]

    boat_number = models.CharField(max_length=10)
    date = models.DateField()
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=1000)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    #target_departments = models.ManyToManyField(Department, blank=True)
    priority = models.ForeignKey(Priority, on_delete=models.CASCADE)
    #status = models.CharField(max_length=1, choices=STATUS_NAMES, default='0')
    assigned_user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='tickets_assigned')
    #drawings = models.ManyToManyField(Drawing, blank=True)

    def calculate_priority_points(self):
        points = (date.today() - self.date).days * self.priority.priority_weight + self.priority.priority_primary_points
        return points

    def __str__(self):
        return self.title


class SubTicket(models.Model):
    STATUS_NAMES = [
        (0, 'Wysłano'),
        (1, 'Przypisany'),
        (2,  'W trakcie'),
        (9,  'Zamknięty'),
        ]
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='sub_tickets')
    target_department = models.ForeignKey(Department, on_delete=models.CASCADE)
    status = models.CharField(max_length=1, choices=STATUS_NAMES, default=0)
    drawing = models.ForeignKey(Drawing, on_delete=models.CASCADE)


class TicketImage(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='ticket_images/')


class Comment(models.Model):
    sub_ticket = models.ForeignKey(SubTicket, related_name="comments", on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField(max_length=1000)
    date = models.DateTimeField(auto_now_add=True)


class Event(models.Model):
    TYPE_NAMES = [
        ('0',  'status_change'),
        ('1',  'assigned_change'),
        ]
    ticket = models.ForeignKey(Ticket, related_name="events", on_delete=models.CASCADE)
    type = models.CharField(max_length=1, choices=TYPE_NAMES, default='0')
    assigned_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    new_status = models.CharField(max_length=20, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

# xd
class Quotations(models.Model):
    content = models.CharField(max_length=500)
    author = models.CharField(max_length=100)


    