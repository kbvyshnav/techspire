from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.auth.models import AbstractUser,BaseUserManager,AbstractBaseUser
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField
from datetime import datetime,timedelta
# Create your models here.
import os

# class CUserManager(BaseUserManager):
#     pass






class Company(models.Model):
    companyId = models.AutoField(primary_key=True,)
    companyName = models.CharField(max_length=100,verbose_name='Company Name',editable=True,) # Check req if there any constraints about Duplicate company name 
    companyAddr = models.TextField(max_length=300,editable=True)
    companyCntry = CountryField()
    companyCntct = PhoneNumberField(null = True ,unique=True,help_text="Enter your mobile number in any format, it will be automatically formatted.",error_messages={
            'unique': 'Primary contact number is already in use.',
           
        })
    companyCode = models.CharField(max_length = 4,verbose_name = 'Company Code', help_text='A short code for company name',unique=True,error_messages={'unique':'Compnay with this code already exists ,Pleas try another!','null' : "This field can't be null."})
    companymobs = PhoneNumberField(unique=True,help_text = "Add alternate contact number",null=True,error_messages={
            'unique': 'Alternate Contact number is already in use.',
            
        })
    companyMail = models.EmailField(editable=True,unique=True,error_messages={
            'unique': 'This mail id is already in use.',
            
        })
    is_active = models.BooleanField(default=True,editable=True)



    def __str__(self) -> str:
        return f"{self.companyName}"

class Department(models.Model):
    deptId=models.AutoField(primary_key=True)
    deptName=models.CharField(max_length=30)
    companyId=models.ForeignKey(Company,on_delete=models.CASCADE)
    #Admin_Id=models.ForeignKey(Admin,on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.deptName}"
    

class CustomUser(AbstractUser):
    ROLE_CHOICES = (('D','Developer'),('T','Tester'),('' ,'None'),('A','Admin'),('U','User'))
    #is_admin = models.BooleanField(default=False)
    company = models.ForeignKey(Company,on_delete=models.CASCADE,null=True)
    department = models.ForeignKey(Department,on_delete=models.CASCADE,null=True,blank=True)
    contact = models.CharField(max_length=17,null=True)
    role = models.CharField(max_length=2,choices=ROLE_CHOICES,blank=True)

    def __str__(self) -> str:
        return f"{self.username}"



class Priority(models.Model):
    id=models.IntegerField(primary_key=True)
    priority=models.CharField(max_length=30)
    days=models.IntegerField(editable=True,default=1)

    def __str__(self) -> str:
        return f"{self.priority}"

class Category(models.Model):
    ctgryId = models.AutoField(primary_key=True)
    ctgryName = models.CharField(max_length=30,editable=True)
    company = models.ForeignKey(Company,on_delete= models.CASCADE)
    is_active = models.BooleanField(editable=True,default=True)
    # adminId = 

    def __str__(self) -> str:
        return f"{self.ctgryName}"

# class Tickets(models.Model):
#     ticketId = models.BigAutoField(primary_key=True)
#     ticketHolder = models.CharField(max_length=1,null=True)
#     issueHead = models.CharField(max_length=30)
#     issuedDate = models.DateField(auto_now=True)
#     dateOfClosing = models.DateField(null=True)
#     clientId = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
#     status = models.CharField(max_length=10,default='P')
#     category = models.ForeignKey(Category,on_delete=models.SET_NULL,null=True)
#     priority = models.ForeignKey(Priority,on_delete= models.CASCADE)
#     dev_id = models.CharField(max_length =8 , blank=True ,)
#     #developersId = models.ForeignKey
#     #testerId 
    

# class TicketActions(models.Model):
#     ticketRef = models.ForeignKey(Tickets,on_delete=models.CASCADE,)
#     status = models.CharField(max_length=5,)
#     issue = models.TextField(max_length=500,editable=True)
#     media = models.FileField(upload_to='Media/',null=True)
#     DOE = models.DateField(auto_now=True) # Date of entry
#     prevState = models.CharField(max_length=6,null=True)
#     is_reopened = models.BooleanField(default=False)


"""
Model of Ticket.
"""
# class Tickets(models.Model):
#     t_id = models.IntegerField(editable=True,blank=True,null=True)
#     doe = models.DateField(auto_now=True)
#     status = models.CharField(max_length=6)
#     ctg = models.ForeignKey(Category,on_delete=models.SET_NULL,null=True)
#     cli = models.ForeignKey(CustomUser,on_delete=models.DO_NOTHING, related_name='client_id',blank=True,null=True)
#     prt = models.CharField(default=None,max_length=1,null=True,blank=True)  
#     exp = models.DateField(editable=True,blank=True,null=True)
#     head = models.CharField(max_length=50,)
#     dev = models.ForeignKey(CustomUser,on_delete=models.DO_NOTHING,related_name='developer_id',null=True,blank=True)
#     tester = models.ForeignKey(CustomUser,on_delete=models.DO_NOTHING, related_name='tester_id',null=True,blank=True)
#     issue = models.TextField(max_length=500)
#     Media = models.FileField(upload_to='Media/',null=True,blank=True)
#     notification = models.BooleanField(default=False)
#     slno = models.IntegerField(editable=True,blank=True,null=True)
#     cur_status = models.CharField(max_length=5,blank=True,null=True)




