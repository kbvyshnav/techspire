from django.contrib.auth import get_user_model
from .models import *
from tuser.models import uTickets
from cAdmin.models import Tickets
from django.db.models import Q,Count,OuterRef, Subquery

User = get_user_model()



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

def searchfilter(user_id,frmdate,todate,searchkey=None , db = None):

   results = None
   if searchkey == 'None':
        searchkey = None
   if (searchkey is not None ) :

    results = (Tickets.objects.filter(Q(issued_on__date__range=(frmdate, todate)) & Q(old_ticket__isnull=False) & Q(ticket_no__icontains = searchkey)).annotate(maker_ids=Subquery(uTickets.objects.filter(ticket_no=OuterRef('old_ticket')).values('maker_id__username')[:1])).order_by('-updated_on'))
    
    # Tickets.objects.filter( Q(issued_on__date__range=(frmdate, todate)) & Q(ticket_no__icontains = searchkey) ).order_by('-updated_on')

   elif(searchkey is None  ):
    
    results = (Tickets.objects.filter(Q(issued_on__date__range=(frmdate, todate)) &Q(old_ticket__isnull=False)).annotate(maker_ids=Subquery(uTickets.objects.filter(ticket_no=OuterRef('old_ticket')).values('maker_id__username')[:1])).order_by('-updated_on'))

   return results


def inqueueSearchFilter(user_id,frmdate,todate,searchkey=None , db = None):

   inqueue = None
   if searchkey == 'None':
        searchkey = None
   if (searchkey is not None ) :

    inqueue = uTickets.objects.filter(Q(issued_on__date__range=(frmdate, todate)) & Q( status = 'SP') & Q(ticket_no__icontains = searchkey)).order_by('-updated_on')

   elif(searchkey is None ):
    
    inqueue = uTickets.objects.filter(Q(issued_on__date__range=(frmdate, todate)) & Q( status = 'SP')).order_by('-updated_on')

   return inqueue