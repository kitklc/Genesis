from django.db import models
from accounts.models import User, UserProfile
from accounts.utils import send_notification
from datetime import time, date, datetime

# Create your models here.
class Vendor(models.Model):
    user = models.OneToOneField(User, related_name='user', on_delete=models.CASCADE)
    user_profile = models.OneToOneField(UserProfile, related_name='userprofile', on_delete=models.CASCADE)
    vendor_name=models.CharField(max_length=50)
    vendor_slug = models.SlugField(max_length=100, unique=True)
    vendor_license= models.ImageField(upload_to='vendor/license')
    is_approved= models.BooleanField(default=False)
    created_at= models.DateField(auto_now_add=True)
    modified_at= models.DateField(auto_now=True)
    
    def __str__(self):
        return self.vendor_name
    
    def is_open(self):
        # Check current day's opening hours.
        today_date = date.today()
        today = today_date.isoweekday()
    
        current_opening_hours = OpeningHour.objects.filter(vendor=self, day=today)
        now= datetime.now()
        current_time=now.strftime("%H:%M:%S")
        
        is_open = False  
        
        for i in current_opening_hours:
            # Strip whitespace and check for empty from_hour and to_hour
            from_hour = i.from_hour.strip() if i.from_hour else None
            to_hour = i.to_hour.strip() if i.to_hour else None
            
            # Proceed only if both from_hour and to_hour are valid
            if from_hour and to_hour:
                # Parse the time and convert to string in the same format for comparison
                start = datetime.strptime(from_hour, "%I:%M %p").time()
                end = datetime.strptime(to_hour, "%I:%M %p").time()
                
                # Compare current_time with start and end
                if start <= datetime.strptime(current_time, "%H:%M:%S").time() <= end:
                    is_open = True
                    break  # Exit the loop if a match is found

        return is_open
    
    def save(self, *args, **kwargs):
        if self.pk is not None:
            # update 
            orig =Vendor.objects.get(pk=self.pk)
            if orig.is_approved != self.is_approved:
                mail_template = 'accounts/emails/admin_approved_email.html'
                context = {
                        'user':self.user,
                        'is_approved':self.is_approved,
                        'to_email': self.user.email,
                        
                }
                if self.is_approved == True:
                     # send a notification email 
                    mail_subject = 'Félicitations ! Votre société a été approuvé'
                    send_notification(mail_subject, mail_template, context)
                else:
                    # send a notification email 
                    mail_subject = "Nous sommes désolés ! votre société n'est pas éligible pour publier vos articles sur Genesis."
                    send_notification(mail_subject, mail_template, context)
                    
        return super(Vendor, self).save(*args, **kwargs)   # super function is allow to save method Vendor class 

DAYS = [
    (1, ("Lundi")),
    (2, ("Mardi")),
    (3, ("Mercredi")),
    (4, ("Jeudi")),
    (5, ("Vendredi")),
    (6, ("Samedi")),
    (7, ("Dimanche")),
]

HOUR_OF_DAY_24 = [(time(h, m).strftime('%I:%M %p'), time(h, m).strftime('%I:%M %p')) for h in range(0, 24) for m in (0, 30)]

class OpeningHour(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    day = models.IntegerField(choices=DAYS)
    from_hour = models.CharField(choices=HOUR_OF_DAY_24, max_length=10, blank=True)
    to_hour = models.CharField(choices=HOUR_OF_DAY_24, max_length=10, blank=True)
    is_closed = models.BooleanField(default=False)

    class Meta:
        ordering = ('day', '-from_hour')
        unique_together = ('vendor', 'day', 'from_hour', 'to_hour')

    def __str__(self):
        return self.get_day_display()