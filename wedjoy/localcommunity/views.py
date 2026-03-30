# localcommunity/views.py
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .decorators import role_required
from django.db.models import Count
from django.contrib import messages
from .forms import OwnerProfileUpdateForm , EventProfileUpdateForm


# Import the Business model
from business.models import Business 
from events.models import Event,EventRegistration

# Import the form from forms.py
from .forms import addBusiness,EventForm


@login_required
@role_required(allowed_roles=["owner"])
def business_owner_dashboard(request):
    return render(request, "localcommunity/businessowner/businessowner.html")

@login_required
@role_required(allowed_roles=["user"])
def user_dashboard(request):
    return render(request, "core/index.html")

@login_required
@role_required(allowed_roles=["event_organizer"])
def eventstudio(request):
    events = Event.objects.filter(organizer=request.user).annotate(rsvp_count=Count('eventregistration'))
    total_events = events.count()
    total_rsvps = sum(getattr(event, 'rsvp_count', 0) for event in events)

    avg_attendance = 0
    if total_events > 0:
        avg_attendance = round(sum(
            (getattr(event, 'rsvp_count', 0) / event.max_participants * 100) if event.max_participants else 0
            for event in events
        ) / total_events)

    comments_count = 0

    upcoming_events = []
    for event in events.order_by('event_date')[:3]:
        maxp = event.max_participants or 0
        rsvps = getattr(event, 'rsvp_count', 0)
        prg = int((rsvps / maxp * 100)) if maxp else 0
        upcoming_events.append({
            'event': event,
            'rsvp_count': rsvps,
            'progress': prg,
        })

    context = {
        'total_events': total_events,
        'total_rsvps': total_rsvps,
        'avg_attendance': avg_attendance,
        'comments_count': comments_count,
        'upcoming_events': upcoming_events,
    }

    return render(request, "localcommunity/eventstudio/eventstudio.html", context)

# Business Owner Views
def businessownerdashboard(request):
    return render(request, "localcommunity/businessowner/businessowner.html")

# add Business--------  

def mybusinesses(request):
    businessList = Business.objects.filter(owner=request.user)
    return render(request, "localcommunity/businessowner/mybusinesses.html", {"businessList": businessList})

@login_required
def addbusiness(request):
    days = ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]

    if request.method == "POST":
        form = addBusiness(request.POST, request.FILES)
        if form.is_valid():
            business = form.save(commit=False)
            business.owner = request.user
            business.save()
            return redirect("localcommunity:mybusinesses")
    else:
        form = addBusiness()

    # Prepare business hours fields for template
    business_hours_fields = []
    for day in days:
        business_hours_fields.append({
            'day': day.title(),
            'open': form[day + "_open"],
            'close': form[day + "_close"]
        })

    return render(request, "localcommunity/businessowner/addbusiness.html", {
        'form': form,
        'business_hours_fields': business_hours_fields
    })

#---Update Business View ------

def updateBusiness(request, business_id):
    business = Business.objects.get(id=business_id, owner=request.user)

    if request.method == "POST":
        form = addBusiness(request.POST, request.FILES, instance=business)
        if form.is_valid():
            form.save()
            return redirect("localcommunity:mybusinesses")
    else:
        form = addBusiness(instance=business)

    # Prepare business hours fields for template
    days = ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]
    business_hours_fields = []
    for day in days:
        business_hours_fields.append({
            'day': day.title(),
            'open': form[day + "_open"],
            'close': form[day + "_close"]
        })

    return render(request, "localcommunity/businessowner/addbusiness.html", {
        'form': form,
        'business_hours_fields': business_hours_fields,
        'business': business
    })

#----delete` Business View ------
def deleteBusienss(request, business_id):
    business = Business.objects.get(id=business_id, owner=request.user)
    business.delete()
    return redirect("localcommunity:mybusinesses")

def reviews(request):
    return render(request, "localcommunity/businessowner/reviews.html")


# def analyticsbusiness(request):
   # return render(request, "localcommunity/businessowner/analyticsbusiness.html")


# ================= SETTINGS (FIXED) =================

@login_required
@role_required(allowed_roles=["owner"])
def settingsbusiness(request):

    user = request.user

    if request.method == 'POST':
        form = OwnerProfileUpdateForm(request.POST, instance=user)

        if form.is_valid():

            # ✅ DON'T SAVE YET
            user_obj = form.save(commit=False)

            # password fields
            current_password = form.cleaned_data.get('current_password')
            new_password = form.cleaned_data.get('new_password')
            confirm_password = form.cleaned_data.get('confirm_password')

            # 👉 if user trying to change password
            if current_password or new_password or confirm_password:

                if not user.check_password(current_password):
                    messages.error(request, "Current password is incorrect")
                    return render(request, 'localcommunity/businessowner/settingsbusiness.html', {"form": form})

                if new_password != confirm_password:
                    messages.error(request, "New passwords do not match")
                    return render(request, 'localcommunity/businessowner/settingsbusiness.html', {"form": form})

                # ✅ set new password
                user_obj.set_password(new_password)

                # save BEFORE updating session
                user_obj.save()

                # keep user logged in
                update_session_auth_hash(request, user_obj)

                messages.success(request, "Password updated successfully")

            else:
                # ✅ save normal profile updates
                user_obj.save() 
                messages.success(request, "Profile updated successfully")

            return redirect('localcommunity:businessownerdashboard')

        else:
            print(form.errors)

    else:
        form = OwnerProfileUpdateForm(instance=user)

    return render(request, 'localcommunity/businessowner/settingsbusiness.html', {"form": form})
