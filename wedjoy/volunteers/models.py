from django.db import models
from django.conf import settings

# Create your models here.
class VolunteerOpportunity(models.Model):

    organization = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=150)
    description = models.TextField()
    location = models.CharField(max_length=150)
    category = models.CharField(max_length=20,blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    required_hours = models.PositiveIntegerField()
    cover_image = models.ImageField(upload_to="volunteers/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "volunteerOpportunity"

    def __str__(self):
        return self.title

class VolunteerRegistration(models.Model):
    event = models.ForeignKey(VolunteerOpportunity, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    age = models.CharField(max_length=50)
    availability = models.CharField(max_length=50)
    experience = models.TextField(blank=True)
    reason = models.TextField()

    class Meta:
        db_table ="volunteerRegisteration"
    
class VolunteerParticipation(models.Model):

    STATUS_CHOICES = (
        ('active', 'Active'),
        ('completed', 'Completed'),
    )

    volunteer = models.ForeignKey(VolunteerOpportunity, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    hours_completed = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    class Meta:
        db_table ="volunteerParticipation"

    def __str__(self):
        return f"{self.user} - {self.volunteer}"