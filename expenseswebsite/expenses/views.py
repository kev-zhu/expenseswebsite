from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from userpreferences.models import UserPreference
from .models import Expense, Category
from django.contrib import messages
from django.core.paginator import Paginator
import json
from django.http import JsonResponse, HttpResponse
import datetime
import csv
import xlwt

# Create your views here.

@login_required(login_url=('/authentication/login'))
def index(request):
    expenses = Expense.objects.filter(owner=request.user)
    paginator = Paginator(expenses, 7)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    
    try:
        currency = UserPreference.objects.get(user=request.user).currency
    except:
        currency = None
    context = {
        'expenses': expenses,
        'page_obj': page_obj,
        'currency': currency
    }

    return render(request, 'expenses/index.html', context)

def category_dne(user, category: str) -> bool:
    existing_categories = [category.name.lower() for category in Category.objects.filter(owner=user)]
    return not category.lower() in existing_categories

@login_required(login_url=('/authentication/login'))
def add_expense(request):
    categories = Category.objects.filter(owner=request.user)
    context = {
        'categories': categories,
        'values': request.POST
    }

    if request.method == 'POST':
        amount = request.POST['amount']
        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, "expenses/add_expense.html", context)

        description = request.POST['description']
        if not description:
            messages.error(request, 'Description is required')
            return render(request, "expenses/add_expense.html", context)

        category = request.POST['category'].lower().capitalize()
        if not category:
            messages.error(request, 'Category is required')
            return render(request, "expenses/add_expense.html", context)

        #default date today if no date selected
        date = request.POST['expense_date']
        if not date:
            date = str(datetime.date.today())

        if category_dne(request.user, category):
            Category.objects.create(owner=request.user, name=category)

        Expense.objects.create(owner=request.user, amount=amount, description=description, date=date, category=category)
        messages.success(request,'Expense has been added')
        return redirect('overview')

    return render(request, "expenses/add_expense.html", context)


@login_required(login_url=('/authentication/login'))
def expense_edit(request, id):
    #try block here incase user tries to edit an expense that DNE or is not theirs
    try:
        expense = Expense.objects.filter(owner=request.user).get(pk=id)
    except:
        messages.error(request, "Expense does not exist")
        return redirect('overview')
        
    categories = Category.objects.filter(owner=request.user)

    #this is necessary? conversion to str so django can read it in html page
    #otherwise, html page cannot read date objects to show on edit page
    expense.date = str(expense.date)

    context = {
        'expense': expense,
        'categories': categories
    }

    if request.method == 'GET':
        return render(request, 'expenses/edit_expense.html', context)

    if request.method == 'POST':
        amount = request.POST['amount']
        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, "expenses/edit_expense.html", context)

        description = request.POST['description']
        if not description:
            messages.error(request, 'Description is required')
            return render(request, "expenses/edit_expense.html", context)

        category = request.POST['category'].lower().capitalize()
        if not category:
            messages.error(request, 'Category is required')
            return render(request, "expenses/edit_expense.html", context)

        date = request.POST['expense_date']
        if not date:
            date = str(datetime.date.today())

        if category_dne(request.user, category):
            Category.objects.create(owner=request.user, name=category)
            
        expense.amount = amount
        expense.description = description
        expense.category = category
        expense.date = date

        expense.save()
        messages.success(request, 'Expense has been updated')

        return redirect('overview')


@login_required(login_url=('/authentication/login'))
def delete_expense(request, id):
    try:
        expense = Expense.objects.filter(owner=request.user).get(pk=id)
    except:
        messages.error(request, "Expense does not exist")
        return redirect('overview')

    expense.delete()
    messages.success(request, 'Expense deleted')

    return redirect('overview')


@login_required(login_url=('/authentication/login'))
def search_expenses(request):
    if request.method == "POST":
        search_str = json.loads(request.body).get('searchText')
        expenses = Expense.objects.filter(
            amount__istartswith=search_str, owner=request.user) | Expense.objects.filter(
            date__istartswith=search_str, owner=request.user) | Expense.objects.filter(
            description__istartswith=search_str, owner=request.user) | Expense.objects.filter(
            category__istartswith=search_str, owner=request.user)
        data=expenses.values()

        return JsonResponse(list(data), safe=False)


@login_required
def stats_view(request):
    return render(request, 'expenses/stats.html')


def expense_category_summary(request):
    todays_date = datetime.date.today()
    six_months_ago = todays_date - datetime.timedelta(days=30*6)
    expenses = Expense.objects.filter(owner=request.user, date__gte=six_months_ago, date__lte=todays_date)
    final_rep = {}

    def get_category(expense):
        return expense.category

    def get_amount(expense):
        return expense.amount

    for exp in expenses:
        if get_category(exp) not in final_rep:
            final_rep[get_category(exp)] = get_amount(exp)
        else:
            final_rep[get_category(exp)] += get_amount(exp)

    return JsonResponse({"expense_category_data": final_rep}, safe=False)


def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename=Expenses{str(datetime.datetime.now())}.csv'

    writer = csv.writer(response)
    writer.writerow(['Amount', 'Description', 'Category', 'Date'])

    expenses = Expense.objects.filter(owner=request.user)
    
    for expense in expenses:
        writer.writerow([expense.amount, expense.description, expense.category, expense.date])

    return response


def export_excel(request):
    response = HttpResponse(content_type='application/ms-excel')   
    response['Content-Disposition'] = f'attachment; filename=Expenses{str(datetime.datetime.now())}.xls'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Expenses')
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['Amount', 'Description', 'Category', 'Date']
    
    for col_nums in range(len(columns)):
        ws.write(row_num, col_nums, columns[col_nums], font_style)

    font_style = xlwt.XFStyle()
    rows = Expense.objects.filter(owner=request.user).values_list('amount', 'description', 'category', 'date')

    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, str(row[col_num]), font_style)
    
    wb.save(response)
    return response