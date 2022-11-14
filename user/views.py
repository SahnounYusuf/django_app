import csv
import io

from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, PasswordChangeForm
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .forms import UserRegisterForm, EmployeeForm
from django.db.models.query_utils import Q
from django.core.mail import EmailMultiAlternatives

from .models import Employee, Users


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
        authenticated_user = authenticate(request, username=username, password=password)
        if authenticated_user is not None:
            user = Users.objects.get(username=username)
            print(user.is_admin())
            form = login(request, user)
            messages.success(request, f' welcome {username} !!')
            return render(request, 'user/index.html', {'form': form, 'title': 'Welcome'})
        else:
            user_to_connect = Users.objects.filter(username=username)
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
            associated_users = Users.objects.filter(Q(email=data))
            if associated_users.exists():
                for user in associated_users:
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


def upload(request):
    # # declaring template
    template = 'user/uploads.html'
    data = Employee.objects.all()
    # prompt is a context variable that can have different values      depending on their context
    prompt = {
        'order': 'Order of the CSV should be name, email, address, phone, profile',
        'profiles': data,
        'file_not_selected': False
    }
    # GET request returns the value of the data with the specified key.
    if request.method == "GET":
        return render(request, template, prompt)
    try:
        csv_file = request.FILES['file']
    except MultiValueDictKeyError:
        prompt['file_not_selected'] = True
        return render(request, template, prompt)
    if not csv_file.name.endswith('.csv'):
        messages.error(request, 'THIS IS NOT A CSV FILE')
    data_set = csv_file.read().decode('UTF-8')
    # set up a stream which is when we loop through each line we are able to handle a data in a stream
    io_string = io.StringIO(data_set)
    next(io_string)
    existing_employees = []
    for column in csv.reader(io_string, delimiter=',', quotechar="|"):
        employee = Employee.objects.filter(username=column[0])
        if employee.count():
            existing_employee = Employee.objects.get(username=column[0])
            existing_employees.append(existing_employee)
            if existing_employee.username != column[0]:
                existing_employee.username = column[0]

            if existing_employee.password != column[1]:
                existing_employee.password = column[1]

            if existing_employee.role != column[2]:
                existing_employee.role = column[2]

            names = [name for name in existing_employee.name.split(" ")]
            if column[3] not in names:
                existing_employee.name += f' {column[3]}'

            if existing_employee.email != column[4]:
                existing_employee.email = column[4]

            addresses = [address for address in existing_employee.address.split(" ")]
            if column[5] not in addresses:
                existing_employee.address += f' {column[5]}'

            countries = [country for country in existing_employee.country.split(" ")]
            if column[6] not in countries:
                existing_employee.country += f' {column[6]}'

            companies = [company for company in existing_employee.company.split(" ")]
            if column[7] not in companies:
                existing_employee.company += f' {column[7]}'
            existing_employee.save()
        else:
            _, created = Employee.objects.update_or_create(
                username=column[0],
                password=column[1],
                role=column[2],
                name=column[3],
                email=column[4],
                address=column[5],
                country=column[6],
                company=column[7]
            )
            user_to_connect = Users.objects.filter(username=column[0])
            if not user_to_connect.count():
                print(f'creating user with cred:'
                      f'\nusername: {column[0]}'
                      f'\npassword: {column[1]}'
                      f'\nemail: {column[4]}')
                Users.objects.create_user(
                    username=column[0],
                    password=column[1],
                    role=column[2],
                    email=column[4],
                )

    context = {'profiles': data, 'existing': existing_employees}
    return render(request, template, context)


def edit(request, pk=None):
    item = get_object_or_404(Employee, pk=pk)
    form = EmployeeForm(request.POST or None,
                        request.FILES or None, instance=item)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            form.save()
            return redirect('profile_upload')
    return render(request, 'user/edit.html', {'form': form})
