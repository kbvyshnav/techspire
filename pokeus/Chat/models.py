from django.db import models
from cAdmin.models import CustomUser,Tickets

# Create your models here.

class tcktChat(models.Model):
    msg_id = models.BigAutoField(primary_key=True)
    user_id = models.ForeignKey(CustomUser,on_delete=models.DO_NOTHING)
    msg = models.CharField(max_length=500,blank=True,null=True,)
    updated_on = models.DateTimeField(auto_now=True)
    ticket_no = models.CharField(max_length=15,null=bool,)
    seen_by = models.CharField(max_length=150,blank=True)
    atchmnt = models.FileField(upload_to='tickets',null=True,blank=True) #Refers attachement
    seen = models.CharField(max_length=4,blank=True,)

