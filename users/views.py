from django.views import generic
from django.shortcuts import redirect, reverse
from django.contrib.auth import logout, login
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from .forms import UserForm, AuthForm

class SignUpView(generic.FormView):
    '''
    Basic view for user sign up
    '''
    template_name = "users/sign_up.html"
    form_class = UserForm
    success_url = '/account/'

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return HttpResponseRedirect(self.get_success_url())

class SignInView(generic.FormView):
    '''
    Basic view for user sign in
    '''
    template_name = "users/sign_in.html"
    form_class = AuthForm
    success_url = '/account/'

    def form_valid(self, form):
        login(self.request, form.get_user())
        return HttpResponseRedirect(self.get_success_url())


def sign_out(request):
	'''
	Basic view for user sign out
	'''
	logout(request)
	return redirect(reverse('users:sign-in'))


class AccountView(generic.TemplateView):
    '''
    Basic view for user accounts
    '''
    template_name = "users/account.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


