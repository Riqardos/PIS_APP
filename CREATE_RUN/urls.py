from django.urls import path, include

from . import views
from .views import *

urlpatterns = [
    path('', view_home, name='home'),
    path('create_run', view_stanovisko, name='stanovisko')

]
