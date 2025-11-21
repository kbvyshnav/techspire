from django.contrib.auth import get_user_model
from .models import *
from cAdmin.models import Tickets,Company
from django.db.models import Q,Count,Max
from datetime import datetime

User = get_user_model()

def TcktCdeUsr(request):
    
    latest_entry = None
    Cmpnycde = Company.objects.get(companyId = request.user.company.companyId).companyCode
    current_year = str(datetime.now().year)
    current_month = datetime.now().strftime('%m')
    # tckt_max = Cmpnycde + current_year[2:] + current_month + '9999'
    # tckt_min = Cmpnycde + current_year[2:] + current_month + '0001'
    tckt_max = Cmpnycde + 'TMP9999'
    tckt_min = Cmpnycde + 'TMP0001'
    try:
        Tckt_no = uTickets.objects.filter(client = request.user.company.companyName , ticket_no__lte = tckt_max ,ticket_no__gte = tckt_min ).aggregate(max_tckt =Max('ticket_no'))['max_tckt']
        latest_entry = str(int(Tckt_no[7:])+1)
        if (len(latest_entry) == 1) :
            latest_entry = '000' + str(latest_entry)
        elif (len(latest_entry) == 2):
            latest_entry = '00' + str(latest_entry)
        elif (len(latest_entry) == 3):
            latest_entry = '0' + str(latest_entry)
    except:
        latest_entry = '0001'
    ticket_id = Cmpnycde + 'TMP' + latest_entry
    return(ticket_id)


def outlook(ticket_id):
    pass
    # logs = TicketLogs.objects.filter(ticket_no = ticket_id).order_by('updated_on')
    # return logs

def CpyLog():
    pass



def get_company_is_active_status(username):
    try:
        company_is_active = User.objects.filter(username=username).values('company__is_active').get()
        return company_is_active['company__is_active']
    except User.DoesNotExist:
        # Handle the case where the user does not exist or is not associated with any company
        return None


'''
for copying data ticket table from log table.

'''

def searchfilter(user_id,frmdate,todate,searchkey=None):

   results = None
   if searchkey == 'None':
        searchkey = None
   if (searchkey is not None ) :

    results = uTickets.objects.filter( Q(issued_on__date__range=(frmdate, todate)) & Q(ticket_no__icontains = searchkey) & Q( maker_id = user_id) ).order_by('-updated_on')

   elif(searchkey is None):
    
    results = uTickets.objects.filter(Q(issued_on__date__range=(frmdate, todate)) & Q( maker_id = user_id) ).order_by('-updated_on')

    print(type(searchkey))


   return results