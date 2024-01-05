from django.contrib import auth
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from admin.form import AdminUserCreationForm
from paymentApp.models import Transaction_Sender, Transaction_Receiver, Request
from register.models import Profile


def admin_home(request):
    """
    This method redirects admin users to main admin panel
    :param request:
    :return: Html page displaying a main page
   """
    # Get admins details
    user = auth.get_user(request)
    if user.is_authenticated and user.is_superuser:
        # Go to admin homepage
        return render(request, 'administrator/admin_home.html', {'user': user})
    else:
        # If url is manually tempered and view is called, show error Message
        return redirect('show_admin_error')


def transactions_all(request):
    """
    This method redirects admin users to all transactions of app
    :param request:
    :return: Html page displaying list of all transactions
   """
    # Get admins details
    user = auth.get_user(request)
    if user.is_authenticated and user.is_superuser:
        # Get the value of user selected toggler
        choice = request.GET.get('type', 'sender')

        if choice == 'sender':
            # Get all transactions sender details along with all transactions
            transactions = Transaction_Sender.objects.all().order_by('-pk').select_related('transaction')
        else:
            # Get all transactions receiver details along with all transactions
            transactions = Transaction_Receiver.objects.all().order_by('-pk').select_related('transaction')

        # Start pagination
        page_number = int(request.GET.get('page', 1))
        page_number = int(request.GET.get('select_page', page_number))

        paginator = Paginator(transactions, 10)

        records = paginator.get_page(page_number)

        return render(request, 'administrator/all_trans.html', {'transactions': records, 'paginator': paginator,
                                                                'type': choice,
                                                                'total_page': range(1, paginator.num_pages + 1)})
    else:
        # If url is manually tempered and view is called, show error Message
        return redirect('show_admin_error')


def request_all(request):
    """
    This method redirects admin users to user made requests
    :param request:
    :return: Html page displaying list of all request
   """
    # Get admins details
    user = auth.get_user(request)
    if user.is_authenticated and user.is_superuser:
        # Get all request by all users
        requests = Request.objects.all().order_by('-pk').select_related('request_sender')

        # Start pagination
        page_number = int(request.GET.get('page', 1))
        page_number = int(request.GET.get('select_page', page_number))

        paginator = Paginator(requests, 10)

        records = paginator.get_page(page_number)

        return render(request, 'administrator/all_requests.html',
                      {'requests': records, 'paginator': paginator, 'total_page': range(1, paginator.num_pages + 1)})
    else:
        # If url is manually tempered and view is called, show error Message
        return redirect('show_admin_error')


def users_all(request):
    """
    This method redirects admin users to all users page
    :param request:
    :return: Html page displaying list of all users
   """
    # Get admins details
    user = auth.get_user(request)
    if user.is_authenticated and user.is_superuser:
        user_records = Profile.objects.all().order_by('-pk').select_related('user')

        page_number = int(request.GET.get('page', 1))
        page_number = int(request.GET.get('select_page', page_number))

        paginator = Paginator(user_records, 10)

        records = paginator.get_page(page_number)

        return render(request, 'administrator/Users.html', {'users': records, 'paginator': paginator,
                                                            'total_page': range(1, paginator.num_pages + 1)})
    else:
        # If url is manually tempered and view is called, show error Message
        return redirect('show_admin_error')


def admin_create(request):
    """
    This method redirects admin users new admin creation page
    :param request:
    :return: Html page displaying Admin user creation form
   """
    # Get admins details
    user = auth.get_user(request)
    if user.is_authenticated and user.is_superuser:
        if request.method == "POST":
            form = AdminUserCreationForm(request.POST)
            if form.is_valid():
                form.save()
                username = form.cleaned_data.get("username")
                return render(request, 'register/messages.html',
                              {'User_info': f'Admin user: {username} has been successfully created'})
        else:
            form = AdminUserCreationForm()
        return render(request, 'administrator/register_super.html', {'form': form})
    else:
        # If url is manually tempered and view is called, show error Message
        return redirect('show_admin_error')
