from django.shortcuts import render,HttpResponse,redirect
from .models import *
from django.contrib import messages
from django.contrib.auth.models import User,Group
from django.contrib.auth import login,logout,authenticate
from django.views.decorators.csrf import csrf_exempt
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.utils.encoding import force_bytes,force_str,DjangoUnicodeDecodeError
from .utils import GenerateToken,generate_token,PasswordResetTokenGenerator
from django.core.mail import EmailMessage
from django.conf import settings
import threading
from django.views.generic import View

class EmailThread(threading.Thread):
    def __init__(self,email_msg):
        self.email_msg=email_msg
        threading.Thread.__init__(self)
    def run(self):
        return self.email_msg.send()

def index(request):
    return render(request,'index.html')

def signup(request):
    if request.method=="POST":
        fn=request.POST.get("fn")
        ln=request.POST.get("ln")
        un=request.POST.get("un")
        email=request.POST.get("email")
        pw1=request.POST.get("pw1")
        pw2=request.POST.get("pw2")

        if pw1!=pw2:
            messages.warning(request,"password doesnt match")
            return render(request,"auth/signup.html")
        try:
            if User.objects.filter(username=un).exists():
                messages.warning(request,"User already exist")  ## info blue color
                return render(request,"auth/signup.html")
             
        except Exception as e:
            messages.warning(request,f"something went wrong in {str(e)}")

        user=User.objects.create_user(first_name=fn,last_name=ln,username=un, email=email, password=pw1)
        user.is_active=False
        user.save()
        ### Account activation through email link
        current_site=get_current_site(request)
        email_sub="ACTIVATE YOUR ACCOUNT IN HOMESTAY"
        msg=render_to_string("auth/activate_mail.html",{
            "user":user,
            "domain":current_site.domain,
            "uid":urlsafe_base64_encode(force_bytes(user.pk)),
            "token":generate_token.make_token(user)
        })
        email_msg=EmailMessage(email_sub,msg,settings.EMAIL_HOST_USER, [email])
        EmailThread(email_msg).start()
        messages.info(request,"We have sent activation link to your mail, Activate your account by clicking link on your email")
        if user.is_active==True:
            messages.success(request,"User registered successfully")
            return redirect("in")
    return render(request,"auth/signup.html")

class AccountActivateView(View):
    def get(self,request,uidb64,token):
        try:
            uid=force_str(urlsafe_base64_decode(uidb64))
            user=User.objects.get(id=uid)
            print(f"Decoded uid: {uid}, User: {user}")
        except Exception as e:
            messages.warning(request, f"something wrong in {str(e)}")

        try:
            if user is not None and generate_token.check_token(user,token):
                user.is_active=True
                user.save()
                messages.success(request,"account activation success. You can login into your account")
                return render (request,"auth/log.html")
            else:
                messages.warning(request,"Activation link is invalid")
                return render (request, "activate_fail.html")
                
        except Exception as e:
            messages.warning(request, f"Activation link is invalid {str(e)}")
            return render (request, "auth/activate_fail.html")

def log(request):
    try:
        if request.method=="POST":
            un=request.POST.get("un")
            pw1=request.POST.get("pw1")
                
            user=authenticate(request,username=un,password=pw1)
            if user is not None:
                login(request,user)
                messages.success(request,"user logged in successfully")
                return render(request,'index.html')
            else:
                messages.info(request,"Invalid credentials")
            
    except Exception as e:
        print("error", str(e))
    return render (request,"auth/log.html")

def lout(request):
    logout(request)
    messages.success(request,f"user logged out successfully")
    return redirect("index")
    
class ReqResetPWView(View):
    def get (self,request):
        return render(request,"auth/reset_pw_page.html")
    
    def post (self,request):
        if request.method=="POST":
            email=request.POST.get("email")
            user=User.objects.filter(email=email)

            if user.exists():
                current_site=get_current_site(request)
                email_sub="Reset Your Homesless Account Password"
                msg=render_to_string("auth/reset_pw_mail.html",{
                    "user":user[0],
                    "domain":current_site.domain,
                    "uid":urlsafe_base64_encode(force_bytes(user[0].pk)),
                    "token":PasswordResetTokenGenerator().make_token(user=user[0]),
                })

                email_msg=EmailMessage(email_sub,msg,settings.EMAIL_HOST_USER,[email])
                EmailThread(email_msg).start()
                messages.info(request,"WE HAVE SENT YOU AN EMAIL FOR RESET THE PASSWORD")
                return render (request,"auth/reset_pw_page.html")



class ResetNewPWView(View):
    def get(self,request,uidb64,token):
        context={"uidb64":uidb64,
                 "token":token}
        try:

            uid=force_str(urlsafe_base64_decode(uidb64))
            user=User.objects.get(id=uid)
            print("Decoded uid in get request: {uid}, User: {user}")
            token=token
            if not PasswordResetTokenGenerator.check_token(user,token):
                messages.warning(request,"password reset link is invalid please try again")
                return render (request,"auth/reset_pw_page.html")
            
        except Exception as e:
            messages.warning(request,"error in get request"+ str(e))
            print("error in get request while resetting new password" ,str(e))
        return render (request,"auth/new_pw.html",context)
    
    def post(self,request,uidb64,token):
        context={"uidb64":uidb64,
                 "token":token}


        pw1=request.POST.get("pw1")
        pw2=request.POST.get("pw2")

        if pw1!=pw2:
            messages.warning(request,"password doesnt match enter correct password")
            return render (request,"auth/new_pw.html",context)
        try:

            uid=force_str(urlsafe_base64_decode(uidb64))
            user=User.objects.get(pk=uid)
            print("Decoded uid in post request: {uid}, User: {user}")
            user.set_password(pw1)
            user.save()
            messages.success(request, "password reset success please login with your new password")
            return render(request,"auth/log.html")

        except Exception as e:
            messages.error(request,"something went wrong & error in saving the new password",str(e))
            print("error in last exception", str(e))
            return render (request,"auth/new_pw.html",context)

        return render (request,"auth/new_pw.html",context)
        



    
