from django import forms
from .models import Company,Department,CustomUser,Category


class addCompany(forms.ModelForm):
    
    class Meta:
        model = Company
        fields = '__all__'
        exclude = ['companyId',]
        # help_texts = { "companyCntct": "Enter valid format +countrycode , mobile number"}

class editCompany(forms.ModelForm):
    
    class Meta:
        model = Company
        fields = '__all__'
        exclude = ['companyId','companyCode']
        # help_texts = { "companyCntct": "Enter valid format +countrycode , mobile number"}


class addDepartmentf(forms.ModelForm):

    class Meta:
        model = Department
        fields = ['deptName']
        exclude = ['deptId','company']

class UserAdd(forms.ModelForm):
    
    class Meta:
        model=CustomUser
        fields= '__all__'
        exclude=['id','company','last_login','is_active','is_admin','is_superuser','is_staff','role','department']
        widgets= {
            'username':forms.TextInput(attrs={'oninput': 'this.value = this.value.replace(/ /g, "")'}),
            "date_joined":forms.DateInput(attrs={'class':"form-control",'type':"date",}),
            "password":forms.TextInput(attrs={'class':"form-control",'type':"password",}),
        }
        
    # def is_valid(self):
    #     valid = super().is_valid()
    #     if not valid:
    #         for field, error_list in self.errors.items():
    #             # Do something with the errors (e.g., print or log)
    #             print(f"Field: {field}, Errors: {error_list}")

    #         # You can perform additional actions based on errors

    #     return valid


class addCategoryf(forms.ModelForm):
    
    class Meta:
        model = Category
        fields = '__all__'
        exclude = ['ctgryId','company']
        # help_texts = { "companyCntct": "Enter valid format +countrycode , mobile number"}

class addDeveloper(forms.ModelForm):
    ROLE = (('D','Developer'),('T','Tester'))
    slct_role = forms.ChoiceField(choices=ROLE,)
    class Meta:
        model = CustomUser
        #fields = ['']
        exclude=['id','company','last_login','is_active','is_admin','is_superuser','is_staff','department']
        widgets = {

             "date_joined":forms.DateInput(attrs={'class':"form-control",'type':"date",}),
        }

class editDevForm(forms.ModelForm):

    class Meta:
        model = CustomUser
        exclude = ['user_permissions','groups','id','company','password','last_login','is_active','is_admin','is_superuser','is_staff','department','username','date_joined','role']


class editUsrForm(forms.ModelForm):

    class Meta:
        model = CustomUser
        exclude = ['user_permissions','groups','id','company','password','last_login','is_active','is_admin','is_superuser','is_staff','department','username','date_joined','role']