class Tickets(models.Model):
    prt = (('HIGH','High'),('Medium','Medium'),('Low','Low'))
    ticket_no = models.CharField(max_length=15,primary_key=True)
    issued_on = models.DateTimeField(auto_now=False)
    maker = models.ForeignKey(CustomUser,on_delete=models.DO_NOTHING,verbose_name='maker',related_name='maker')
    client = models.CharField(max_length=100)
    subject = models.CharField(max_length=20,)
    desc = models.TextField(max_length=500,null=True)
    priority = models.CharField(choices=prt,max_length=10,null=True)
#   attachment = 
    file = models.FileField(upload_to='',null=True,blank=True,help_text='Related to issue')
    expiry = models.DateField(null=True,blank=True)
    status = models.CharField(max_length=4,)
    approved_by = models.CharField(max_length=50,)
    approved_on = models.DateTimeField(null=True)
    updated_on = models.DateTimeField(null=True,auto_now=True)
    updated_by = models.ForeignKey(CustomUser,on_delete=models.DO_NOTHING,verbose_name='updated_by',)
    closed_by = models.CharField(max_length=50,null=True)
    closed_on = models.DateTimeField(null=True)
    old_ticket = models.CharField(max_length=15,null=True)
    old_ticket_date = models.DateTimeField(null=True)
    new_ticket = models.BigIntegerField(null=True)
    new_ticket_date = models.DateTimeField(null=True)
    dev_id = models.CharField(max_length=50,default='',null=True) #uses username
    tester_id = models.CharField(max_length=50,default = '',null=True) #uses username
    dev_assigned_date = models.DateTimeField(null=True)
    tester_assigned_date = models.DateTimeField(null=True)
    category  = models.ForeignKey(Category,on_delete=models.DO_NOTHING)
    remarks = models.CharField(max_length=250,null = True,blank=True,default='')
    rmrk_files = models.FileField(upload_to='',null=True,blank=True,help_text='Related to issue')
    tgt_days = models.IntegerField(null=True,blank=True,help_text='Target date')
    # files = models.File
    # tstr_expiry = models.DateField(null=True)

    def save(self, *args, **kwargs):
        print('================',self.file.name,'============')
        if self.file and self.approved_on is None and self.file.name[12:15] != "TMP":
            _, extension = os.path.splitext(self.file.name)
            
            # Replace spaces with hyphens in the new filename
            new_filename = f"{self.ticket_no}_{self.updated_on.date()}{extension}"
            new_filename = new_filename.replace(" ", "-")

            self.file.name = os.path.join('tickets', new_filename)
            # print(self.file.name,'File name')
        
        if self.rmrk_files:
            _, extension = os.path.splitext(self.rmrk_files.name)
            new_filename = f"{self.ticket_no}_{self.updated_on.date()}{extension}"
            new_filename = new_filename.replace(" ", "-")
            self.rmrk_files.name = os.path.join('remarks', new_filename)
            print('file name',self.file.name)
        super(Tickets, self).save(*args, **kwargs)
        


class TicketLogs(models.Model):
    prt = (('H','High'),('M','Medium'),('L','Low'))
    ticket_no = models.CharField(max_length=15,primary_key=True)
    issued_on = models.DateTimeField()
    maker = models.CharField(max_length=50)
    client = models.CharField(max_length=50)
    subject = models.CharField(max_length=20,)
    desc = models.CharField(max_length=500,null=True)
    priority = models.CharField(choices=prt,max_length=10,null=True)
#   attachment = 
    rmrk_files = models.FileField(upload_to='',null=True,blank=True,help_text='Related to issue')
    file = models.FileField(upload_to='tickets',null=True)
    expiry = models.DateField(null=True)
    status = models.CharField(max_length=4,)
    approved_by = models.CharField(max_length=50,)
    approved_on = models.DateTimeField(null=True)
    updated_on = models.DateTimeField()
    updated_by = models.ForeignKey(CustomUser,on_delete=models.DO_NOTHING,verbose_name='updated_by',)
    closed_by = models.CharField(max_length=50,null=True)
    closed_on = models.DateTimeField(null=True)
    old_ticket =models.CharField(max_length=15,null=True)
    old_ticket_date = models.DateTimeField(null=True)
    new_ticket = models.BigIntegerField(null=True)
    new_ticket_date = models.DateTimeField(null=True)
    dev_id = models.CharField(max_length=50,default='',null=True) #uses username
    tester_id = models.CharField(max_length=50,default = '',null=True) #uses username
    dev_assigned_date = models.DateTimeField(null=True)
    tester_assigned_date = models.DateTimeField(null=True)
    category  = models.ForeignKey(Category,on_delete=models.DO_NOTHING,null=True)
    remarks = models.CharField(max_length=250,null = True,blank=True,)
    # tstr_expiry = models.DateField(null=True)
    
    def save(self, *args, **kwargs):
        
        if self.rmrk_files:
            _, extension = os.path.splitext(self.rmrk_files.name)
            new_filename = f"{self.ticket_no}_{self.updated_on.date()}{extension}"
            new_filename = new_filename.replace(" ", "-")
            self.rmrk_files.name = os.path.join('remarks', new_filename)
        super(TicketLogs, self).save(*args, **kwargs)
        
    
    class Meta:
        # Define the composite primary key using unique_together
        unique_together = ('ticket_no', 'updated_on')
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['ticket_no', 'updated_on'], name='unique_combination'
            )
        ]







