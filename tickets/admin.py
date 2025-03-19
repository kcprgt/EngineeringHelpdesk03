from django.contrib import admin
from .models import Ticket, SubTicket, Department, Priority, Quotations, Comment, TicketImage, Event, Drawing

# Register your models here.
admin.site.register(Ticket)
admin.site.register(SubTicket)
admin.site.register(Department)
admin.site.register(Priority)
admin.site.register(Quotations)
admin.site.register(Comment)
admin.site.register(TicketImage)
admin.site.register(Event)
admin.site.register(Drawing)