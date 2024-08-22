from django.shortcuts import render,redirect
from django.http import HttpResponse 
from.forms import UserForm
from django.contrib import messages,auth
from vendor.forms import VendorForm
from .models import User,UserProfile
from .utils import detectUser,send_verification_email
from django.contrib.auth.decorators import login_required,user_passes_test
from django.core.exceptions import PermissionDenied
from django.utils.http import urlsafe_base64_decode
from django.utils.http import urlsafe_base64_decode
from datetime import datetime
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import message
from django.http.response import HttpResponse
from django.shortcuts import redirect, render

from vendor.forms import VendorForm
from .forms import UserForm


# Create your views here.
# Restrict the vendor from accessing the customer page
def check_role_vendor(user):
    if user.role == 1:
        return True
    else:
        raise PermissionDenied


# Restrict the customer from accessing the vendor page
def check_role_customer(user):
    if user.role == 2:
        return True
    else:
        raise PermissionDenied


def register_User(request):
     if request.user.is_authenticated:
        messages.warning(request, 'Vous êtes déjà connecté')
        return redirect('custDashboard')
     elif request.method =='POST':
          form =UserForm(request.POST)
          if form.is_valid():
               #password = form.cleaned_data['password']
               #user=form.save(commit=False)     
               #user.set_password(password)
               #user.role = user.CUSTOMER
               #user.save()
               
                # Create the user using create_user method
               first_name = form.cleaned_data['first_name']
               last_name = form.cleaned_data['last_name']
               username = form.cleaned_data['username']
               email = form.cleaned_data['email']
               password = form.cleaned_data['password']
               user = User.objects.create_User(first_name=first_name, last_name=last_name, username=username, email=email, password=password)
               user.role = User.CUSTOMER
               user.save()
               
               mail_subject= "Prière d'activer vitre compte"
               email_template= 'accounts/emails/account_verification_email.html'
               send_verification_email(request,user,mail_subject,email_template)
            
                                         
               messages.success(request,'Votre Compte est presque prêt; Activez-le  !')
               
               return redirect ('registeruser')
          else:
               pass
     else:
          form = UserForm()
     context = {
          'form':form,
     }
     return render(request, 'accounts/registeruser.html',context)
 
 

def registerVendor(request):
     if request.user.is_authenticated:
        messages.warning(request, 'Vous êtes déjà connecté')
        return redirect('custDashboard')
     elif request.method == 'POST':
        # store the data and create the user
        form = UserForm(request.POST)
        v_form = VendorForm(request.POST, request.FILES)
        if form.is_valid() and v_form.is_valid:
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.objects.create_User(first_name=first_name, last_name=last_name, username=username, email=email, password=password)
            user.role= User.VENDOR
            user.save()
            vendor = v_form.save(commit=False)
            vendor.user = user
            user_profile = UserProfile.objects.get(user=user)
            vendor.user_profile = user_profile
            vendor.save()
            
            mail_subject= "Prière d'activer votre compte"
            email_template= 'accounts/emails/account_verification_email.html'
            send_verification_email(request,user,mail_subject,email_template)
            messages.success(request,'Votre entreprise est maintenant enregistrée')
            return redirect('registervendor')
        else:
             print('osali erreur')
             print(form.errors)
     else:
          form = UserForm()
          v_form = VendorForm()
     
     context= {
          'form': form,
          'v_form': v_form,
     }
     
     
     return render(request, 'accounts/registervendor.html', context)
 
def activate (request,uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Congratulation!, Your Account is Activated")
        return redirect('myAccount')
    else:
        messages.error(request, 'Invalid Activation link')
    return redirect('myAccount')
   


def login(request):
    if request.user.is_authenticated:
        messages.warning(request, 'Vous êtes déjà connecté')
        return redirect('myAccount')
    elif request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            auth.login(request, user)
            messages.success(request, 'Vous êtes maintenant connecté .')
            return redirect('myAccount')
        else:
            messages.error(request, 'informations incorrectes')
            return redirect('login')
    return render(request, 'accounts/login.html')

def logout(request):
    auth.logout(request)
    messages.info(request, 'Vous êtes deconnecté.')
    return redirect('login')

@login_required(login_url='login')
def myAccount(request):
    user = request.user
    redirectUrl = detectUser(user)
    return redirect(redirectUrl)

@login_required(login_url='login')
@user_passes_test(check_role_customer)
def custDashboard(request):
     return render (request,'accounts/custDashboard.html')

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def vendorDashboard(request):
     return render (request,'accounts/vendorDashboard.html')


def ForgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']

        # Check if the Email is Exist in the databse
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email__exact=email)

            # Send reset Password Email
            mail_subject = "Réinitialisez votre mot de passe "   
            email_template = 'accounts/emails/reset_password_email.html'
            send_verification_email(request, user,mail_subject,email_template)
            messages.success(request, 'Le lien de réinitialisation du mot de passe a été envoyé à votre adresse email.')
            return redirect('login')
        else:
            messages.error(request, "Ce compte n'éxiste pas")
            return redirect('forgot_password')
    return render (request,'accounts/forgot_password.html')

def reset_password_validate(request,uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid']=uid
        messages.info(request,'Prière de réinitialiser votre mot de passe')
        return redirect('reset_password')
    else:
        messages.error(request,'Ce lien a éxpiré !')
        return redirect ('myAccount')

def reset_password(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        
        if password == confirm_password:
            pk = request.session.get('uid')
            user = User.objects.get(pk=pk)
            user.set_password(password)
            user.is_active = True
            user.save()
            messages.success(request, 'Votre mot de passe a été réinitialisé')
            return redirect('login')
        
        
        else:
            messages.error(request, 'Le mot de passe ne correspond pas!')
            return redirect('reset_password')
    return render (request,'accounts/reset_password.html')