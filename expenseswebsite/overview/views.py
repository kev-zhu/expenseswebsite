from django.shortcuts import render, redirect
from userpreferences.models import UserPreference
from userincome.models import Source, UserIncome
from expenses.models import Category, Expense
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
# from django.contrib import messages
import json
from django.http import JsonResponse
import datetime
import calendar

# Create your views here.
    

@login_required(login_url=('/authentication/login'))
def index(request):
    income = UserIncome.objects.filter(owner=request.user)
    expenses = Expense.objects.filter(owner=request.user)
    allInputs = [inputObj for inputObj in sorted(list(income) + list(expenses), key=lambda x:x.date, reverse=True)]

    paginator = Paginator(allInputs, 7)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    
    try:
        currency = UserPreference.objects.get(user=request.user).currency
    except:
        currency = None

    context = {
        'inputs': allInputs,
        'page_obj': page_obj,
        'currency': currency
    }

    return render(request, 'overview/index.html', context)


@login_required(login_url=('/authentication/login'))
def search_overview(request):
    if request.method == "POST":
        search_str = json.loads(request.body).get('searchText')
        income = UserIncome.objects.filter(
            amount__istartswith=search_str, owner=request.user) | UserIncome.objects.filter(
            date__istartswith=search_str, owner=request.user) | UserIncome.objects.filter(
            description__istartswith=search_str, owner=request.user) | UserIncome.objects.filter(
            source__istartswith=search_str, owner=request.user)
        data=list(income.values())

        expenses = Expense.objects.filter(
            amount__istartswith=search_str, owner=request.user) | Expense.objects.filter(
            date__istartswith=search_str, owner=request.user) | Expense.objects.filter(
            description__istartswith=search_str, owner=request.user) | Expense.objects.filter(
            category__istartswith=search_str, owner=request.user)

        data += list(expenses.values())

        data.sort(key=lambda x: x['date'], reverse=True)

        return JsonResponse(data, safe=False)


@login_required
def get_one_year_data(request):
    todays_date = datetime.date.today()
    one_yr_ago = (todays_date - datetime.timedelta(days=365)).replace(day=1)

    #add total_prior_year_ago for line graph
    total_prior_year = 0
    expenses = Expense.objects.filter(owner=request.user, date__lt=one_yr_ago)
    income = UserIncome.objects.filter(owner=request.user, date__lt=one_yr_ago)

    for exp in expenses:
        total_prior_year -= exp.amount
    for inc in income:
        total_prior_year += inc.amount

    final_rep = {}

    #within the last year, including current month
    expenses = Expense.objects.filter(owner=request.user, date__gte=one_yr_ago)
    income = UserIncome.objects.filter(owner=request.user, date__gte=one_yr_ago)

    while one_yr_ago <= todays_date:
        month_yr_format = f'{calendar.month_abbr[one_yr_ago.month]} \'{str(one_yr_ago.year)[-2:]}'
        if month_yr_format not in final_rep:
            final_rep[month_yr_format] = 0
        one_yr_ago += datetime.timedelta(days=1)


    for exp in expenses:
        month_yr = f'{calendar.month_abbr[exp.date.month]} \'{str(exp.date.year)[-2:]}'
        final_rep[month_yr] -= exp.amount

    for inc in income:
        month_yr = f'{calendar.month_abbr[inc.date.month]} \'{str(inc.date.year)[-2:]}'
        final_rep[month_yr] += inc.amount

    return JsonResponse({"data": final_rep, "total_prior_year": total_prior_year}, safe=False)