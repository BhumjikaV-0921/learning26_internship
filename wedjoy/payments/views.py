import json
import razorpay
import qrcode
import uuid
from io import BytesIO
from django.core.files.base import ContentFile
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from events.models import Event, EventRegistration
from .models import Payment

# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

@login_required
def create_payment_order(request, event_id):
    """Create payment QR code for event registration"""
    event = get_object_or_404(Event, id=event_id)

    # Check if user is already registered
    if EventRegistration.objects.filter(event=event, user=request.user).exists():
        messages.warning(request, "You are already registered for this event.")
        return redirect('events', event_id=event.id)

    # Check participant limit
    total_registered = EventRegistration.objects.filter(event=event).count()
    if total_registered >= event.max_participants:
        messages.error(request, "Event is full.")
        return redirect('events', event_id=event.id)

    if event.registration_fee == 0:
        # Free event - register directly
        registration = EventRegistration.objects.create(
            event=event,
            user=request.user,
            amount=0,
            payment_status='paid'
        )
        messages.success(request, "Successfully registered for the event!")
        return redirect('events', event_id=event.id)

    # Paid event - generate QR code for payment
    try:
        # Generate unique transaction ID
        transaction_id = str(uuid.uuid4())[:8].upper()

        # Create UPI payment string
        upi_string = f"upi://pay?pa={settings.UPI_ID}&pn=WedJoy&am={event.registration_fee}&cu=INR&tn=Event Registration - {event.title[:20]}&tr={transaction_id}"

        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(upi_string)
        qr.make(fit=True)

        # Create QR code image
        img = qr.make_image(fill_color="black", back_color="white")

        # Save QR code to BytesIO
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)

        # Create payment record
        payment = Payment.objects.create(
            user=request.user,
            amount=event.registration_fee,
            payment_method='qr_code',
            razorpay_order_id=transaction_id  # Using this field for transaction ID
        )

        # Save QR code image
        qr_filename = f"qr_{transaction_id}.png"
        payment.qr_code.save(qr_filename, ContentFile(buffer.getvalue()), save=True)

        context = {
            'event': event,
            'amount': event.registration_fee,
            'transaction_id': transaction_id,
            'upi_string': upi_string,
            'qr_code_url': payment.qr_code.url,
            'payment': payment
        }

        return render(request, 'payments/payment_qr.html', context)

    except Exception as e:
        messages.error(request, f"Payment QR generation failed: {str(e)}")
        return redirect('events', event_id=event.id)

@csrf_exempt
@require_POST
def payment_success(request):
    """Handle successful payment from QR code"""
    try:
        data = json.loads(request.body)
        transaction_id = data.get('transaction_id')
        event_id = data.get('event_id')
        payment_method = data.get('payment_method', 'UPI')

        # Get payment record
        payment = Payment.objects.get(razorpay_order_id=transaction_id)
        payment.payment_status = 'completed'
        payment.razorpay_payment_id = f"QR_{transaction_id}"  # Using QR prefix for identification
        payment.save()

        # Create event registration
        event = get_object_or_404(Event, id=event_id)
        registration = EventRegistration.objects.create(
            event=event,
            user=payment.user,
            amount=payment.amount,
            payment_status='paid',
            payment_id=payment.razorpay_payment_id
        )

        # Send email with receipt and ticket
        send_payment_receipt_and_ticket(payment, registration, event)

        return JsonResponse({
            'status': 'success',
            'message': 'Payment successful! Receipt and ticket sent to your email.',
            'registration_id': registration.id
        })

    except Exception as e:
        return JsonResponse({'status': 'failed', 'message': str(e)})

def send_payment_receipt_and_ticket(payment, registration, event):
    """Send payment receipt and event ticket via email"""
    try:
        subject = f"Payment Receipt & Event Ticket - {event.title}"

        # Generate ticket QR code for entry
        ticket_id = f"TICKET_{registration.id}_{uuid.uuid4().hex[:8].upper()}"

        # Create ticket QR code
        ticket_qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=8,
            border=2,
        )
        ticket_data = f"Event:{event.id}|User:{payment.user.id}|Ticket:{ticket_id}|Reg:{registration.id}"
        ticket_qr.add_data(ticket_data)
        ticket_qr.make(fit=True)

        # Create ticket QR code image
        ticket_img = ticket_qr.make_image(fill_color="black", back_color="white")

        # Save ticket QR code to BytesIO for email
        ticket_buffer = BytesIO()
        ticket_img.save(ticket_buffer, format='PNG')
        ticket_buffer.seek(0)

        # Convert to base64 for embedding in email
        import base64
        ticket_qr_base64 = base64.b64encode(ticket_buffer.getvalue()).decode('utf-8')
        ticket_qr_data_url = f"data:image/png;base64,{ticket_qr_base64}"

        # Prepare context for email
        context = {
            'user': payment.user,
            'payment': payment,
            'registration': registration,
            'event': event,
            'transaction_id': payment.razorpay_order_id,
            'payment_method': payment.payment_method,
            'amount': payment.amount,
            'payment_date': payment.created_at,
            'ticket_id': ticket_id,
            'qr_code_url': ticket_qr_data_url,  # Ticket QR code for email
        }

        # Render HTML email content
        html_content = render_to_string('email/payment_receipt_ticket.html', context)

        # Create email
        email = EmailMessage(
            subject=subject,
            body=html_content,
            from_email=settings.EMAIL_HOST_USER,
            to=[payment.user.email]
        )
        email.content_subtype = "html"

        # Send email
        email.send(fail_silently=False)

    except Exception as e:
        # Log error but don't break payment flow
        print(f"Email sending failed: {str(e)}")

@csrf_exempt
@require_POST
def payment_failed(request):
    """Handle failed payment"""
    try:
        data = json.loads(request.body)
        razorpay_order_id = data.get('razorpay_order_id')

        # Update payment status
        payment = Payment.objects.get(razorpay_order_id=razorpay_order_id)
        payment.payment_status = 'failed'
        payment.save()

        return JsonResponse({'status': 'failed', 'message': 'Payment failed'})

    except Exception as e:
        return JsonResponse({'status': 'failed', 'message': str(e)})

@login_required
def payment_history(request):
    """View user's payment history"""
    payments = Payment.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'payments/payment_history.html', {'payments': payments})
