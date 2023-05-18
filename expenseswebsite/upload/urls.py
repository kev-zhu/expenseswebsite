from django.urls import path
from . import views

urlpatterns = [ 
    path('', views.index, name="upload"),
    path('user-has-file', views.user_has_file, name='user-has-file'),
    path('upload-changes', views.upload_changes, name='upload-changes'),
    path('download-template', views.download_template, name='download-template')
]