import decimal
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib import auth
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import TransactionForm, FilterForm, bl_object
from register.models import Profile
from .models import Transactions, Transaction_Sender, Transaction_Receiver, Request
from .BL_transactions import make_transaction, get_converted_amount, respond_request
from notifications.models import Notification
from notifications.signals import notify
from django.views.decorators.csrf import csrf_protect, requires_csrf_token


def main(request):
    """
    This method redirects user to main page
    :param request:
    :return: Main page
    """

    # Check the type of authenticated admin user
    if auth.get_user(request).is_superuser:
        return redirect('admin_home')

    # Check the type of authenticated non-admin user
    if auth.get_user(request).is_authenticated:
        return redirect('home')

    # Go back to main page.
    return render(request, 'webapps/main.html')


@login_required(login_url='show_login_message', )
def home(request):
    """
    This method redirects user to home page after user logs in
    :param request:
    :return: Html page displaying User Balance
    """
    # Get user details and display homepage
    user = auth.get_user(request)
    user_profile = Profile.objects.get(user=user)  # Getting User's Balance and Currency information
    return render(request, 'paymentapp/home.html',
                  {'user': user, 'profile': user_profile})


@login_required(login_url='show_login_message', )
def profile(request):
    """
    This method redirects user to user profile page after user logs in
    :param request:
    :return: Html page displaying changeable User information e.g) Mobile, Address, Currency
    """
    # Get user details
    user = auth.get_user(request)

    # if user has posted the form, then update the profile data.
    if request.method == 'POST':
        prf_user = Profile.objects.get(user_id=user.pk)    # Getting User's Balance and Currency information
        if prf_user.currency != request.POST['currency']:  # In case if user changed his profile currency
            new_balance = get_converted_amount(currency1=prf_user.currency,
                                               currency2=request.POST['currency'],
                                               amount=prf_user.balance,
                                               parm=request)
        else:
            new_balance = prf_user.balance

        Profile.objects.filter(user_id=user.pk).update(mobile=request.POST['mobile'],
                                                       address_1=request.POST['address_1'],
                                                       address_2=request.POST['address_2'],
                                                       post_code=request.POST['post_code'],
                                                       state=request.POST['state'],
                                                       area=request.POST['area'],
                                                       country=request.POST['country'],
                                                       region=request.POST['region'],
                                                       currency=request.POST['currency'],
                                                       balance=new_balance
                                                       )
    user_profile = Profile.objects.get(user_id=user.pk)
    return render(request, 'paymentapp/profile.html', {'user': user, 'profile': user_profile})


