from django.shortcuts import render,redirect
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import CustomUser,UserProfile

from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator

from django.contrib import messages

from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from .models import CustomUser
from blog_app.models import CreateBlog

import random
from django.core.cache import cache

from twilio.rest import Client

from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy

def send_mobile_otp(phone, otp):
     # add here "account_sid" and auth_toke 
   
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        body=f'Your OTP for registration is {otp}',
        from_='+12548294504',  # Your Twilio number
        to=f'+{phone}'  # User's mobile number
    )
    return message.sid


def generate_otp():
    return random.randint(100000,999999)

def register_view(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('username')  # Use email as username
        phone = request.POST.get('phone')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            error_message = 'Passwords do not match.'
            return render(request, 'auth_app/register.html', {'error_message': error_message})

        if CustomUser.objects.filter(username=email).exists():
            error_message = 'Username (email) already exists.'
            return render(request, 'auth_app/register.html', {'error_message': error_message})

        # Create the user and set is_active to False until email is confirmed
        user = CustomUser.objects.create_user(
            username=email,  # Using email as username
            phone = phone,
            password=password1,
            first_name=first_name,
            last_name=last_name,
            is_active=False  # Account is inactive until email confirmation
        )
        
        otp = generate_otp()
        
        cache.set(f'otp_{user.username}',otp,timeout=300)

        # The signal will automatically create the UserProfile here.

        # Send confirmation otp
        mail_subject = 'Activate your account.'
        message = f'Your OTP for account activation is: {otp}'
        send_mail(mail_subject, message, settings.EMAIL_HOST_USER, [user.username])
        
        
        otp_mobile = generate_otp()
        cache.set(f'mobile_otp_{user.username}', otp_mobile, timeout=300)
        send_mobile_otp(phone, otp_mobile)

        # Store mobile number in the user's profile
        user_profile = UserProfile.objects.get(user=user)
        user_profile.phone = phone
        user_profile.save()
        
        messages.success(request,'your account has been created successfully!')
        return redirect('verify_otp',user_id = user.id)
    
    return render(request, 'auth_app/register.html')


def verify_otp_view(request, user_id):
    if request.method == 'POST':
        email_otp_input = request.POST.get('email_otp')
        mobile_otp_input = request.POST.get('mobile_otp')
        user = CustomUser.objects.get(id=user_id)
        
        stored_email_otp = cache.get(f'otp_{user.username}')
        stored_mobile_otp = cache.get(f'mobile_otp_{user.username}')

        if stored_email_otp and str(stored_email_otp) == email_otp_input and \
           stored_mobile_otp and str(stored_mobile_otp) == mobile_otp_input:
            # Both OTPs are correct, activate the user
            user.is_active = True
            user.save()
            return redirect('login')
        else:
            error_message = 'Invalid or expired OTP for email or mobile.'
            return render(request, 'auth_app/verify_otp.html', {'error_message': error_message})

    return render(request, 'auth_app/verify_otp.html')



# def verify_otp_view(request, user_id):
#     if request.method == 'POST':
#         email_otp_input = request.POST.get('email_otp')
#         phone_otp_input = request.POST.get('phone_otp')
#         user = CustomUser.objects.get(id=user_id)
        
#         stored_email_otp = cache.get(f'otp_{user.username}')
        

#         if stored_email_otp and str(stored_email_otp) == email_otp_input:
#             # OTP is correct, activate the user
#             user.is_active = True
#             user.save()
#             return redirect('login')
#         else:
#             error_message = 'Invalid or expired OTP.'
#             return render(request, 'auth_app/verify_otp.html', {'error_message': error_message})

#     return render(request, 'auth_app/verify_otp.html')



def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Authenticate the user
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.is_active:
            login(request, user)
            return redirect('blogs')  
        else:
            error_message = 'Invalid username or password.'
            return render(request, 'auth_app/login.html', {'error_message': error_message})
        
    messages.success(request,'you are successfully logged in!')
    return render(request, 'auth_app/login.html')

@login_required(login_url='login')
def dashboard_view(request):
    return render(request, 'blog/dashboard.html') 

def logout_view(request):
    logout(request)
    return redirect('login')


def user_profile_view(request):
    # Get the logged-in user's profile (assuming it's already created by the signal)
    profile = request.user.userprofile
    user_blogs = CreateBlog.objects.filter(author=request.user)  # Get blogs created by the logged-in user

    if request.method == 'POST':
        # Update basic user info (from registration)
        request.user.first_name = request.POST.get('first_name')
        request.user.last_name = request.POST.get('last_name')
        request.user.email = request.POST.get('email')
        request.user.save()

        # Update profile-specific fields
        profile.address = request.POST.get('address')
        profile.pincode = request.POST.get('pincode')
        profile.street = request.POST.get('street')
        profile_image = request.FILES.get('profile_image')

        if profile_image:
            profile.profile_image = profile_image

        profile.save()
        
        

        return redirect('profile')

    return render(request, 'auth_app/user_profile.html', {'profile': profile, 'blogs': user_blogs})




class ChangePasswordView(PasswordChangeView):
    template_name = 'auth_app/change-password.html'
    success_url = reverse_lazy('login')  # Redirect to the profile page after password change
    success_message = "Your password was successfully updated!"
    login_url = 'login'
