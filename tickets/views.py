from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from .models import Ticket, SubTicket, Quotations, Department, Drawing, Priority, Comment, TicketImage, Event
import random
import datetime
from django.contrib.auth.decorators import login_required
from .forms import CommentForm
from django.contrib.auth import get_user_model


@login_required
def home(request):
    tickets = Ticket.objects.all()
    sorted_tickets = sorted(tickets, key=lambda ticket: ticket.calculate_priority_points(), reverse = True)
    #quotes = Quotations.objects.all()
    #todays_quote = random.choice(quotes).content
    return render(request, "tickets_list.html", {"tickets": sorted_tickets, "quote": None})

@login_required
def my_tickets(request):
    tickets = Ticket.objects.filter(author=request.user)
    sorted_tickets = sorted(tickets, key=lambda ticket: ticket.calculate_priority_points(), reverse = True)
    title = 'Moje zgłoszenia'
    return render(request, 'tickets_list.html', {'tickets': sorted_tickets, 'title': title})

@login_required
def received_tickets(request):
    tickets = Ticket.objects.filter(assigned_user=request.user)
    sorted_tickets = sorted(tickets, key=lambda ticket: ticket.calculate_priority_points(), reverse = True)
    title = 'Otrzymane zgłoszenia'
    return render(request, 'tickets_list.html', {'tickets': sorted_tickets, 'title': title})

@login_required
def department_tickets(request):
    department = get_object_or_404(Department, id=request.user.department.id)
    tickets = Ticket.objects.filter(target_departments=department)
    sorted_tickets = sorted(tickets, key=lambda ticket: ticket.calculate_priority_points(), reverse = True)
    title = 'Zgłoszenia działu ' + department.name
    return render(request, 'tickets_list.html', {'tickets': sorted_tickets, 'title': title})

@login_required
def unassigned_tickets(request):
    department = get_object_or_404(Department, id=request.user.department.id)
    tickets = Ticket.objects.filter(target_department=department, status='0')
    sorted_tickets = sorted(tickets, key=lambda ticket: ticket.calculate_priority_points(), reverse = True)
    title = 'Nieprzypisane zgłoszenia działu ' + department.name
    return render(request, 'tickets_list.html', {'tickets': sorted_tickets, 'title': title})

@login_required
def add_ticket(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        boat_number = request.POST.get('boat_number')
        description = request.POST.get('description')
        date = datetime.datetime.now()
        author = request.user
        priority_id = request.POST.get('priority')
        priority = Priority.objects.get(id=priority_id)

        ticket = Ticket.objects.create(
            title=title, 
            boat_number=boat_number, 
            description=description, 
            date=date, 
            author=author, 
            #priority=priority,
        )
        
        departments = request.POST.getlist('departments[]')
        for department_id in departments:
            department = Department.objects.get(id=department_id)
            #ticket.target_departments.add(department)
            drawing_name = request.POST.get('drawings_' + department_id)
            drawing = Drawing.objects.create(name=drawing_name, department=department)

            sub_ticket = SubTicket.objects.create(
                ticket=ticket,
                target_department=department,
                status=0,
                drawing=drawing,
                )

        creation_event = Event(
            ticket=ticket,
            type='0',
            new_status='Wysłano'
            )
        creation_event.save()

        images = request.FILES.getlist('images')
        for image in images:
            TicketImage.objects.create(ticket=ticket, image=image)

        ticket.save();
        return redirect('details', ticket_id=ticket.id)
    departments = Department.objects.all()
    priorities = Priority.objects.all()
    return render(request, 'create_ticket.html', {"departments": departments, "priorities": priorities})

@login_required
def ticket_details(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    User = get_user_model()
    department_users = User.objects.all()

    # Handle comment submission
    if request.method == 'POST':
        form = CommentForm(request.POST)
        sub_ticket_id = request.POST.get("sub_ticket_id")
        sub_ticket = get_object_or_404(SubTicket, id=sub_ticket_id)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.sub_ticket = sub_ticket
            comment.author = request.user
            comment.save()
            return redirect('details', ticket_id=ticket.id)
    else:
        form = CommentForm()

    images = ticket.images.all()
    events = ticket.events.all()
    return render(request, 'ticket_details.html', {
        'ticket': ticket,
        'form': form,
        'images': images,
        'department_users': department_users,
        'events': events
    })

@login_required
def delete_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    if request.method == 'POST' and request.user == ticket.author:
        ticket.status = '9'
        ticket.save()
        close_event = Event(
            ticket=ticket,
            type='0',
            new_status='Zamknięto'
            )
        close_event.save()
        return redirect('details', ticket_id=ticket.id)
    return render(request, "close_ticket.html", {"ticket": ticket})

@login_required
def modify_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    if request.method == 'POST' and request.user == ticket.author:
        ticket.title = request.POST.get('title')
        ticket.boat_number = request.POST.get('boat_number')
        ticket.description = request.POST.get('description')
        departments = request.POST.getlist('departments[]')
        SubTicket.objects.filter(ticket=ticket).delete()
        
        for department_id in departments:
            department = Department.objects.get(id=department_id)
            #ticket.target_departments.add(department)
            drawing_name = request.POST.get('drawings_' + department_id)
            drawing = Drawing.objects.create(name=drawing_name,
                                             department=department,
                                             )
            #ticket.drawings.add(drawing)
            sub_ticket = SubTicket.objects.create(
                ticket=ticket,
                target_department=department,
                status=0,
                drawing=drawing,
            )
        
        priority_id = request.POST.get('priority')
        ticket.priority = Priority.objects.get(id=priority_id)
        ticket.save()

        delete_image_ids = request.POST.getlist('delete_images')
        if delete_image_ids:
            TicketImage.objects.filter(id__in=delete_image_ids, ticket=ticket).delete()
        images = request.FILES.getlist('images')
        for image in images:
            TicketImage.objects.create(ticket=ticket, image=image)
        return redirect('details', ticket_id=ticket.id)
    departments = Department.objects.all()
    priorities = Priority.objects.all()
    department_drawings = {}
    for sub_ticket in ticket.sub_tickets.all():
        drawing = sub_ticket.drawing
        department_drawings[sub_ticket.target_department.id] = drawing.name if drawing else ''
    assigned_departments = []
    for sub_ticket in ticket.sub_tickets.all():
        assigned_departments.append(sub_ticket.target_department)

    return render(request, "modify_ticket.html", {"ticket": ticket, 
                                                  "departments": departments, 
                                                  "priorities": priorities, 
                                                  "department_drawings": department_drawings,
                                                  "assigned_departments": assigned_departments,
                                                  })

@login_required
def assign_user(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)

    if request.method == 'POST':
        assigned_user_id = request.POST.get('assigned_user')
        User = get_user_model()
        #assigned_user = User.objects.get(id=assigned_user_id)
        assigned_user = get_object_or_404(User, id=assigned_user_id)
        ticket.assigned_user = assigned_user
        ticket.status = '1'
        ticket.save()
        assign_event = Event(
            ticket=ticket,
            type='1',
            new_status='Przypisano',
            assigned_user=assigned_user
            )
        assign_event.save()
        return redirect('details', ticket_id=ticket.id)