def logoutbusiness(request):
        logout(request)
        return redirect("login")




# Event Studio Views
def eventstudiodashboard(request):
    return render(request, "localcommunity/eventstudio/eventstudio.html")

#Event List ......
@login_required
def myevents(request):

    eventList = (
        Event.objects
        .filter(organizer=request.user)
        .annotate(rsvp_count=Count("eventregistration"))
        .order_by("-created_at")
    )

    for event in eventList:
        if event.max_participants:
            event.progress = int((event.rsvp_count / event.max_participants) * 100)
        else:
            event.progress = 0

    return render(
        request,
        "localcommunity/eventstudio/myevents.html",
        {"eventList": eventList}
    )

def createevent(request):

    if request.method == "POST":
        form = EventForm(request.POST, request.FILES)

        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user
            event.save()
            return redirect("localcommunity:myevents")

    else:
        form = EventForm()

    return render(request, "localcommunity/eventstudio/createevent.html", {"form": form})


@login_required
@role_required(allowed_roles=["event_organizer", "owner"])
def attendeesevent(request):

    registrations = EventRegistration.objects.filter(
        event__organizer=request.user
    ).select_related('event', 'user')

    attendees = []
    for reg in registrations:
        status_mapping = {
            'registered': 'Pending',
            'attended': 'Confirmed',
            'cancelled': 'Cancelled'
        }

        attendees.append({
            'name': f"{reg.user.first_name} {reg.user.last_name}".strip() or reg.user.username,
            'email': reg.user.email,
            'event_title': reg.event.title,
            'status': status_mapping.get(reg.status, reg.status),
            'rsvp_date': reg.registration_date.date(),
        })

    context = {
        'attendees': attendees,
        'confirmed_count': sum(1 for a in attendees if a['status'] == 'Confirmed'),
        'pending_count': sum(1 for a in attendees if a['status'] == 'Pending'),
        'cancelled_count': sum(1 for a in attendees if a['status'] == 'Cancelled'),
        'all_emails': ','.join([a['email'] for a in attendees]),
    }

    return render(request, "localcommunity/eventstudio/attendeesevent.html", context)


# ======  update event ======
 
@login_required
def update_event(request, event_id):

    event = get_object_or_404(Event, id=event_id, organizer=request.user)

    if request.method == "POST":
        form = EventForm(request.POST, request.FILES, instance=event)

        if form.is_valid():
            form.save()
            return redirect("localcommunity:myevents")

    else:
        form = EventForm(instance=event)

    return render(request, "localcommunity/eventstudio/createevent.html", {"form": form})

#====== Delete Event =====
@login_required
def delete_event(request, event_id):

    event = get_object_or_404(Event, id=event_id, organizer=request.user)

    event.delete()

    return redirect("localcommunity:myevents")

def analyticsevent(request):
    return render(request, "localcommunity/eventstudio/analyticsbusiness.html")
@login_required
@role_required(allowed_roles=["event_organizer"])
def settingsevent(request):
    
    user = request.user

    if request.method == 'POST':
        form = EventProfileUpdateForm(request.POST, instance=user)

        if form.is_valid():

            user_obj = form.save(commit=False)

            current_password = form.cleaned_data.get('current_password')
            new_password = form.cleaned_data.get('new_password')
            confirm_password = form.cleaned_data.get('confirm_password')

            if current_password or new_password or confirm_password:

                if not user.check_password(current_password):
                    messages.error(request, "Current password is incorrect")
                    return render(request, 'localcommunity/eventstudio/settingsevent.html', {"form": form})

                if new_password != confirm_password:
                    messages.error(request, "New passwords do not match")
                    return render(request, 'localcommunity/eventstudio/settingsevent.html', {"form": form})

                user_obj.set_password(new_password)
                user_obj.save()
                update_session_auth_hash(request, user_obj)

                messages.success(request, "Password updated successfully")

            else:
                user_obj.save()
                messages.success(request, "Profile updated successfully")

            return redirect('localcommunity:eventstudiodashboard')

        else:
            print(form.errors)

    else:
        form = EventProfileUpdateForm(instance=user)
    
    # ✅ FIX IS HERE
    return render(request, "localcommunity/eventstudio/settingsevent.html", {"form": form})


def logoutevent(request):
    logout(request)
    return redirect('login')  # change if needed