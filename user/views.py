from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, PasswordChangeForm
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .forms import UserRegisterForm
from django.db.models.query_utils import Q
from django.core.mail import EmailMultiAlternatives


def index(request):
    return render(request, 'user/index.html', {'title': 'index'})


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            # email section
            subject, from_email, to = 'welcome', 'joseph.sahnoun@gmail.com', email
            content = f'Welcome aboard {username}, your password is set to {form.cleaned_data.get("password1")}'
            msg = EmailMultiAlternatives(subject, content, from_email, [to])
            msg.send()
            # end mail section
            messages.success(request, f'Your account has been created ! You are now able to log in')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'user/register.html', {'form': form, 'title': 'register here'})


def Login(request):
    if request.method == 'POST':

        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            form = login(request, user)
            messages.success(request, f' welcome {username} !!')
            return redirect('index')
        else:
            user_to_connect = User.objects.filter(username=username)
            if user_to_connect.count():
                messages.info(request, f'Your password is incorrect.')
            else:
                messages.info(request, f"There's no account with username {username}, "
                                       f"SignUp to create your account.")
    form = AuthenticationForm()
    return render(request, 'user/login.html', {'form': form, 'title': 'log in'})


def password_reset_request(request):
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            associated_users = User.objects.filter(Q(email=data))
            if associated_users.exists():
                for user in associated_users:
                    # subject = "Password Reset Requested"
                    # email_template_name = "user/password/password_reset_email.txt"
                    # c = {
                    #     "email": user.email,
                    #     'domain': '127.0.0.1:8000',
                    #     'site_name': 'Website',
                    #     "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    #     "user": user,
                    #     'token': default_token_generator.make_token(user),
                    #     'protocol': 'http',
                    # }
                    # email = render_to_string(email_template_name, c)
                    # try:
                    #     send_mail(subject, email, 'admin@example.com', [user.email], fail_silently=False)
                    # except BadHeaderError:
                    #     return HttpResponse('Invalid header found.')
                    return render(request=request, template_name="user/password/password_reset_done.html",
                                  context={
                                      "password_link": f"/reset"
                                                       f"/{urlsafe_base64_encode(force_bytes(user.pk))}"
                                                       f"/{default_token_generator.make_token(user)}"
                                  })
    password_reset_form = PasswordResetForm()
    return render(request=request, template_name="user/password/password_reset.html",
                  context={"form": password_reset_form})


def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('index')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'user/password_change.html', {
        'form': form
    })
