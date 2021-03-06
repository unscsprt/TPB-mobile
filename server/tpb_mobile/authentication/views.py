from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic.base import View


class LoginView(View):
    template_name = 'mobile/registration/login.html'
    
    def get(self, request, *args, **kwargs):
        next_url = request.GET.get('next', default=None)
        return render(request, self.template_name, {'next': next_url})
        
    def post(self, request, *args, **kwargs):
        result = attempt_login(request)
        if result['status'] == True:
            next_url = request.POST.get('next')
            return HttpResponseRedirect('/')
            if next != "None":
                return HttpResponseRedirect(next_url)
            else:
                return HttpResponseRedirect('/')
        else:
            return render(request, self.template_name, {'message': result['message']})
      
def attempt_login(request):
    '''
    attempts to log user in using Django's authentication system
    '''
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
            return {'status': True, 'message': "Login successful."}
        else:
            return {'status': False, 'message': "That user is no longer active."}
    else:
        return {'status': False, 'message': "Your username and password didn't match. Please try again."}
        
def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')