from . import views
from django.urls import path
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('general', views.general_settings, name='general'),
    path('account', views.account_settings, name='account'),
    path('change-account-info', csrf_exempt(views.change_account_info), name='change-account-info'),
    path('change-password', views.change_password, name='change-password'),
    path('deactivate-account', views.deactivate_account, name='deactivate-account'),
    path('delete-account', views.delete_account, name='delete-account'),
    path('edit-category', csrf_exempt(views.edit_category), name='edit-category'),
    path('delete-category', views.del_category, name='delete-category'),
    path('edit-source', csrf_exempt(views.edit_source), name='edit-source'),
    path('delete-source', views.del_source, name='delete-source'),
    path('upload', views.upload, name='upload'),
    path('user-has-file', views.user_has_file, name='user-has-file'),
    path('upload-changes', views.upload_changes, name='upload-changes')
]