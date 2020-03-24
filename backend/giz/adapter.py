from allauth.account.adapter import DefaultAccountAdapter
from django.forms import ValidationError

class CustomProcessAdapter(DefaultAccountAdapter):

    def clean_username(self, username):
        if len(username) > 8:
            raise ValidationError('Please enter a username value less than the current one')
        return DefaultAccountAdapter.clean_username(self,username) # For other default validations.

    def clean_email(self,email):
        RestrictedList = ['test@test.com']
        if email in RestrictedList:
            raise ValidationError('You are restricted from registering. Please contact admin.')
        return email
