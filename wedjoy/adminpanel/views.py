# adminpanel/views.py
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from core.models import User
from events.models import Event
from business.models import Business
from volunteers.models import VolunteerOpportunity
from .forms import AdminLoginForm,VolunteerOpportunityForm
from volunteers.models import VolunteerOpportunity, VolunteerParticipation,VolunteerRegistration
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta


# Admin login view
def admin_login(request):
    if request.user.is_authenticated and request.user.is_admin:
        return redirect("adminpanel:dashboard")

    if request.method == "POST":
        form = AdminLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user and user.is_admin:
                login(request, user)
                return redirect("adminpanel:dashboard")
            else:
                messages.error(request, "Invalid credentials or not authorized")
    else:
        form = AdminLoginForm()
    return render(request, "adminpanel/login.html", {'form': form})

# Admin logout

def admin_logout(request):
    logout(request)
    messages.success(request, "Logged out successfully")
    return redirect('adminpanel:login')

# Admin-only access decorator
def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_admin:
            return view_func(request, *args, **kwargs)
        messages.error(request, "You are not authorized to view this page")
        return redirect('adminpanel:login')
    return wrapper

# Admin dashboard
@login_required
@admin_required
def dashboard(request):
    total_users = User.objects.count()
    total_events = Event.objects.count()
    total_businesses = Business.objects.count()
    total_volunteers = VolunteerOpportunity.objects.count()

    return render(request, "adminpanel/dashboard.html", {
        'total_users': total_users,
        'total_events': total_events,
        'total_businesses': total_businesses,
        'total_volunteers': total_volunteers
    })



@login_required
@admin_required
def manage_users(request):

    users = User.objects.all().order_by('-id')

    # 🔍 Search
    query = request.GET.get('q')
    if query:
        users = users.filter(
            Q(firstName__icontains=query) |
            Q(lastName__icontains=query) |
            Q(email__icontains=query)
        )

    # 🎭 Role Filter
    role = request.GET.get('role')
    if role and role != "all":
        users = users.filter(role=role)

    # 📊 Status Filter
    status = request.GET.get('status')
    if status == "active":
        users = users.filter(is_active=True)
    elif status == "suspended":
        users = users.filter(is_active=False)

    # 📈 Stats
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    suspended_users = User.objects.filter(is_active=False).count()

    last_30_days = timezone.now() - timedelta(days=30)
    new_users = User.objects.filter(created_at__gte=last_30_days).count()
    context = {
        "users": users,
        "total_users": total_users,
        "active_users": active_users,
        "suspended_users": suspended_users,
        "new_users": new_users,
    }

    return render(request, "adminpanel/user.html", context)

@login_required
@admin_required
def suspend_user(request, id):
    user = get_object_or_404(User, id=id)
    user.is_active = False
    user.save()
    messages.warning(request, "User suspended")
    return redirect('adminpanel:users')


@login_required
@admin_required
def activate_user(request, id):
    user = get_object_or_404(User, id=id)
    user.is_active = True
    user.save()
    messages.success(request, "User activated")
    return redirect('adminpanel:users')


@login_required
@admin_required
def delete_user(request, id):
    user = get_object_or_404(User, id=id)
    user.delete()
    messages.error(request, "User deleted")
    return redirect('adminpanel:users')

# Manage events
@login_required
@admin_required
def manage_events(request):

    events = Event.objects.all().order_by('-id')

    # 🔍 Search
    query = request.GET.get('q')
    if query:
        events = events.filter(
            Q(title__icontains=query) |
            Q(location_name__icontains=query)
        )

    # 🎯 Filter
    status = request.GET.get('status')
    if status and status != "all":
        events = events.filter(approval_status=status)

    # 📊 Stats
    total_events = Event.objects.count()
    approved_events = Event.objects.filter(approval_status='approved').count()
    pending_events = Event.objects.filter(approval_status='pending').count()

    # 👥 attendees + %
    total_attendees = 0

    for event in events:
        current = event.eventregistration_set.count()
        total_attendees += current

        event.current_participants = current

        if event.max_participants > 0:
            event.fill_percent = int((current / event.max_participants) * 100)
        else:
            event.fill_percent = 0

    context = {
        "events": events,
        "total_events": total_events,
        "approved_events": approved_events,
        "pending_events": pending_events,
        "total_attendees": total_attendees,
    }

    return render(request, "adminpanel/manage_event.html", context)

@login_required
@admin_required
def approve_event(request, id):
    event = get_object_or_404(Event, id=id)
    event.approval_status = "approved"
    event.save()
    messages.success(request, "Event approved")
    return redirect('adminpanel:events')


@login_required
@admin_required
def reject_event(request, id):
    event = get_object_or_404(Event, id=id)
    event.approval_status = "cancelled"
    event.save()
    messages.warning(request, "Event rejected")
    return redirect('adminpanel:events')


@login_required
@admin_required
def delete_event(request, id):
    event = get_object_or_404(Event, id=id)
    event.delete()
    messages.error(request, "Event deleted")
    return redirect('adminpanel:events')


