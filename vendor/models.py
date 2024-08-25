from django.db import models
from accounts.models import User, UserProfile
from accounts.utils import send_notification

# Create your models here.
class Vendor(models.Model):
    user= models.OneToOneField(User,related_name='user',on_delete=models.CASCADE)
    user_profile= models.OneToOneField(UserProfile,related_name='userprofile',on_delete=models.CASCADE)
    vendor_name=models.CharField(max_length=50)
    vendor_license= models.ImageField(upload_to='vendor/license')
    is_approved= models.BooleanField(default=False)
    created_at= models.DateField(auto_now_add=True)
    modified_at= models.DateField(auto_now=True)
    
    def __str__(self):
        return self.vendor_name
    
    def save(self, *args, **kwargs):
        if self.pk is not None:
            # update 
            orig =Vendor.objects.get(pk=self.pk)
            if orig.is_approved != self.is_approved:
                mail_template = 'accounts/emails/admin_approved_email.html'
                context = {
                        'user':self.user,
                        'is_approved':self.is_approved,
                        
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