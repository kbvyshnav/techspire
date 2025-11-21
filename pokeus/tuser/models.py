from django.db import models
import os
from cAdmin.models import CustomUser,Category

# Create your models here.
class uTickets(models.Model):
    prt = (('HIGH','High'),('Medium','Medium'),('Low','Low'))
    ticket_no = models.CharField(max_length=15,primary_key=True)
    issued_on = models.DateTimeField(auto_now=False)
    maker = models.ForeignKey(CustomUser,on_delete=models.DO_NOTHING,verbose_name='maker',related_name='umaker')
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
        if self.file:
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
        super(uTickets, self).save(*args, **kwargs)
        


