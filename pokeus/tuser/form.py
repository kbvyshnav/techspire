from django import forms
from cAdmin.models import Tickets,Category
from .models import uTickets

class TicketForm(forms.ModelForm):


    class Meta:
        model = uTickets
        exclude = ['ticket_no', 'issued_on', 'maker', 'status', 'client', 'expiry', 'approved_by', 'approved_on', 'updated_on','updated_by','closed_by','closed_on','old_ticket','old_ticket_date','new_ticket','new_ticket_date','dev_id','tester_id','dev_assigned_date','tester_assigned_date','prt']
    
    def __init__(self, *args, **kwargs):
        company = kwargs.pop('company', None)
        super(TicketForm, self).__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(company = company ,is_active = True)
        
