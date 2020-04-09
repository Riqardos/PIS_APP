from django.urls import path, include

from . import views
from .views import *

urlpatterns = [

    path('', view_stanovisko, name='home')

]
