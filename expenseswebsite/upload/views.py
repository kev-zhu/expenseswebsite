from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from userpreferences.models import UserPreference
from expenses.models import Category, Expense
from userincome.models import Source, UserIncome
import datetime
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
import os
from django.conf import settings
import json
from django.contrib import messages
import csv

# Create your views here.

@login_required
def index(request):
    target_path = os.path.join(settings.BASE_DIR, 'userupload/')
    file_end = '-data.json'
    user_file_loc = f'{str(target_path)}{request.user.username}{file_end}'

    if request.method == "POST":
        try:
            file = request.FILES['filename']
        except:
            messages.error(request, 'No file uploaded. Please upload a new file.')
            return redirect('upload')

        data = str(file.read())
        #****** later change this so the user can download a formatted spread sheet so file upload can be more "flexible"/prevent errors for user if the follow directions
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
            return redirect('upload')

        return redirect('upload-changes')

    #get or put requests defaults to rendering of upload page
    return render(request, 'upload/upload.html')


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


@login_required
def user_has_file(request):
    target_path = os.path.join(settings.BASE_DIR, 'userupload/')
    return JsonResponse({'result': os.path.exists(f'{str(target_path)}{request.user.username}-data.json')})


@login_required
def upload_changes(request):
    try:
        currency = UserPreference.objects.get(user=request.user).currency
    except:
        currency = None
    cates = Category.objects.filter(owner=request.user)
    sources = Source.objects.filter(owner=request.user)

    target_path = os.path.join(settings.BASE_DIR, 'userupload/')
    file_end = '-data.json'
    user_file_loc = f'{str(target_path)}{request.user.username}{file_end}'

    if os.path.exists(user_file_loc):
        json_data = open(user_file_loc)
        retrieved_data = json.load(json_data)
        json_data.close()
    else:
        messages.error(request, 'No file uploaded previously. Please upload a new file.')
        return redirect('upload')

    if request.method == "GET":
        if len(request.GET) == 0:
            messages.success(request, 'Data retrieved from upload. Please make any necessary changes.')

    if request.method == "POST":
        categories = retrieved_data['categories']
        expenses = retrieved_data['expense']

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
        elif 'post' in request.POST:
            #another layer of check to make sure all categories have a type -- if not then reload page with mesage
            for category in categories:
                if category['type'] == '':
                    messages.error(request, 'Please ensure that all Categories/Sources fall under a Expense/Income type.')
                    return redirect(reverse('upload-changes')+"?re=T")
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

    context = {
        "cats": cates,
        "sources": sources,
        "data": retrieved_data,
        "currency": currency
    }
    return render(request, 'upload/edit-upload.html', context)


def download_template(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=UploadTemplate.csv'

    writer = csv.writer(response)
    instructions = ['Instructions: Please do not change the formatting. Upload any data into the respective columns. Avoid using any "," (in amount or description) as it would disrupt the .csv file. Save file as a .csv file before uploading. You can upload file to Google Sheets or Excel to add new data easily. You can add more rows under heading if needed.']
    writer.writerow(instructions)
    writer.writerow(['Date(mm/dd/yyyy)', 'Category', 'Amount', 'Description'])

    messages.success(request, 'Template Downloaded')
    return response 