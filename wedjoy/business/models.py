from django.db import models
from django.conf import settings


class Business(models.Model):

    APPROVAL_STATUS = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    owner = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    # Basic Information
    business_name = models.CharField(max_length=150)
    description = models.TextField()
    category = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=15)
    email = models.EmailField()

    # Location
    street_address = models.CharField(max_length=255,null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)

    zip_code = models.CharField(max_length=10, null=True, blank=True)

    latitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)

    # Business Hours
    monday_open = models.TimeField(null=True, blank=True)
    monday_close = models.TimeField(null=True, blank=True)

    tuesday_open = models.TimeField(null=True, blank=True)
    tuesday_close = models.TimeField(null=True, blank=True)

    wednesday_open = models.TimeField(null=True, blank=True)
    wednesday_close = models.TimeField(null=True, blank=True)

    thursday_open = models.TimeField(null=True, blank=True)
    thursday_close = models.TimeField(null=True, blank=True)

    friday_open = models.TimeField(null=True, blank=True)
    friday_close = models.TimeField(null=True, blank=True)

    saturday_open = models.TimeField(null=True, blank=True)
    saturday_close = models.TimeField(null=True, blank=True)

    sunday_open = models.TimeField(null=True, blank=True)
    sunday_close = models.TimeField(null=True, blank=True)

    # Photo
    photo = models.ImageField(upload_to="media/", null=True, blank=True)

    approval_status = models.CharField(
        max_length=20,
        choices=APPROVAL_STATUS,
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "Business"

    def __str__(self):
        return self.business_name
    

class promotion(models.Model):

    STATUS_CHOICES = (
        ('active', 'Active'),
        ('expired', 'Expired'),
    )

    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    title = models.CharField(max_length=150)
    description = models.TextField()
    discount_percent = models.PositiveIntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    class Meta:
        db_table = "promotion"

    def __str__(self):
        return self.title