# Manage businesses
@login_required
@admin_required
def manage_businesses(request):

    businesses = Business.objects.all().order_by('-id')

    # 🔍 Search
    query = request.GET.get('q')
    if query:
        businesses = businesses.filter(
            Q(business_name__icontains=query) |
            Q(city__icontains=query)
        )

    # 🎯 Category filter
    category = request.GET.get('category')
    if category and category != "all":
        businesses = businesses.filter(category=category)

    # 🎯 Status filter
    status = request.GET.get('status')
    if status and status != "all":
        businesses = businesses.filter(approval_status=status)

    # 📊 Stats
    total_businesses = Business.objects.count()
    approved_businesses = Business.objects.filter(approval_status='approved').count()
    pending_businesses = Business.objects.filter(approval_status='pending').count()

    # ⭐ Fake rating (since not in model yet)
    avg_rating = 4.7

    # 📂 Categories list
    categories = Business.objects.values_list('category', flat=True).distinct()

    context = {
        "businesses": businesses,
        "total_businesses": total_businesses,
        "approved_businesses": approved_businesses,
        "pending_businesses": pending_businesses,
        "avg_rating": avg_rating,
        "categories": categories,
    }

    return render(request, "adminpanel/manage_business.html", context)

@login_required
@admin_required
def approve_business(request, id):
    obj = get_object_or_404(Business, id=id)
    obj.approval_status = "approved"
    obj.save()
    messages.success(request, "Business approved")
    return redirect('adminpanel:businesses')


@login_required
@admin_required
def reject_business(request, id):
    obj = get_object_or_404(Business, id=id)
    obj.approval_status = "rejected"
    obj.save()
    messages.warning(request, "Business rejected")
    return redirect('adminpanel:businesses')


@login_required
@admin_required
def delete_business(request, id):
    obj = get_object_or_404(Business, id=id)
    obj.delete()
    messages.error(request, "Business deleted")
    return redirect('adminpanel:businesses')


# LIST ALL OPPORTUNITIES
@login_required
@admin_required
def volunteer_list(request):

    opportunities = VolunteerOpportunity.objects.all().order_by('-id')

    # 🔍 Search
    query = request.GET.get('q')
    if query:
        opportunities = opportunities.filter(
            Q(title__icontains=query) |
            Q(location__icontains=query)
        )

    from django.utils import timezone
    today = timezone.now().date()

    total_participants = 0

    for v in opportunities:

        # 👥 count participants
        count = VolunteerParticipation.objects.filter(volunteer=v).count()
        v.participant_count = count
        total_participants += count

        # 📊 status logic
        if v.start_date > today:
            v.status_label = "Upcoming"
        elif v.start_date <= today <= v.end_date:
            v.status_label = "Active"
        else:
            v.status_label = "Expired"

    # 🎯 Filter
    status = request.GET.get('status')
    if status and status != "all":
        opportunities = [v for v in opportunities if v.status_label.lower() == status]

    # 📊 Cards
    total_opportunities = len(opportunities)
    active_count = len([v for v in opportunities if v.status_label == "Active"])
    upcoming_count = len([v for v in opportunities if v.status_label == "Upcoming"])

    context = {
        "opportunities": opportunities,
        "total_opportunities": total_opportunities,
        "active_count": active_count,
        "upcoming_count": upcoming_count,
        "total_participants": total_participants,
    }

    return render(request, "adminpanel/volunteer_list.html", context)


# CREATE OPPORTUNITY
@login_required
@admin_required
def create_volunteer(request):
    if request.method == "POST":
        form = VolunteerOpportunityForm(request.POST,request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.organization = request.user  # admin as creator
            obj.save()
            messages.success(request, "Volunteer opportunity created successfully!")
            return redirect('adminpanel:volunteer_list')
    else:
        form = VolunteerOpportunityForm()

    return render(request, "adminpanel/volunteer_form.html", {"form": form})


# EDIT OPPORTUNITY
@login_required
@admin_required
def edit_volunteer(request, id):
    opportunity = get_object_or_404(VolunteerOpportunity, id=id)

    if request.method == "POST":
        form = VolunteerOpportunityForm(request.POST,request.FILES, instance=opportunity)
        if form.is_valid():
            form.save()
            messages.success(request, "Updated successfully!")
            return redirect('adminpanel:volunteer_list')
    else:
        form = VolunteerOpportunityForm(instance=opportunity)

    return render(request, "adminpanel/volunteer_form.html", {"form": form})


# DELETE OPPORTUNITY
@login_required
@admin_required
def delete_volunteer(request, id):
    opportunity = get_object_or_404(VolunteerOpportunity, id=id)
    opportunity.delete()
    messages.success(request, "Deleted successfully!")
    return redirect('adminpanel:volunteer_list')



@login_required
@admin_required
def volunteer_participants(request, id):
    opportunity = get_object_or_404(VolunteerOpportunity, id=id)

    # ✅ CORRECT FILTER
    participants = VolunteerRegistration.objects.filter(event_id=id)

    total_participants = participants.count()
    #active_count = participants.filter(status='active').count()
    #completed_count = participants.filter(status='completed').count()

    context = {
        "opportunity": opportunity,
        "participants": participants,
        "total_participants": total_participants,
        #"active_count": active_count,
        #"completed_count": completed_count,
    }

    return render(request, "adminpanel/participants.html", context)

@login_required
@admin_required
def mark_completed(request, id):
    p = get_object_or_404(VolunteerRegistration, id=id)
    p.status = "completed"
    p.save()
    return redirect('adminpanel:participants', id=p.event.id)