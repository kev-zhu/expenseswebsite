from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import os
import json
from django.conf import settings
from .models import UserPreference
from expenses.models import Expense, Category
from userincome.models import UserIncome, Source
from django.contrib import messages, auth
from django.contrib.auth import update_session_auth_hash

from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from authentication.utils import token_generator
from django.urls import reverse
import threading

import datetime

# Create your views here.

class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send(fail_silently=False)


@login_required
def general_settings(request):
    currency_data = []

    file_path = os.path.join(settings.BASE_DIR, 'currencies.json')

    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
        for k,v in data.items():
            currency_data.append({'name': k, 'value': v})

    exists = UserPreference.objects.filter(user=request.user).exists()
    user_preferences = None

    if exists:
        user_preferences = UserPreference.objects.get(user=request.user)

    categories = Category.objects.filter(owner=request.user)
    sources = Source.objects.filter(owner=request.user)

    context = {
        'currencies': currency_data, 
        'user_preferences': user_preferences,
        'categories': categories,
        'sources': sources,
    }
   
    if request.method == "GET":
        return render(request, 'preferences/general.html', context)
    else:
        currency = request.POST['currency']
        if exists:
            user_preferences.currency=currency
            user_preferences.save()
        else:
            UserPreference.objects.create(user=request.user, currency=currency)

        messages.success(request, 'Changes saved')

        return render(request, 'preferences/general.html', context)


@login_required
def account_settings(request):
    expenses = Expense.objects.filter(owner=request.user)
    income = UserIncome.objects.filter(owner=request.user)

    networth = 0

    for exp in expenses:
        networth -= exp.amount

    for inc in income:
        networth += inc.amount

    context = {
        "expensesCount": expenses.count(),
        "incomeCount": income.count(),
        "networth": networth
    }
    return render(request, 'preferences/account.html', context)


@login_required
def change_account_info(request):
    if request.method == "POST":
        data = json.loads(request.body)
        username = data['username']
        name = data['name']

        if username != request.user.username:
            old_username = request.user.username
            request.user.username = username
            target_path = os.path.join(settings.BASE_DIR, 'userupload/')

            #renaming of data file if exists so can be retrieved later on/prevent cluttering or overlapping of having same username files
            if os.path.exists(f'{str(target_path)}{old_username}-data.json'):
                os.rename(f'{str(target_path)}{old_username}-data.json', f'{str(target_path)}{request.user.username}-data.json')

        request.user.first_name = name
        request.user.save()

    return JsonResponse({'account_updated': True})


@login_required
def change_password(request):
    print(request.POST)
    if request.method == "POST":
        currPass = request.POST['currPass']
        pass1 = request.POST['password']
        pass2 = request.POST['password2']

        if not auth.authenticate(username=request.user.username, password=currPass):
            messages.error(request, 'Current password is invalid')
            return redirect('account')
        
        if len(pass1) < 6 or len(pass2) < 6:
            messages.error(request, 'Password(s) are not long enough')
            return redirect('account')
        elif pass1 != pass2:
            messages.error(request, 'New passwords do not match')
            return redirect('account')
        else:
            request.user.set_password(pass1)
            update_session_auth_hash(request, request.user)

            request.user.save()

            messages.success(request, 'Password has been updated')
            return redirect('overview')


@login_required
def deactivate_account(request):
    user = request.user

    #safety for admin to not deactivate acc by accident
    if not user.email:
        return redirect('overview')

    #send activation email out to user formatted: activate/<uid>/<token> - like the one used in registration/verification
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    domain = get_current_site(request).domain
    link = reverse('activate', kwargs={'uidb64': uidb64, 'token': token_generator.make_token(user)})
    reactivate_url = f'http://{domain}{link}'

    email_subject = 'Reactivate your account'
    email_body = f'Hello {user.username}! \n Your account was deactivated on {datetime.date.today()}. Please click on this link when you want to reactivate your account.\n {reactivate_url}'
    email = EmailMessage(
        email_subject,
        email_body,
        'noreply@semycolon.com',
        [user.email]
    )
    EmailThread(email).run()

    #deactivate account
    user.is_active = False
    user.save()

    #logout not required becasue is_active=False will logoff user
    messages.success(request, 'Your account has been deactivated')
    return redirect('login')

    
@login_required
def delete_account(request):
    user = request.user

    #safety for admin to not delete acc by accident
    if not user.email:
        return redirect('overview')

    try:
        user.delete()
    except:
        pass

    messages.success(request, 'Your account has been deleted')
    return redirect('login')


@login_required
def edit_category(request):
    if request.method == "POST":
        data = json.loads(request.body)
        update_category = Category.objects.get(owner=request.user, name=data['old'])
        update_category.name=data['new']
        update_category.save()

        expenses = Expense.objects.filter(owner=request.user, category=data['old'])
        for exp in expenses:
            exp.category = data['new']
            exp.save()

        return JsonResponse({"response": "success"})

    return JsonResponse({"response":"fail"})


@login_required
def del_category(request):
    if request.method == "POST":
        to_delete = request.POST['del-category']
        categories = [category.name for category in Category.objects.filter(owner=request.user)]
        expenses = Expense.objects.filter(owner=request.user, category=to_delete)

    if to_delete in categories:
        Category.objects.get(owner=request.user, name=to_delete).delete()
        for expense in expenses:
            expense.delete()

        messages.success(request, f'The {to_delete} category, along all expenses under that category, has been deleted.')
        return redirect('overview')
    else:
        messages.error(request, 'Please select a valid category to delete')
        return redirect('general')


@login_required
def edit_source(request):
    if request.method == "POST":
        data = json.loads(request.body)
        update_source = Source.objects.get(owner=request.user, name=data['old'])
        update_source.name=data['new']
        update_source.save()

        income = UserIncome.objects.filter(owner=request.user, source=data['old'])
        for inc in income:
            inc.source = data['new']
            inc.save()

        return JsonResponse({"response": "success"})

    return JsonResponse({"response":"fail"})


@login_required
def del_source(request):
    if request.method == "POST":
        to_delete = request.POST['del-source']
        sources = [source.name for source in Source.objects.filter(owner=request.user)]
        income = UserIncome.objects.filter(owner=request.user, source=to_delete)

    if to_delete in sources:
        Source.objects.get(owner=request.user, name=to_delete).delete()
        for inc in income:
            inc.delete()

        messages.success(request, f'The {to_delete} source, along all income under that source, has been deleted.')
        return redirect('overview')
    else:
        messages.error(request, 'Please select a valid income to delete')
        return redirect('general')