from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Source, UserIncome
from django.core.paginator import Paginator
from userpreferences.models import UserPreference
from django.contrib import messages
import json
from django.http import JsonResponse
import datetime
# Create your views here.


@login_required(login_url=('/authentication/login'))
def index(request):
    income = UserIncome.objects.filter(owner=request.user)
    paginator = Paginator(income, 7)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)

    try:
        currency = UserPreference.objects.get(user=request.user).currency
    except:
        currency = None
        
    context = {
        'income': income,
        'page_obj': page_obj,
        'currency': currency
    }

    return render(request, 'income/index.html', context)

def source_dne(user, source: str) -> bool:
    existing_sources = [source.name.lower() for source in Source.objects.filter(owner=user)]
    return not source.lower() in existing_sources

@login_required(login_url=('/authentication/login'))
def add_income(request):
    sources = Source.objects.filter(owner=request.user)
    context = {
        'sources': sources,
        'values': request.POST
    }

    if request.method == 'POST':
        amount = request.POST['amount']
        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, "income/add_income.html", context)

        description = request.POST['description']
        if not description:
            messages.error(request, 'Description is required')
            return render(request, "income/add_income.html", context)

        source = request.POST['source'].lower().capitalize()
        if not source:
            messages.error(request, 'Source is required')
            return render(request, "income/add_income.html", context)

        #default date today if no date selected
        date = request.POST['income_date']
        if not date:
            date = str(datetime.date.today())

        if source_dne(request.user, source):
            Source.objects.create(owner=request.user, name=source)

        UserIncome.objects.create(owner=request.user, amount=amount, description=description, date=date, source=source)
        messages.success(request,'Record saved successfully')
        return redirect('overview')

    return render(request, "income/add_income.html", context)


@login_required(login_url=('/authentication/login'))
def income_edit(request, id):
    try:
        income = UserIncome.objects.filter(owner=request.user).get(pk=id)
    except:
        messages.error(request, "Income does not exist")
        return redirect('income')
        
    sources = Source.objects.filter(owner=request.user)

    #this is necessary? conversion to str so django can read it in html page
    #otherwise, html page cannot read date objects to show on edit page
    income.date = str(income.date)

    context = {
        'income': income,
        'sources': sources
    }

    if request.method == 'GET':
        return render(request, 'income/edit_income.html', context)

    if request.method == 'POST':
        amount = request.POST['amount']
        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, "income/edit_income.html", context)

        description = request.POST['description']
        if not description:
            messages.error(request, 'Description is required')
            return render(request, "income/edit_income.html", context)

        source = request.POST['source'].lower().capitalize()
        if not source:
            messages.error(request, 'Source is required')
            return render(request, "income/edit_income.html", context)

        date = request.POST['income_date']
        if not date:
            date = str(datetime.date.today())

        if source_dne(request.user, source):
            Source.objects.create(owner=request.user, name=source)

        income.amount = amount
        income.description = description
        income.source = source
        income.date = date

        income.save()
        messages.success(request, 'Income has been updated')

        return redirect('overview')


@login_required(login_url=('/authentication/login'))
def delete_income(request, id):
    try:
        income = UserIncome.objects.filter(owner=request.user).get(pk=id)
    except:
        messages.error(request, "Income does not exist")
        return redirect('income')

    income.delete()
    messages.success(request, 'Income deleted')

    return redirect('overview')


@login_required(login_url=('/authentication/login'))
def search_income(request):
    if request.method == "POST":
        search_str = json.loads(request.body).get('searchText')
        income = UserIncome.objects.filter(
            amount__istartswith=search_str, owner=request.user) | UserIncome.objects.filter(
            date__istartswith=search_str, owner=request.user) | UserIncome.objects.filter(
            description__istartswith=search_str, owner=request.user) | UserIncome.objects.filter(
            source__istartswith=search_str, owner=request.user)
        data=income.values()

        return JsonResponse(list(data), safe=False)

    
@login_required
def stats_view(request):
    return render(request, 'income/stats.html')

def income_source_summary(request):
    todays_date = datetime.date.today()
    six_months_ago = todays_date - datetime.timedelta(days=30*6)
    income = UserIncome.objects.filter(owner=request.user, date__gte=six_months_ago, date__lte=todays_date)
    final_rep = {}

    def get_source(income):
        return income.source

    def get_amount(income):
        return income.amount

    for inc in income:
        if get_source(inc) not in final_rep:
            final_rep[get_source(inc)] = get_amount(inc)
        else:
            final_rep[get_source(inc)] += get_amount(inc)

    return JsonResponse({"income_source_data": final_rep}, safe=False)