from django.urls import path
from .views import category_list_create, get_balance, monthly_summary, transaction_list_create

urlpatterns = [
    path('categories/', category_list_create, name='category-list-create'),
    path('transactions/', transaction_list_create, name='transaction-list-create'),
    path('balance/', get_balance, name='get-balance'),
    path('summary/monthly/', monthly_summary, name='monthly-summary'),

]
