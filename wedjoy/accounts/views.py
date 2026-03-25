from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .models import OTP
from .forms import SendOTPForm, VerifyOTPForm, UserRegistrationWithOTPForm
from core.models import User

def send_otp_view(request):
    """View to send OTP to email"""
    if request.method == 'POST':
        form = SendOTPForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            otp_type = form.cleaned_data['otp_type']

            # Check if user exists for login OTP
            if otp_type == 'login':
                try:
                    user = User.objects.get(email=email)
                except User.DoesNotExist:
                    messages.error(request, "No account found with this email address.")
                    return redirect('accounts:send_otp')

            # Generate and save OTP
            otp_code = OTP.generate_otp()
            otp = OTP.objects.create(
                email=email,
                otp_code=otp_code,
                otp_type=otp_type
            )

            # Send OTP email
            try:
                subject = f"WedJoy - Your {otp_type.title()} OTP"
                message = render_to_string("accounts/otp_email.html", {
                    "otp_code": otp_code,
                    "otp_type": otp_type,
                    "email": email
                })
                email_msg = EmailMessage(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
                email_msg.content_subtype = "html"
                email_msg.send(fail_silently=False)

                messages.success(request, f"OTP sent to {email}. Please check your email.")
                return redirect('accounts:verify_otp')

            except Exception as e:
                messages.error(request, "Failed to send OTP. Please try again.")
                return redirect('accounts:send_otp')

    else:
        form = SendOTPForm()

    return render(request, 'accounts/send_otp.html', {'form': form})

def verify_otp_view(request):
    """View to verify OTP"""
    if request.method == 'POST':
        form = VerifyOTPForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            otp_code = form.cleaned_data['otp_code']
            otp_type = form.cleaned_data['otp_type']

            # Get the latest non-expired OTP for this email and type
            try:
                otp = OTP.objects.filter(
                    email=email,
                    otp_type=otp_type,
                    is_verified=False
                ).filter(
                    expires_at__gt=timezone.now()
                ).latest('created_at')

                if otp.otp_code == otp_code:
                    otp.is_verified = True
                    otp.save()

                    if otp_type == 'registration':
                        # Redirect to registration completion
                        request.session['verified_email'] = email
                        messages.success(request, "OTP verified successfully. Please complete your registration.")
                        return redirect('accounts:register_with_otp')

                    elif otp_type == 'login':
                        # Auto login the user
                        try:
                            user = User.objects.get(email=email)
                            login(request, user)
                            messages.success(request, "Login successful!")
                            return redirect('home')
                        except User.DoesNotExist:
                            messages.error(request, "User account not found.")
                            return redirect('accounts:send_otp')

                    elif otp_type == 'password_reset':
                        # Redirect to password reset
                        request.session['reset_email'] = email
                        messages.success(request, "OTP verified. Please set your new password.")
                        return redirect('accounts:password_reset_confirm')

                else:
                    messages.error(request, "Invalid OTP code.")

            except OTP.DoesNotExist:
                messages.error(request, "OTP not found or expired. Please request a new one.")

    else:
        # Pre-fill email from session if available
        initial_data = {}
        if 'email' in request.GET:
            initial_data['email'] = request.GET['email']
        form = VerifyOTPForm(initial=initial_data)

    return render(request, 'accounts/verify_otp.html', {'form': form})

def register_with_otp_view(request):
    """Complete registration after OTP verification"""
    verified_email = request.session.get('verified_email')
    if not verified_email:
        messages.error(request, "Please verify your email first.")
        return redirect('accounts:send_otp')

    if request.method == 'POST':
        form = UserRegistrationWithOTPForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            user.is_active = True  # Activate account after OTP verification
            user.save()

            # Clear session
            del request.session['verified_email']

            # Send welcome email
            try:
                subject = "Welcome to WedJoy!"
                message = render_to_string("email/welcome_email.html", {"user": user})
                email_msg = EmailMessage(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
                email_msg.content_subtype = "html"
                email_msg.send(fail_silently=False)
            except:
                pass

            messages.success(request, "Registration completed successfully! You can now login.")
            return redirect('login')

    else:
        form = UserRegistrationWithOTPForm(initial={'email': verified_email})
        # Make email field readonly
        form.fields['email'].widget.attrs['readonly'] = True

    return render(request, 'accounts/register_with_otp.html', {'form': form})

@login_required
def change_password_view(request):
    """Change password view"""
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if not request.user.check_password(current_password):
            messages.error(request, "Current password is incorrect.")
            return redirect('accounts:change_password')

        if new_password != confirm_password:
            messages.error(request, "New passwords do not match.")
            return redirect('accounts:change_password')

        if len(new_password) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
            return redirect('accounts:change_password')

        request.user.set_password(new_password)
        request.user.save()
        from django.contrib.auth import update_session_auth_hash
        update_session_auth_hash(request, request.user)

        messages.success(request, "Password changed successfully!")
        return redirect('accounts:change_password')

    return render(request, 'accounts/change_password.html')

def forgot_password_view(request):
    """Forgot password - send OTP"""
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            # Create password reset OTP
            otp_code = OTP.generate_otp()
            otp = OTP.objects.create(
                user=user,
                email=email,
                otp_code=otp_code,
                otp_type='password_reset'
            )

            # Send email
            try:
                subject = "WedJoy - Password Reset OTP"
                message = render_to_string("accounts/password_reset_email.html", {
                    "otp_code": otp_code,
                    "user": user
                })
                email_msg = EmailMessage(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
                email_msg.content_subtype = "html"
                email_msg.send(fail_silently=False)

                messages.success(request, f"Password reset OTP sent to {email}")
                return redirect('accounts:verify_otp')

            except Exception as e:
                messages.error(request, "Failed to send email. Please try again.")

        except User.DoesNotExist:
            messages.error(request, "No account found with this email address.")

    return render(request, 'accounts/forgot_password.html')

def password_reset_confirm_view(request):
    """Reset password after OTP verification"""
    reset_email = request.session.get('reset_email')
    if not reset_email:
        messages.error(request, "Please verify your email first.")
        return redirect('accounts:forgot_password')

    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('accounts:password_reset_confirm')

        if len(new_password) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
            return redirect('accounts:password_reset_confirm')

        try:
            user = User.objects.get(email=reset_email)
            user.set_password(new_password)
            user.save()

            # Clear session
            del request.session['reset_email']

            messages.success(request, "Password reset successfully! You can now login.")
            return redirect('login')

        except User.DoesNotExist:
            messages.error(request, "User not found.")

    return render(request, 'accounts/password_reset_confirm.html')
