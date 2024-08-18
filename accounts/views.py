from django.shortcuts import render,redirect
from django.http import HttpResponse 
from.forms import UserForm
from django.contrib import messages,auth
from vendor.forms import VendorForm
from .models import User,UserProfile
from .utils import detectUser,send_verification_email
from django.contrib.auth.decorators import login_required,user_passes_test
from django.core.exceptions import PermissionDenied

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
               
               send_verification_email(request,user)
                                         
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
 
def activate (request,uid64,token):
    #
    return


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