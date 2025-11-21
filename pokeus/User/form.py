from django import forms
from cAdmin.models import Tickets,Category,CustomUser

class TicketForm(forms.ModelForm):


    class Meta:
        model = Tickets
        exclude = ['ticket_no', 'issued_on', 'maker', 'status', 'client', 'expiry', 'approved_by', 'approved_on', 'updated_on','updated_by','closed_by','closed_on','old_ticket','old_ticket_date','new_ticket','new_ticket_date','dev_id','tester_id','dev_assigned_date','tester_assigned_date','prt']
    
    def __init__(self, *args, **kwargs):
        company = kwargs.pop('company', None)
        super(TicketForm, self).__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(company = company ,is_active = True)
        
class editUsrForm(forms.ModelForm):

    class Meta:
        model = CustomUser
        exclude = ['user_permissions','groups','id','company','password','last_login','is_admin','is_superuser','is_staff','department','username','date_joined','role']

class subUserAdd(forms.ModelForm):
    
    class Meta:
        model=CustomUser
        fields= '__all__'
        exclude=['id','company','last_login','is_admin','is_superuser','is_staff','role','department']
        widgets= {
            'username':forms.TextInput(attrs={'oninput': 'this.value = this.value.replace(/ /g, "")'}),
            "date_joined":forms.DateInput(attrs={'class':"form-control",'type':"date",}),
            "password":forms.TextInput(attrs={'class':"form-control",'type':"password",}),
        }