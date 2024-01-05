from django.contrib import auth
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect

from .forms import RegistrationForm, LoginForm


def login_page(request):
    """
    This method handles Login Page requests for Sign In and Sign Up.
    :param: Request
    :return: Login page requests
    """

    # In case admin user is already logged in
    if auth.get_user(request).is_superuser:
        return redirect('admin_home')

    # In case non-admin user is already logged in
    if auth.get_user(request).is_authenticated:
        return redirect('home')

    # In case toggler of login is selected
    if request.method == 'GET' and 'signin' in request.GET["action"]:
        form = LoginForm()
        return render(request, 'register/login.html', {'form': form})

    # In case toggler of signup is selected
    elif request.method == 'GET' and 'signup' in request.GET["action"]:
        form = RegistrationForm()
        return render(request, 'register/register.html', {'form': form})

    # If URL is manually tempered, then say error
    else:
        return redirect('show_login_message')


def show_login_message(request):
    # In case URL is tempered for non admin pages and user is logged out
    message = "You are currently not logged in, Please click here to sign in."
    return render(request, 'register/messages.html', {'User_info': message, 'login_required': True})


def show_admin_error(request):
    # In case URL is tempered for admin pages and non-admin user is logged out
    message = "You cannot view Admin panel"
    return render(request, 'register/messages.html', {'User_info': message, 'login_required': False})


@csrf_protect
def create_account(request):
    """
    This method handles Login Page requests for Sign In and Sign Up.
    :param: Request
    :return: Create account requests
    """

    # If user has posted the registration form
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Save the form and create a new user.
            form.save(request)

            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')

            # Take user to success page.
            message = f"Account successfully created for {first_name} {last_name}."
            return render(request, 'register/messages.html', {'User_info': message, 'login_required': True})
        else:
            return render(request, 'register/register.html', {'form': form})
    else:
        form = RegistrationForm()
        return render(request, 'register/register.html', {'form': form})

@csrf_protect
def sign_in(request):
    """
    This method handles Login Page requests for Sign In and Sign Up.
    :param: Request
    :return: redirection of Home
    """

    # If user has posted the login form
    if request.method == "POST":
        form = LoginForm(request=request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth.login(request, user)
            if auth.get_user(request).is_superuser:
                return redirect('admin_home')
        else:
            # Take the user back to login page and show error message.
            return render(request, 'register/login.html', {'form': form})

    return redirect('home')

@csrf_protect
def sign_out(request):
    """
     This method helps users to sign out and land to sign out.
     :param: Request
     :return: Home Page
    """
    # Logout the user and take him to main page.
    auth.logout(request)
    return redirect('main')
