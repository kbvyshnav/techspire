from django.db import connection
from .models import *
from django.db import connection
from django.db.models import Max
from datetime import datetime
from django.db.models import Q,Count,F
from Chat.models import *
from django.db.models import Q,Count,F,Min,Max,OuterRef,Subquery,Case, When, Value, CharField

#flag =N for new ticket log
def CpyLog(ticketQset,remarks=None,remarks_file=None):
    if remarks is None or remarks == '':
        print('none part')
        log = TicketLogs.objects.create(ticket_no=ticketQset.ticket_no,file = ticketQset.file,issued_on = ticketQset.issued_on,subject = ticketQset.subject,desc = ticketQset.desc , priority = ticketQset.priority , expiry = ticketQset.expiry, status = ticketQset.status , approved_by = ticketQset.approved_by , approved_on = ticketQset.approved_on, updated_on = ticketQset.updated_on ,updated_by = ticketQset.updated_by , closed_by = ticketQset.closed_by , closed_on = ticketQset.closed_on , old_ticket=ticketQset.old_ticket ,old_ticket_date= ticketQset.old_ticket_date , new_ticket = ticketQset.new_ticket , new_ticket_date = ticketQset.new_ticket_date , dev_id = ticketQset.dev_id , tester_id = ticketQset.tester_id , dev_assigned_date = ticketQset.dev_assigned_date , tester_assigned_date = ticketQset.tester_assigned_date , client = ticketQset.client , maker = ticketQset.maker.username , category_id = ticketQset.category_id )
    else:
        print('smthg')
        log = TicketLogs.objects.create(ticket_no=ticketQset.ticket_no,remarks = remarks,rmrk_files=ticketQset.rmrk_files,file = ticketQset.file,issued_on = ticketQset.issued_on,subject = ticketQset.subject,desc = ticketQset.desc , priority = ticketQset.priority , expiry = ticketQset.expiry, status = ticketQset.status , approved_by = ticketQset.approved_by , approved_on = ticketQset.approved_on, updated_on = ticketQset.updated_on ,updated_by = ticketQset.updated_by , closed_by = ticketQset.closed_by , closed_on = ticketQset.closed_on , old_ticket=ticketQset.old_ticket ,old_ticket_date= ticketQset.old_ticket_date , new_ticket = ticketQset.new_ticket , new_ticket_date = ticketQset.new_ticket_date , dev_id = ticketQset.dev_id , tester_id = ticketQset.tester_id , dev_assigned_date = ticketQset.dev_assigned_date , tester_assigned_date = ticketQset.tester_assigned_date , client = ticketQset.client , maker = ticketQset.maker.username , category_id = ticketQset.category_id )



def TcktCde(request):  
    latest_entry = None
    Cmpnycde = Company.objects.get(companyId=request.user.company.companyId).companyCode
    current_year = datetime.now().strftime('%y')
    current_month = datetime.now().strftime('%m')

    # Fetch the latest ticket based on issued_on
    latest_ticket = Tickets.objects.filter(
        client=request.user.company.companyName ).order_by('-issued_on').first()
        
    if latest_ticket:
        # Extract the year from the latest ticket number
        latest_year = latest_ticket.ticket_no[4:6]
        latest_serial = int(latest_ticket.ticket_no[8:])
            
        # Check if the year matches the current year
        if latest_year == current_year:
            # Increment the serial number
            latest_entry = str(latest_serial + 1).zfill(4)
        else:
            # Start from 0001 if the year has changed
            latest_entry = '0001'
    else:
        # No tickets exist, start with 0001
        latest_entry = '0001'
    # Construct the new ticket ID
    ticket_id = f"{Cmpnycde}{current_year}{current_month}{latest_entry}"
    return ticket_id




def outlook(ticket_id):
    logs = TicketLogs.objects.filter(ticket_no = ticket_id).order_by('updated_on')
    return logs

# def userformvalidator

# def searchfilter(cmpnyId,frmdate,todate,searchkey=None):

#    results = None
#    cond = '';

#    if (searchkey is not None and cmpnyId != '*') :

#     results = Tickets.objects.filter(Q(maker__company__companyCode=cmpnyId) & Q(issued_on__date__range=(frmdate, todate)) & Q(ticket_no__icontains = searchkey) ).order_by('-updated_on')

#    elif(searchkey is None and cmpnyId != '*'):
#     results = Tickets.objects.filter(Q(maker__company__companyCode=cmpnyId) & Q(issued_on__date__range=(frmdate, todate)) ).order_by('-updated_on')

#    elif(searchkey is not None and cmpnyId == '*'):
#     results = Tickets.objects.filter(Q(issued_on__date__range=(frmdate, todate)) & Q(ticket_no__icontains = searchkey)).order_by('-updated_on')

#    elif(searchkey is None and cmpnyId =="*"):
#     results = Tickets.objects.filter(Q(issued_on__date__range=(frmdate, todate)) ).order_by('-updated_on')


#    return results

def searchfilter(cmpnyId, frmdate =None, todate= None, searchkey=None):
    filters = Q()
    if frmdate is not None and todate is not None:
        filters &= Q(issued_on__date__range=(frmdate, todate))

    if cmpnyId != '*':
        filters &= Q(maker__company__companyCode=cmpnyId)
    
    if searchkey is not None:
        filters &= Q(ticket_no__icontains=searchkey)

    results = Tickets.objects.filter(filters).order_by('-updated_on')
    return results

    # if cmpnyId != '*' and frmdate == '' and todate == ''  : # for all tickets
    #     print('first')
    #     tickets = Tickets.objects.filter(Q(maker__company__companyCode=cmpnyId)).order_by('-updated_on')
    # if cmpnyId is not None and cmpnyId != '*' and frmdate != '' and todate != '' and searchkey is None:
    #     print('second',todate)                                                           
    #     tickets = Tickets.objects.filter(Q(maker__company__companyCode=cmpnyId) & Q(issued_on__date__range=(frmdate, todate))).order_by('-updated_on')

    # elif cmpnyId is not None and cmpnyId != '*' and frmdate != '' and todate != '' and searchkey is not None:
    #     print('secondxxxxxxxxxxx',todate)                                                           
    #     tickets = Tickets.objects.filter(Q(maker__company__companyCode=cmpnyId) & Q(issued_on__date__range=(frmdate, todate)) & Q(ticket_no__icontains = searchkey) ).order_by('-updated_on')

    # elif cmpnyId == '*' and frmdate != '' and todate != ''  and searchkey != None:
    #     tickets = Tickets.objects.filter( Q(issued_on__date__range=(frmdate, todate)) & Q(ticket_no__icontains = searchkey)).order_by('-updated_on')

    # elif cmpnyId == '*' and frmdate != '' and todate != '':
    #     tickets = Tickets.objects.filter( Q(issued_on__date__range=(frmdate, todate))).order_by('-updated_on')


def chat_notification(request, tickets):
    for ticket in tickets:
        count = tcktChat.objects.filter(ticket_no=ticket.ticket_no, seen__contains= request.user.role ).count()
        ticket.notification =count
        # count_res[ticket.ticket_no] = count  # Add to the dictionary
    return True  # or JsonResponse(count_res) if you're returning it as a response

def bell_notification(request,):
    ticket_counts = tcktChat.objects.filter(seen__contains = request.user.role).values('ticket_no').annotate(count=Count('msg_id'))
    return ticket_counts


