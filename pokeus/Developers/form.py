from django import forms
from cAdmin.models import *



class acptTicket(forms.ModelForm):
    class Meta:
        model = Tickets
        fields = ['expiry']