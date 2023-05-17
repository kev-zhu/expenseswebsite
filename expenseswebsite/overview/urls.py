from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [ 
    path('', views.index, name="overview"),
    path('search-overview', csrf_exempt(views.search_overview), name='search-overview'),
    path('get-one-year-data', views.get_one_year_data, name='get-one-year-data'),
    # path('export_csv', views.export_csv, name='export-csv'),
    # path('export_excel', views.export_excel, name='export-excel'),
]