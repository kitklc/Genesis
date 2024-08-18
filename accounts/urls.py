from django.urls import path
from . import views

urlpatterns = [
    
    path('registeruser/', views.register_User, name='registeruser'),
    path('registervendor/', views.registerVendor, name='registervendor'),
    
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('custDashboard/', views.custDashboard, name='custDashboard'),
    path('vendorDashboard/', views.vendorDashboard, name='vendorDashboard'),
    
    path('myAccount/', views.myAccount, name='myAccount'),
    
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),

]