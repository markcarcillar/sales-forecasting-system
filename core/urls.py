from django.contrib.auth import views as dj_auth_views
from django.urls import path

from . import views
from . import auth_views
from . import apis


urlpatterns = [
    path('', views.index_view, name='index'),
    path('industry-info/<str:industry_name>/', views.industry_info_view, name='industry-info'),
    path('main/<str:industry_name>/', views.main_view, name='main'),

    # Help URLs
    path('help/', views.help_view, name='help'),
    path('help/how-to-register-and-login-account/', views.how_to_register_and_login_account_view, name='how-to-register-and-login-account'),
    path('help/using-the-tool-for-each-specific-industry/', views.using_the_tool_for_each_specific_industry_view, name='using-the-tool-for-each-specific-industry'),
    path('help/downloading-and-deleting-forecasted-results/', views.downloading_and_deleting_forecasted_results_view, name='downloading-and-deleting-forecasted-results'),

    # Footer URLs
    path('privacy-policy/', views.privacy_policy_view, name='privacy-policy'),
    path('tos/', views.tos_view, name='tos'),
    path('contact/', views.contact_view, name='contact'),

    # API URLs
    path('clear-all-forecast/<str:industry_name>/', apis.ClearAllForecastAPIView.as_view(), name='clear-all-forecast'),
    path('download-forecast/<int:forecast_id>/', apis.download_forecast_api_view, name='download-forecast'),
    path('forecast/<str:industry_name>/', apis.ForecastAPIView.as_view(), name='sales-data'),

    # Authentication URLs
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', dj_auth_views.LogoutView.as_view(), name='logout'),
    path('register/', auth_views.RegisterView.as_view(), name='register'),
]