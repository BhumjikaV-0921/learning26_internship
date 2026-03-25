from django.shortcuts import render, redirect, get_object_or_404
from .forms import VolunteerRegistrationForm
from django.contrib.auth.decorators import login_required
from .models import VolunteerOpportunity
from django.contrib import messages
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
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