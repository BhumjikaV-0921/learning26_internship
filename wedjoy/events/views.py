from django.shortcuts import render,redirect,get_object_or_404
from .forms import EventRegistrationForm
from .models import EventRegistration
from events.models import Event
from  django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings

# Create your views here.

def showEvents(request):
    query = request.GET.get('q', '')  # default empty string
    eventList = Event.objects.all()

    if query:
        eventList = eventList.filter(
            Q(title__icontains=query) |
            Q(category__icontains=query) |
            Q(address__icontains=query)
        )

    return render(request, 'events/showEvents.html', {
        "eventList": eventList,
        "query": query
    })


def events(request,event_id):
    eventDetails = get_object_or_404(Event, id=event_id)
    return render(request, 'events/events.html', {'eventDetails': eventDetails})



@login_required(login_url='login')
def Eventrsvp(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    # Check if already registered
    if EventRegistration.objects.filter(event=event, user=request.user).exists():
        messages.warning(request, "You already registered for this event.")
        return redirect('events', event_id=event.id)

    # Check participant limit
    total_registered = EventRegistration.objects.filter(event=event).count()
    if total_registered >= event.max_participants:
        messages.error(request, "Event is full.")
        return redirect('events', event_id=event.id)

    if request.method == "POST":
        if event.registration_fee == 0:
            # Free event - register directly
            registration = EventRegistration.objects.create(
                event=event,
                user=request.user,
                amount=0,
                payment_status='paid'
            )

            # Send RSVP confirmation email
            try:
                subject = f"RSVP Confirmed: {event.title}"
                body = render_to_string("email/rsvp_confirmation.html", {
                    "user": request.user,
                    "event": event,
                    "registration": registration,
                })
                email = EmailMessage(subject, body, settings.DEFAULT_FROM_EMAIL, [request.user.email])
                email.content_subtype = "html"
                email.send(fail_silently=False)
                messages.success(request, "Successfully registered and email confirmation sent!")
            except Exception:
                messages.warning(request, "Successfully registered, but confirmation email could not be sent.")

            return redirect('events', event_id=event.id)
        else:
            # Paid event - redirect to payment
            return redirect('payments:create_payment_order', event_id=event.id)

    return render(request, 'events/Eventrsvp.html', {'event': event})