@login_required(login_url='show_login_message', )
def transaction_history(request):
    """
    This method redirects user to transaction history page after user logs in
    :param request:
    :return: Html page displaying list of all transactions and filter for sorting
    """
    # Get user details
    user = auth.get_user(request)

    # Get transactions for the user, where it was either receiver or sender
    records_transaction = Transactions.objects.filter(Q(receiver_id=user.pk) | Q(sender_id=user.pk)).order_by('-pk')

    # Date filter form
    filter_form = FilterForm(request.GET)
    page_number = int(request.GET.get('page_number', 1))

    # In case clear button is clicked Remove filters and return to first page
    if request.GET.get('action', '') == 'Clear':
        page_number = 1
        filter_form = FilterForm()

    # In case user wants to see transactions for specific date range
    if filter_form.is_valid():
        if filter_form.filter_applied:
            records_transaction = records_transaction.filter(
                create_at__range=[filter_form.start_date, filter_form.end_date])

    # Pagination
    paginator = Paginator(records_transaction, 10)
    records = paginator.get_page(page_number)

    data = []

    # Get all records of user's transactions and populate inside list of objects
    for item in records:
        obj_table = bl_object.Transaction_Table()
        obj_table.id = item.id
        obj_table.description = item.title

        # In case Transaction's notification is unseen, then display red badge and mark notification seen
        try:
            object_notification = Notification.objects.get(target_object_id=item.id, verb='Transfer')
            if object_notification is not None and object_notification.unread and user.pk == object_notification.recipient_id:
                obj_table.is_new = True
                Notification.objects.filter(pk=object_notification.id).update(unread=False)
        except:
            pass

        # In case user was sender, then fill these values
        if user.pk == item.sender_id_id:
            rec_user = User.objects.get(id=item.receiver_id_id)
            send = Transaction_Sender.objects.get(transaction_id=item.id)
            obj_table.full_name = bl_object.show_name(rec_user.first_name, rec_user.last_name)
            obj_table.amount = bl_object.show_amount(item.transferred_amount, send.currency)
            obj_table.trend = 'Decreased'
            obj_table.direction = 'Sent'
            obj_table.balance = bl_object.show_amount(send.new_balance, send.currency)

        # In case user was receiver, then fill these values
        elif user.pk == item.receiver_id_id:
            send_user = User.objects.get(id=item.sender_id_id)
            rec = Transaction_Receiver.objects.get(transaction_id=item.id)

            obj_table.full_name = bl_object.show_name(send_user.first_name, send_user.last_name)

            obj_table.amount = bl_object.show_amount(item.received_amount, rec.currency)
            obj_table.trend = 'Increased'
            obj_table.direction = 'Received'
            obj_table.balance = bl_object.show_amount(rec.new_balance, rec.currency)

        obj_table.res_mode = item.request_type

        # Transaction was made directly or requested by other user
        if item.request_type.lower() == "request":
            try:
                req = Request.objects.get(request_trans=item.id)
                item.res_date = f"{req.id}: Request responded on " + str(req.response)
                obj_table.res_date = item.res_date
            except:
                pass

        obj_table.date = item.create_at
        obj_table.time = item.time
        data.append(obj_table)

    context = {'data': data, 'page': records, 'total_page': range(1, paginator.num_pages + 1),
               'filter_form': filter_form}
    return render(request, 'paymentapp/transactions.html', context)


@login_required(login_url='show_login_message', )
def request_history(request):
    """
    This method redirects user to transaction history page after user logs in
    :param request:
    :return: Html page displaying list of all request and filter for sorting
    """
    # Get user details
    user = auth.get_user(request)

    # Get requests for the user, where it was either receiver or sender
    request_records = Request.objects.filter(Q(request_receiver_id=user.pk) | Q(request_sender_id=user.pk)).order_by(
        '-pk')

    # Date filter form
    filter_form = FilterForm(request.GET)

    page_number = int(request.GET.get('page_number', 1))
    response = None

    # Take action in case if user responded some request made by others.
    if request.GET.get('Decline', 0) != 0:
        response = respond_request(request.GET.get('Decline', 0), 'Decline', parm=request)
    elif request.GET.get('Accept', 0) != 0:
        response = respond_request(request.GET.get('Accept', 0), 'Accept', parm=request)

    # In case the request acceptance has some errors.
    if response is not None:
        # Get description of error returned by respond_request function
        if bl_object.validation_error.get(response, False):
            filter_form.add_error(None, bl_object.validation_error[response])

        page_number = request.GET.get('current_page', 1)

    # In case clear button is clicked Remove filters and return to first page
    if request.GET.get('action', '') == 'Clear':
        page_number = 1
        filter_form = FilterForm()

    # In case user wants to see requests for specific date range
    if filter_form.is_valid():
        if filter_form.filter_applied:
            request_records = request_records.filter(
                create_at__range=[filter_form.start_date, filter_form.end_date])

    # Paginator
    paginator = Paginator(request_records, 10)
    records = paginator.get_page(page_number)

    data = []

    for item in records:
        obj_table = bl_object.Request_Table()
        obj_table.ID = item.id
        # In case Request's notification is unseen, then display red badge and mark notification seen
        try:
            object_notification = Notification.objects.get(target_object_id=item.id, verb='Request')
            if object_notification is not None and object_notification.unread and user.pk == object_notification.recipient_id:
                obj_table.is_new = True
                Notification.objects.filter(pk=object_notification.id).update(unread=False)
        except:
            pass

        # In case user was sender, then fill these values
        if user.pk == item.request_sender_id:
            rec_user = User.objects.get(id=item.request_receiver_id)
            obj_table.full_name = bl_object.show_name(rec_user.first_name, rec_user.last_name)
            obj_table.inc_out = 'Outgoing'

        # In case user was receiver, then fill these values
        elif user.pk == item.request_receiver_id:
            send_user = User.objects.get(id=item.request_sender_id)
            obj_table.full_name = bl_object.show_name(send_user.first_name, send_user.last_name)
            obj_table.inc_out = 'Incoming'

        obj_table.seen = item.response
        obj_table.status = item.request_answer
        obj_table.trans = item.request_trans
        obj_table.amount = bl_object.show_amount(item.requested_amount, item.requested_currency)
        obj_table.date = item.create_at
        obj_table.time = item.time
        obj_table.description = item.title
        data.append(obj_table)

    context = {'data': data, 'page': records, 'total_page': range(1, paginator.num_pages + 1),
               'filter_form': filter_form}
    return render(request, 'paymentapp/requests.html', context)


