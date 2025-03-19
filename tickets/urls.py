from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    #path('create', views.create_ticket, name='create_ticket'),
    path('add_ticket', views.add_ticket, name='add_ticket'),
    path('details/<int:ticket_id>', views.ticket_details, name='details'),
    path('delete/<int:ticket_id>', views.delete_ticket, name='delete'),
    path('modify/<int:ticket_id>', views.modify_ticket, name='modify'),
    path('my', views.my_tickets, name='my_tickets'),
    path('received', views.received_tickets, name='received_tickets'),
    path('department', views.department_tickets, name='department_tickets'),
    path('unassigned', views.unassigned_tickets, name='unassigned_tickets'),
    path('assign_user/<int:ticket_id>/', views.assign_user, name='assign_user'),
]
