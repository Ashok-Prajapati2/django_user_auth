from django.utils.http import urlsafe_base64_encode , urlsafe_base64_decode
from django.core.mail import EmailMessage
from .token import custom_token_generator
from django.shortcuts import render , redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate , login,logout
from django.contrib import messages
from django.core.mail import send_mail
from auth_django import settings
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes , force_str



def home(request):
    user = None
    if request.user.is_authenticated:
        user = request.user.first_name
    return render(request,"home.html",{'fname': user})

def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            first = user.first_name
            return render(request,'home.html', {'fname':first})  
        else:
            messages.error(request, "Incorrect username or password.")
            return redirect('login')  
        
    return render(request, "login.html")

def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        firstname = request.POST.get("firstname")
        lastname = request.POST.get("lastname")
        password = request.POST.get("password")
        repassword = request.POST.get("repassword")
        
        if len(username) < 3 or len(username) > 10:
            messages.error(request, "Username Error: Username must be between 3 and 10 characters")
            return redirect('register')
        
        if len(password) < 8 or len(password) > 15 or password != repassword:
            messages.error(request, "Password Error: Password must be between 8 and 15 characters and match the confirm password")
            return redirect('register')

        
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "username already exists")
            return redirect('register')
        if User.objects.filter(email=email).exists():
            messages.error(request, "email already exists")
            return redirect('register')
        
        myuser = User.objects.create_user(username,email, password)
        myuser.first_name = firstname
        myuser.last_name = lastname
        myuser.is_active = False
        myuser.save()
        messages.success(request,"Register successful")
        
        # email 
        
        subject = "welcome to my project ! "
        message = "welcome  "+ myuser.first_name +" !\n\n"+"Thank you for viewing my project. \n We have also send a confirmation email to you \n Please confirm your email \n\n Thank you \n ASHOK KUMAR \n\n http://proscience24.com"
        from_email  = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        send_mail(subject, message,from_email,to_list)
        
        #email address confirmation
        
        current_site = get_current_site(request)
        email_subject = "confirmation email"
        to_email = [myuser.email]
        message2 = render_to_string("confirmation_email.html",{
            'name': myuser.first_name,
            'domain': current_site.domain,
            'uid':urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token': custom_token_generator.make_token(myuser)
            
        })
        email = EmailMessage(email_subject, message2, to=to_email)
        email.send(fail_silently=True)
        
        
        
       
        if email.send():
            messages.success(request, f'Dear {myuser.first_name}, please go to you email {to_email} inbox and click on \
            received activation link to confirm and complete the registration. Note: Check your spam folder.')
        else:
            messages.error(request, f'Problem sending confirmation email to {to_email}, check if you typed it correctly.')
        
        return redirect('login')

    return render(request,"register.html")

        
        
        

def logout_view(request):
    logout(request)
    messages.success(request,"Logout successful")
    return redirect('home')


def activate_view(request , uid64,token):
    
    
    try:
        uid = force_str(urlsafe_base64_decode(uid64))
        myuser = User.objects.get(pk=uid)
    except Exception as e:
        myuser = None
        messages.error(request, e)
        
    if myuser is not None and custom_token_generator.check_token(myuser,token):
        myuser.is_active = True
        myuser.save()
        login(request, myuser)
        
        first = myuser.first_name
        return render(request,'home.html', {'fname':first})
    else:
        return render(request,"activate_failed.html")
    