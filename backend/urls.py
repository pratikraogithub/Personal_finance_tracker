from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


from finance.views import AIFinanceAssistantAPIView
# from finance.views import ai_finance_assistant
# from finance.views import ai_query

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),
    path('api/finance/', include('finance.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("api/ai-assistant/", AIFinanceAssistantAPIView.as_view(), name="ai-finance-assistant"),
    # path("api/ai-query/", ai_query, name="ai-query"),
]
