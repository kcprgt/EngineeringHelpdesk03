from django.urls import path
from .views import register

urlpatterns = [
    #path('login/', CustomLoginView.as_view(), name='login'),
    path('/', register, name='register'),
]