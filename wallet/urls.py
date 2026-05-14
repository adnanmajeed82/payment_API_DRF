from django.urls import path
from .views import SendMoneyView

urlpatterns = [
    path('send/', SendMoneyView.as_view()),
]