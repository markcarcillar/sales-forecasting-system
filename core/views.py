from django.shortcuts import render
from django.conf import settings
from django.http import Http404

from .models import ForecastModel


def index_view(request):
    industries = [i['Industry'] for i in settings.INDUSTRIES]
    return render(request, 'core/industry_selection.html', {'industries': industries})


def industry_info_view(request, industry_name):
    if not industry_name in (i['Industry'] for i in settings.INDUSTRIES):
        raise Http404('Industry does not exist')
    
    context = {
        'title': f'{industry_name} Industry Info',
        'industry_name': industry_name,
        'industry_description': next((i['Description'] for i in settings.INDUSTRIES if i['Industry'] == industry_name), ''),
        'required_data': next((i['Attributes'] for i in settings.INDUSTRIES if i['Industry'] == industry_name), []),
        'sample_json_format': next((i['SampleJSON'] for i in settings.INDUSTRIES if i['Industry'] == industry_name), ''),
        'sample_csv_format': next((i['SampleCSV'] for i in settings.INDUSTRIES if i['Industry'] == industry_name), '')
    }
    return render(request, 'core/industry_info.html', context)


def main_view(request, industry_name):
    if request.user.is_authenticated:
        forecasts = ForecastModel.objects.filter(user=request.user, industry=industry_name).order_by('-date')
    else:
        forecasts = []
    return render(request, 'core/main.html', {'industry': industry_name, 'forecasts': forecasts, 'title': f'{industry_name} Forecast Tool'})


def privacy_policy_view(request):
    return render(request, 'core/privacy_policy.html', {'title': f'Privacy Policy'})


def tos_view(request):
    return render(request, 'core/tos.html', {'title': f'Terms of Use'})


def contact_view(request):
    return render(request, 'core/contact.html', {'title': f'Contact'})


def help_view(request):
    return render(request, 'core/help/index.html', {'title': f'Help'})


def how_to_register_and_login_account_view(request):
    return render(request, 'core/help/how_to_register_and_login_account.html', {'title': f'How to register and login account?'})


def using_the_tool_for_each_specific_industry_view(request):
    return render(request, 'core/help/using_the_tool_for_each_specific_industry.html', {'title': f'Using the tool for each specific industry.'})


def downloading_and_deleting_forecasted_results_view(request):
    return render(request, 'core/help/downloading_and_deleting_forecasted_results.html', {'title': f'Downloading and deleting forecasted results.'})