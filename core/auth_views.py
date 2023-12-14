from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import views as auth_views
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.views import View


class LoginView(auth_views.LoginView):
    template_name = 'core/form.html'    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Login'
        context['form_title'] = 'Login'
        context['form_btn'] = 'Login'
        return context
    

class RegisterView(View):
    template_name = 'core/form.html'

    def get(self, request):
        form = UserCreationForm()
        return render(request, self.template_name, {'form': form, 'form_title': 'Register', 'form_btn': 'Register', 'title': 'Register'})

    def post(self, request):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
        return render(request, self.template_name, {'form': form, 'form_title': 'Register', 'form_btn': 'Register', 'title': 'Register'})