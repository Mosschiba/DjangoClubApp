from django.shortcuts import render, redirect
import calendar
from calendar import HTMLCalendar
from datetime import datetime
from .models import Venue, Event
from .forms import VenueForm, EventForm, EventFormAdmin
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.contrib import messages
import csv

# pdf things to import
from django.http import FileResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter

# Paginations thing to import
from django.core.paginator import Paginator

# Generate PDF file


def venue_pdf(request):
    # create Buffer
    buf = io.BytesIO()
    # create a canvas
    c = canvas.Canvas(buf, pagesize=letter, bottomup=0)
    # create text object
    textob = c.beginText()
    textob.setTextOrigin(inch, inch)
    textob.setFont('Helvetica', 14)
    # Designate the Model
    venues = Venue.objects.all()
    lines = []

    for venue in venues:
        lines.append(venue.name)
        lines.append(venue.address)
        lines.append(venue.zip_code)
        lines.append(venue.phone)
        lines.append(venue.web)
        lines.append(venue.email_address)
        lines.append("  ")
    # loop throught the lines
    for line in lines:
        textob.textLine(line)

    # finich the reportlab thing
    c.drawText(textob)
    c.showPage()
    c.save()
    buf.seek(0)

    # return the something here is will be response
    return FileResponse(buf, as_attachment=True, filename='venue.pdf')


# Generate CSV pile (EXCEL)
def venue_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-disposition'] = 'attachment; filename = venues.csv'

    # create a csv writer this comes with the import csv
    writer = csv.writer(response)
    # Designate the models to pprint
    venues = Venue.objects.all()

    # add culomn heading to the csv file
    writer.writerow(['Venue Name', 'Address', 'Zip Code',
                    'Phone', 'Website', 'Email'])

    for venue in venues:
        writer.writerow([venue.name, venue.address, venue.zip_code,
                        venue.phone, venue.web, venue.email_address])

    return response


# Generate text file dynamicly
def venue_text(request):
    response = HttpResponse(content_type='text/plain')
    response['Content-disposition'] = 'attachment; filename = venues.txt'
    # Designate the models to pprint
    venues = Venue.objects.all()
    lines = []
    for venue in venues:
        lines.append(
            f'{venue.name}\n{venue.address}\n{venue.zip_code}\n{venue.phone}\n{venue.web}\n{venue.email_address}\n\n\n\n\n')

    response.writelines(lines)
    return response


def home(request, year=datetime.now().year, month=datetime.now().strftime('%B')):
    name = 'Islam'
    month = month.capitalize()
    # convert month to number
    month_number = list(calendar.month_name).index(month)
    month_number = int(month_number)
    # create calendar
    cal = HTMLCalendar().formatmonth(year, month_number)
    # get current year
    now = datetime.now()
    current_year = now.year
    # get current time
    time = now.strftime('%I:%M  %p')
    return render(request, 'events/home.html', {
        'name': name,
        'year': year,
        'month': month,
        'month_number': month_number,
        'cal': cal,
        'current_year': current_year,
        'time': time,
    })


def all_events(request):
    events_list = Event.objects.all()
    return render(request, 'events/events_list.html', {'events_list': events_list})


def add_venue(request):
    submitted = False
    if request.method == "POST":
        form = VenueForm(request.POST)
        if form.is_valid():
            # form.save()
            venue = form.save(commit=False)
            venue.owner = request.user.id  # loggrd in user
            venue.save()
            return HttpResponseRedirect('/add_venue?submitted=True')
    else:
        form = VenueForm
        if 'submitted' in request.GET:
            submitted = True
    return render(request, 'events/add_venue.html', {'form': form, 'submitted': submitted})


def list_venues(request):
    # list_venue = Venue.objects.all().order_by('name') => order by alphabet
    list_venue = Venue.objects.all()

    # set paginations
    # the second argunment(2) is for how many by page
    p = Paginator(Venue.objects.all().order_by('name'), 3)
    page = request.GET.get('page')
    venues = p.get_page(page)
    page_num = 'n' * venues.paginator.num_pages
    return render(request, 'events/venues.html', {'list_venue': list_venue, 'venues': venues, 'page_num': page_num})


def show_venue(request, venue_id):
    venue = Venue.objects.get(pk=venue_id)
    venue_owner = User.objects.get(pk=venue.owner)
    return render(request, 'events/show_venue.html', {'venue': venue, 'venue_owner': venue_owner})


def search_venue(request):
    if request.method == "POST":
        searched = request.POST['searched']
        venues = Venue.objects.filter(name__contains=searched)
        return render(request, 'events/search_venue.html', {'searched': searched, 'venues': venues})
    else:
        return render(request, 'events/search_venue.html', {})


def update_venue(request, venue_id):
    venue = Venue.objects.get(pk=venue_id)
    form = VenueForm(request.POST or None, instance=venue)
    if form.is_valid():
        form.save()
        return redirect('list-venues')
    return render(request, 'events/update_venue.html', {'vanue': venue, 'form': form})


def add_event(request):
    submitted = False
    if request.method == "POST":
        if request.user.is_superuser:
            form = EventFormAdmin(request.POST)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect('/add_event?submitted=True')
        else:
            form = EventForm(request.POST)
            if form.is_valid():
                event = form.save(commit=False)
                event.manager = request.user
                event.save()
                return HttpResponseRedirect('/add_event?submitted=True')
    else:
        if request.user.is_superuser:
            form = EventFormAdmin
        else:
            form = EventForm
        if 'submitted' in request.GET:
            submitted = True
    return render(request, 'events/add_event.html', {'form': form, 'submitted': submitted})


def update_event(request, event_id):
    event = Event.objects.get(pk=event_id)
    if request.user.is_superuser:
        form = EventFormAdmin(request.POST or None, instance=event)
    else:
        form = EventForm(request.POST or None, instance=event)
    if form.is_valid():
        form.save()
        return redirect('list-events')
    else:
        return render(request, 'events/update_event.html', {'form': form, 'event': event})


def delete_event(request, event_id):
    event = Event.objects.get(pk=event_id)
    if request.user == event.manager:
        event.delete()
        messages.success(request, 'You have succesfully deleted the event')
        return redirect('list-events')
    else:
        messages.error(
            request, 'You are Not the event manager You can Not delete the event')
        return redirect('list-events')


def delete_venue(request, venue_id):
    event = Venue.objects.get(pk=venue_id)
    event.delete()
    return redirect('list-venues')


def my_events(request):
    if request.user.is_authenticated:
        me = request.user.id
        events = Event.objects.filter(attendees=me)
        return render(request, 'events/my_events.html', {'events': events})
    else:
        messages.error(
            request, 'You are Not the event manager You can view the event')
        return redirect('home')
