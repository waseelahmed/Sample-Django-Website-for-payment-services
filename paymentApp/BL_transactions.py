import datetime
import decimal

import requests
from django.db import transaction
from register.models import Profile
from django.contrib.auth.models import User
from .models import Transactions, Transaction_Receiver, Transaction_Sender, Request


class Transaction_BL:
    currency_sign = {'USD': '($)', 'GBP': '(£)', 'EURO': '(€)'}
    validation_error = {404: 'Following user is not registered in system.',
                        400: 'Transfer cannot be made to your own user.',
                        401: 'Request cannot be processed due to insufficient funds.',
                        403: 'Request cannot be processed. Please contact helpline ',
                        200: 'Start end cannot be greater then end date.',
                        201: 'Please select some dates to apply the filter.'

                        }

    def show_amount(self, amount, currency, currency_sign=currency_sign):
        return '{:.2f}'.format(amount) + " " + currency_sign[currency]

    def show_name(self, first_name, last_name):
        return first_name + " " + last_name

    class Transaction_Table:
        def __init__(self):
            self.ID = None
            self.full_name = None
            self.trend = None
            self.balance = None
            self.currency = None
            self.data = None
            self.time = None
            self.amount = None
            self.direction = None
            self.description = None
            self.res_mode = None
            self.res_date = None
            self.is_new = None

    class Request_Table:
        def __init__(self):
            self.ID = None
            self.full_name = None
            self.date = None
            self.time = None
            self.amount = None
            self.inc_out = None
            self.status = None
            self.type = None
            self.seen = None
            self.is_new = None
            self.description = None
            self.trans = None


def get_converted_amount(currency1, currency2, amount, parm):
    base_url = parm.build_absolute_uri('/')[:-1] + '/'

    # Calling API URL and bypassing the HTTPS security for it.
    url = base_url + 'webapps2023/api/convert/{}/{}/{}'
    response = requests.get(url.format(currency1, currency2, amount), verify=False)
    data = response.json()
    converted_amount = data['converted_amount']

    return decimal.Decimal(converted_amount)


def transfer_funds(amount, receiver, receiver_currency, sender,
                   sender_currency, title, action, parm):

    # Check if both users currency is same or not.
    if sender_currency != receiver_currency:
        rec_amount = get_converted_amount(sender_currency, receiver_currency, amount, parm=parm)
    else:
        rec_amount = amount

    sender_balance_old = Profile.objects.get(user=sender).balance
    receiver_balance_old = Profile.objects.get(user=receiver).balance

    # Check if sender has enough balance
    if sender_balance_old < rec_amount:
        return 401

    try:
        with transaction.atomic():
            # Atomic Transaction
            # If a single query fails, none of the changes will be made to other tables
            trans_obj = Transactions.objects.create(title=title, transferred_amount=amount, sender_id=sender,
                                                    receiver_id=receiver, received_amount=rec_amount,
                                                    request_type=action)
            # Deduct amount from sender
            sender_balance_new = sender_balance_old - amount

            # Add amount to receiver
            receiver_balance_new = receiver_balance_old + rec_amount

            # Make Entry in sender table
            Transaction_Sender(balance=sender_balance_old, new_balance=sender_balance_new,
                               currency=sender_currency, transaction_id=trans_obj.pk).save()

            # Make Entry in receiver table
            Transaction_Receiver(balance=receiver_balance_old, new_balance=receiver_balance_new,
                                 currency=receiver_currency, transaction_id=trans_obj.pk).save()

            # Update Receiver balance
            Profile.objects.filter(user=receiver).update(balance=receiver_balance_new)

            # Update Sender balance
            Profile.objects.filter(user=sender).update(balance=sender_balance_new)
            return trans_obj
    except:
        return 403


def make_transaction(form, sender, trans_type, parm):
    receiver = form.cleaned_data['receiver_username']
    amount = form.cleaned_data['amount']
    title = form.cleaned_data['title']

    # Get sender's and receiver's details
    sender = User.objects.get(username=sender)
    receiver = User.objects.get(username=receiver)

    sender_profile = Profile.objects.get(user=sender)
    receiver_profile = Profile.objects.get(user=receiver)

    if trans_type == 'Direct':
        # Make transfer if method is direct
        obj_trans = transfer_funds(amount, receiver, receiver_profile.currency, sender, sender_profile.currency, title,
                                   action=trans_type, parm=parm)
        return obj_trans

    elif trans_type == 'Request':
        # Make Request
        obj_request = make_request(amount, receiver, sender, sender_profile.currency, title)
        return obj_request


def make_request(amount, receiver, sender, sender_currency, title):
    try:
        # Create entry in request table
        obj_request = Request(title=title, requested_amount=amount,
                              request_answer='Pending', request_sender=sender,
                              request_receiver=receiver, request_trans=0,
                              requested_currency=sender_currency)
        obj_request.save()
        return obj_request
    except:
        403


def accept_request(request_id, parm):
    try:
        # Get details about request
        request_object = Request.objects.get(pk=request_id)

        # Get details about sender and receiver
        profile_request_receiver = Profile.objects.get(user=request_object.request_receiver)
        profile_request_sender = Profile.objects.get(user=request_object.request_sender)

        # Check if sender has changed his currency at the time of request and at current instance.
        converted_amount = get_converted_amount(amount=request_object.requested_amount,
                                                currency1=request_object.requested_currency,
                                                currency2=profile_request_receiver.currency,
                                                parm=parm)

        # Make transfer according to his current currency value.
        # For transfer_funds receiver is now sender, because the request sender want to receive money

        obj_trans = transfer_funds(amount=converted_amount,

                                   receiver=request_object.request_sender,
                                   receiver_currency=profile_request_sender.currency,

                                   sender=request_object.request_receiver,
                                   sender_currency=profile_request_receiver.currency,

                                   title=request_object.title,
                                   action='Request',
                                   parm=parm
                                   )
        # If no error occur, update the request.
        if obj_trans not in [403, 401]:
            Request.objects.filter(pk=request_id).update(request_answer='Approved',
                                                         response=datetime.datetime.now(),
                                                         request_trans=obj_trans.pk)
        return obj_trans

    except:
        return 403


def decline_request(request_id):
    try:
        # Update request and make it declined
        Request.objects.filter(pk=request_id).update(request_answer='Cancelled', response=datetime.datetime.now())
        return True
    except:
        return 403


def respond_request(request_id, action, parm):
    try:
        # Take action against request based on user's selection
        if action == 'Accept':
            answer = accept_request(request_id, parm)
        elif action == 'Decline':
            answer = decline_request(request_id)

        return answer
    except:
        return None
