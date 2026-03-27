from django.shortcuts import render, redirect, get_object_or_404
from .forms import VolunteerRegistrationForm
from django.contrib.auth.decorators import login_required
from .models import VolunteerOpportunity, VolunteerRegistration
from django.contrib import messages
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
# Create your views here.

def showvounteers(request):
    volList = VolunteerOpportunity.objects.all()
    return render(request, 'volunteers/showevolunteers.html',{"volList":volList})

# volunteers/views.py


@login_required(login_url='login')
def volunteer_register(request, event_id):
    event = get_object_or_404(VolunteerOpportunity, id=event_id)

    if request.method == 'POST':
        form = VolunteerRegistrationForm(request.POST)
        if form.is_valid():
            # Avoid duplicates by email per event
            email = form.cleaned_data.get('email')
            if event.volunteerregistration_set.filter(email=email).exists():
                messages.warning(request, "You are already registered for this volunteer opportunity.")
                return redirect('showvolunteers')

            reg = form.save(commit=False)
            reg.event = event
            reg.save()

            # Send volunteer registration confirmation email
            try:
                subject = f"Volunteer Registration Confirmed: {event.title}"
                body = render_to_string('email/volunteer_confirmation.html', {
                    'user': request.user,
                    'event': event,
                    'registration': reg,
                })
                email_msg = EmailMessage(subject, body, settings.DEFAULT_FROM_EMAIL, [reg.email])
                email_msg.content_subtype = 'html'
                email_msg.send(fail_silently=False)
                messages.success(request, "🎉 Successfully registered as a volunteer! Confirmation email sent.")
            except Exception:
                messages.success(request, "🎉 Successfully registered as a volunteer! Could not send confirmation email.")

            return redirect('showvolunteers')
    else:
        form = VolunteerRegistrationForm()

    return render(request, 'volunteers/volunteer_form.html', {
        'form': form,
        'event': event
    })

@login_required
def volunteer_edit(request, reg_id):
    reg = get_object_or_404(VolunteerRegistration, id=reg_id, email=request.user.email)
    # time_diff = timezone.now() - reg.created_at
    # if time_diff.total_seconds() > 30 * 60:
    #     messages.error(request, "You cannot edit after 30 minutes.")
    #     return redirect('uservolunteering')
    if request.method == 'POST':
        form = VolunteerRegistrationForm(request.POST, instance=reg)
        if form.is_valid():
            form.save()
            messages.success(request, "Updated successfully.")
            return redirect('uservolunteering')
    else:
        form = VolunteerRegistrationForm(instance=reg)
    return render(request, 'volunteers/volunteer_form.html', {'form': form, 'event': reg.event})

@login_required
def volunteer_delete(request, reg_id):
    reg = get_object_or_404(VolunteerRegistration, id=reg_id, email=request.user.email)
    # time_diff = timezone.now() - reg.created_at
    # if time_diff.total_seconds() > 2 * 60 * 60:
    #     messages.error(request, "You cannot delete after 2 hours.")
    #     return redirect('uservolunteering')
    if request.method == 'POST':
        reg.delete()
        messages.success(request, "Deleted successfully.")
        return redirect('uservolunteering')
    return render(request, 'volunteers/volunteer_confirm_delete.html', {'reg': reg})