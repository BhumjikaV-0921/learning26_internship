# core/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import UserSignupForm, UserLoginForm, UserUpdateProfile, UserPasswordChangeForm, UserPostForm, ContactForm
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from events.models import Event,EventRegistration
from volunteers.models import VolunteerRegistration
from business.models import Business
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash, logout
from .models import UserPost
import os
from django.utils import timezone

def aboutus(request):
    return render(request, "core/aboutus.html")

def userSignupView(request):
    if request.method == "POST":    
        form = UserSignupForm(request.POST,request.FILES)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Successfully registered!")

            # Send welcome email (non-blocking)
            subject = "Welcome to WedJoy!"
            message = render_to_string("email/welcome_email.html", {"user": user})
            try:
                email = EmailMessage(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
                email.content_subtype = "html"
                email.send(fail_silently=False)
                messages.success(request, "A welcome email has been sent to your inbox.")
            except Exception as e:
                messages.warning(request, "Account created, but we could not send a welcome email right now.")

            return redirect("login")
    else:
        form = UserSignupForm()
    return render(request, "core/signup.html", {"form": form})

def userLoginView(request):
    if request.method == "POST":
        form = UserLoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                email=form.cleaned_data["email"],
                password=form.cleaned_data["password"],
            )
            if user:
                login(request, user)
                messages.success(request, "Welcome back!")
                if user.role == "owner":
                    return redirect("localcommunity:businessownerdashboard")
                elif user.role == "event_organizer":
                    return redirect("localcommunity:eventstudio")
                else:
                    return redirect("home")
            else:
                messages.error(request, "Invalid email or password.")
    else:
        form = UserLoginForm()
    return render(request, "core/login.html", {"form": form})

def custom_logout(request):
    logout(request)
    messages.success(request, "Successfully logout")
    return redirect("home")

@login_required
def Userprofile(request):
    user = request.user

    # Get user's posts
    from community.models import Post
    user_posts = Post.objects.filter(user=user).prefetch_related('comments')

    # Get user's comments
    from community.models import Comment
    user_comments = Comment.objects.filter(user=user).select_related('post')

    # Get user's registered events
    user_registrations = EventRegistration.objects.filter(user=user).select_related('event')

    # Get user's payment history
    from payments.models import Payment
    user_payments = Payment.objects.filter(user=user).order_by('-created_at')

    context = {
        'user': user,
        'user_posts': user_posts,
        'user_comments': user_comments,
        'user_registrations': user_registrations,
        'user_payments': user_payments,
    }

    return render(request, "core/Userprofile.html", context)


def home(request):
    events = Event.objects.order_by('-id')[:3]
    business = Business.objects.order_by('-id')[:3]
    return render(request, "core/index.html", {"events": events , "business" : business})

@login_required
def userupdateprofile(request):
    user = request.user

    if request.method == 'POST':
        form = UserUpdateProfile(request.POST,request.FILES,instance=user)

        if form.is_valid():
            # ✅ directly save profile
            form.save()

            messages.success(request, "Profile updated successfully")
            return redirect("userupdateprofile") 

        else:
            print(form.errors)

    else:
        form = UserUpdateProfile(instance=user)

    return render(request, "core/userupdateprofile.html",{"form":form}) 

@login_required
def userregisteredevents(request):
    registrations = EventRegistration.objects.filter(user=request.user)
    
    return render(request, "core/userregisteredevents.html", {"registrations": registrations})
 



@login_required
def uservolunteering(request):
   vregistrations = VolunteerRegistration.objects.filter(email=request.user.email)
   now = timezone.now()
   for reg in vregistrations:
       # time_diff = (now - reg.created_at).total_seconds()
       # reg.can_edit = time_diff < 1800  # 30 minutes
       # reg.can_delete = time_diff < 7200  # 2 hours
       reg.can_edit = True  # Temporary
       reg.can_delete = True  # Temporary
       reg.is_expired = reg.event.end_date < now.date()
   return render(request, "core/uservolunteering.html", {"registrations": vregistrations})

def usercomments(request):
    
    if request.method == "POST":
        form = UserPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user   # save user
            post.save()
            return redirect('core:usercomments')
    else:
        form = UserPostForm()

    posts = UserPost.objects.all().order_by('-created_at')

    return render(request, "core/usercomments.html", {
        "form": form,
        "posts": posts
    })
 


@login_required
def usersecurity(request):
    user = request.user

    if request.method == 'POST':
        form = UserPasswordChangeForm(request.POST)

        if form.is_valid():
            current_password = form.cleaned_data.get('current_password')
            new_password = form.cleaned_data.get('new_password')
            confirm_password = form.cleaned_data.get('confirm_password')

            if not user.check_password(current_password):
                messages.error(request, "Current password is incorrect")
                return render(request, "core/usersecurity.html", {"form": form})

            if new_password != confirm_password:
                messages.error(request, "New passwords do not match")
                return render(request, "core/usersecurity.html", {"form": form})

            user.set_password(new_password)
            user.save()

            update_session_auth_hash(request, user)

            messages.success(request, "Password updated successfully")
            return redirect("core:usersecurity")   # reload same page

    else:
        form = UserPasswordChangeForm()

    return render(request, "core/usersecurity.html", {"form": form})

def professional_networking(request):
    return render(request, "core/professional_networking.html")

def job_listings(request):
    return render(request, "core/job_listings.html")

def consulting(request):
    return render(request, "core/consulting.html")

def premium_membership(request):
    return render(request, "core/premium_membership.html")

def careers(request):
    return render(request, "core/careers.html")
    

# -------  contact us page -------
def contactus(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('contactus')
            messages.success(request, "Form submitted successfully!")
    else:
        form = ContactForm()
    return render(request, 'core/contactus.html', {'form': form})