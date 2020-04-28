from django.urls import path, include

from . import views
from .views import *

urlpatterns = [
    path('', view_home, name='home'),
    path('create_run', view_stanovisko, name='stanovisko'),
    path('create_page_success', view_page_success, name='page_success'),
    path('create_page', view_page, name='page')

]
