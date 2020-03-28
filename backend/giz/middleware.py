from re import compile
from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.http import is_safe_url


white_list_paths = (
    reverse('account_login'),
    '/account/(?!.*(?:signup))',
    # block unauthenticated users from creating new accounts.
    '/static/*',
)
white_list = [compile(x) for x in white_list_paths + getattr(settings, "AUTH_EXEMPT_URLS", ())]

class LoginRequiredMiddleware(object):
    
    """
    Requires a user to be logged in to access any page that is not white-listed.
    """
    redirect_to = getattr(settings, 'LOGIN_URL', reverse('account_login'))

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    # def process_exception(self, request, exception):
    #     return HttpResponse("in exception")

    def process_request(self, request):
        if not request.user.is_authenticated:
            if not any(path.match(request.path) for path in white_list):
                return HttpResponseRedirect(
                    '{login_path}?next={request_path}'.format(
                        login_path=self.redirect_to,
                        request_path=request.path))
