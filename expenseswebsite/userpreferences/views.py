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


@login_required
def upload(request):
    try:
        currency = UserPreference.objects.get(user=request.user).currency
    except:
        currency = None

    # get: will try to get a locally saved JSON file of previously uploaded file -- if DNE then message error: no file upladed
    #   on this page: on top have: "Data received by {{ filename }} + show the categories and stuff + form + data underneath -- sorted by date" 
    # post: open + read the file + organize data + save the data as JSON file for get request -- if file already exist -- replace old one
    # later: if final page submission to finalize all data --> delete old JSON file 

    target_path = os.path.join(settings.BASE_DIR, 'userupload/')
    file_end = '-data.json'

    user_file_loc = f'{str(target_path)}{request.user.username}{file_end}'
    if request.method == "GET":
        if os.path.exists(user_file_loc):
            json_data = open(user_file_loc)
            retrieved_data = json.load(json_data)
            json_data.close()

            if len(request.GET) == 0:
                messages.success(request, 'Data retrieved. Please continue where you left off.')
        else:
            messages.error(request, 'No file uploaded previously. Please upload a new file.')
            return redirect('general')

    if request.method == "POST":
        try:
            file = request.FILES['filename']
        except:
            messages.error(request, 'No file uploaded. Please upload a new file.')
            return redirect('general')

        data = str(file.read())
        # later change this so the user can download a formatted spread sheet so file upload can be more "flexible"/prevent errors for user if the follow directions
        data = organize_data(data[2:].replace('\\r\\n',',').split(','))
        uniq_categories = uniq_dataset(data)

        retrieved_data = {
            "categories": uniq_categories,
            "expense": data
        }

        # save data as json file to be opened/deleted later again
        try:
            with open(user_file_loc, 'w') as f:
                json.dump(retrieved_data, f, ensure_ascii=False, indent=4)
        except:
            os.remove(f'{target_path}{request.user.username}{file_end}')
            messages.warning(request, 'Problem with uploading file. Please try again later.')
            return redirect('general')

        messages.success(request, 'File Uploaded')

    categories = Category.objects.filter(owner=request.user)
    sources = Source.objects.filter(owner=request.user)

    context = { 
        "cats": categories,
        "sources": sources,
        "data": retrieved_data,
        "currency": currency
    }
    return render(request, 'preferences/edit-upload.html', context)


def uniq_dataset(data):
    uniq_set = {d['category'] for d in data}
    category_obj = []

    for category in uniq_set:
        obj = {
            "initial": category,
            "type": "",
            "currentname": category
        }
        category_obj.append(obj)

    return category_obj


def organize_data(data):
    organized = []
    i = 0
    while i < len(data):
    # for data in all_data:
        date_cat = data[i]
        if date_cat:
            date = date_cat[:-1].split('/')
            month = int(date[0])
            day = int(date[1])
            year = 2000 + int(date[2])
            item = {
                "initial": date_cat[-1:],
                "date": datetime.date(year=year, month=month, day=day),
                "type": "",
                "category": date_cat[-1:],
                "amount": data[i + 1],
                "desc": data[i + 2]
            }
            organized.append(item)
        i +=3 

    organized.sort(key=lambda x: x['date'])

    def convertDateToStr(obj):
        obj['date'] = str(obj['date'])
        return obj

    return list(map(lambda x: convertDateToStr(x), organized))


@login_required
def user_has_file(request):
    target_path = os.path.join(settings.BASE_DIR, 'userupload/')
    return JsonResponse({'result': os.path.exists(f'{str(target_path)}{request.user.username}-data.json')})


@login_required
def upload_changes(request):
    target_path = os.path.join(settings.BASE_DIR, 'userupload/')
    file_end = '-data.json'
    user_file_loc = f'{str(target_path)}{request.user.username}{file_end}'

    if os.path.exists(user_file_loc):
        json_data = open(user_file_loc)
        retrieved_data = json.load(json_data)
        json_data.close()

    categories = retrieved_data['categories']
    expenses = retrieved_data['expense']

    if request.method == "POST":
        if 'apply' in request.POST:
            for category in categories:
                initial = category['initial']
                category['type'] = request.POST[f'{initial}type'].capitalize()
                if category['type'] == 'Expense':
                    category['currentname'] = request.POST[f'{initial}category']
                elif category['type'] == 'Income':
                    category['currentname'] = request.POST[f'{initial}source']
                if category['currentname'] == '':
                    category['currentname'] = category['initial']

            for expense in expenses:
                initial = expense['initial']
                expense['type'] = request.POST[f'{initial}type'].capitalize()
                if expense['type'] == 'Expense':
                    expense['category'] = request.POST[f'{initial}category']
                elif expense['type'] == 'Income':
                    expense['category'] = request.POST[f'{initial}source']
                if category['currentname'] == '':
                    expense['category'] = expense['initial']

            #save data to json file here
            updated_data = {
                "categories": categories,
                "expense": expenses
            }
            try:
                with open(user_file_loc, 'w') as f:
                    json.dump(updated_data, f, ensure_ascii=False, indent=4)
            except:
                messages.warning(request, 'Problem with editing file. Please try again later.')
            return redirect('upload')      

        # else? if 'apply' not in POST then it is implied that 'post' will be 
        # unless use Postman or something where a POST request can be sent without clicking either button
        elif 'post' in request.POST:
            #another layer of check to make sure all categories have a type -- if not then reload page with mesage
            for category in categories:
                if category['type'] == '':
                    messages.error(request, 'Please ensure that all Categories/Sources fall under a Expense/Income type.')
                    return redirect(reverse('upload')+"?re=T")
            #upload all of expense/source to server
            for obj in expenses:
                date = datetime.datetime.strptime(obj['date'], "%Y-%m-%d").date()
                if date > datetime.date.today():
                    continue

                amount = float(obj['amount'][1:])
                if obj['type'] == 'Expense':
                    if not Category.objects.filter(owner=request.user, name=obj['category']):
                        Category.objects.create(owner=request.user, name=obj['category'].capitalize())
                    Expense.objects.create(owner=request.user, amount=amount, date=date, description=obj['desc'], category=obj['category'].capitalize())
                #elif here incase there is one without a type for some reason -- skip over
                elif obj['type'] == 'Income':
                    if not Source.objects.filter(owner=request.user, name=obj['category']):
                        Source.objects.create(owner=request.user, name=obj['category'].capitalize())
                    UserIncome.objects.create(owner=request.user, amount=amount, date=date, description=obj['desc'], source=obj['category'].capitalize())

            #delete file once everything uploaded
            os.remove(user_file_loc)

            messages.success(request,'All uploaded data has been added.')
            return redirect('overview')

    return redirect('upload')