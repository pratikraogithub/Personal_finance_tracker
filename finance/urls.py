'''
from django.urls import path
from .views import category_list_create, get_balance, monthly_summary, transaction_list_create

urlpatterns = [
    path('categories/', category_list_create, name='category-list-create'),
    path('transactions/', transaction_list_create, name='transaction-list-create'),
    path('balance/', get_balance, name='get-balance'),
    path('summary/monthly/', monthly_summary, name='monthly-summary'),

]
'''

from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, TransactionViewSet
from django.urls import path

router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='category')
router.register('transactions', TransactionViewSet, basename='transaction')

# urlpatterns = [
#     path('balance/', get_balance),
#     path('summary/monthly/', monthly_summary),
# ]

# urlpatterns += router.urls
urlpatterns = router.urls