@login_required(login_url='show_login_message', )
@csrf_protect
def pay_money(request):
    """
    This method redirects user to user payment page after user logs in
    :param request:
    :return: Html page displaying form for sending money to other users
    """
    # Get user details
    user = auth.get_user(request)

    # Set payment type as direct
    action = 'Direct'

    if request.method == "POST":

        form = TransactionForm(request.POST, user, action)  # Getting Transaction form.
        user_profile = Profile.objects.get(user=user)       # Getting User's Balance and Currency information
        if form.is_valid():

            result = make_transaction(form, user, trans_type=action, parm=request)

            # In case system made transaction successfully, refresh the form and send notification to recipient.
            if result is not None:
                form = TransactionForm(user=user, action=action)
                recipient = User.objects.get(username=request.POST["receiver_username"])
                notify.send(user, recipient=recipient, verb='Transfer',
                            description=f'{user.username} has transferred {bl_object.show_amount(decimal.Decimal(request.POST["amount"]), user_profile.currency)}',
                            target=result)
            else:

                form.add_error(None, 'Payment cannot be processed at the moment.')
        else:
            return render(request, 'paymentapp/transfer.html', {'form': form, 'page_type': action})
    else:
        form = TransactionForm(user=user, action=action)

    return render(request, 'paymentapp/transfer.html', {'form': form, 'page_type': action})


@login_required(login_url='show_login_message', )
@csrf_protect
def request_money(request):
    """
    This method redirects user to user payment page after user logs in
    :param request:
    :return: Html page displaying form for requesting money from other users
    """

    # Get user details
    user = auth.get_user(request)
    user_profile = Profile.objects.get(user=user)

    # Set payment type as request
    action = 'Request'

    if request.method == "POST":
        form = TransactionForm(request.POST, user, action)  # Getting Transaction form for making a request.
        if form.is_valid():
            recipient = User.objects.get(username=request.POST["receiver_username"])
            result = make_transaction(form, user, trans_type=action, parm=request)

            # In case system made request successfully, refresh the form and send notification to recipient.
            if result is not None:
                form = TransactionForm(user=user, action=action)
                notify.send(user, recipient=recipient, verb='Request',
                            description=f'{user.username} has requested {bl_object.show_amount(decimal.Decimal(request.POST["amount"]), user_profile.currency)}',
                            target=result)
            else:
                form.add_error(None, 'Request cannot be processed at the moment.')
        else:
            # In case of any other errors:
            return render(request, 'paymentapp/transfer.html', {'form': form, 'page_type': action})
    else:
        form = TransactionForm(user=user, action=action)

    return render(request, 'paymentapp/transfer.html', {'form': form, 'page_type': action})
