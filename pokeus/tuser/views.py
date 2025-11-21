from django.shortcuts import render,get_object_or_404
from django.shortcuts import render,redirect,HttpResponse
from django.views.decorators.cache import never_cache
from django.contrib.auth import login,logout,authenticate
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Q,Count,OuterRef, Subquery
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .utils import get_company_is_active_status,searchfilter
from .models import *
from cAdmin.models import Tickets
from cAdmin.models import *
from .form import *
from datetime import datetime,timedelta
from django.http import JsonResponse
import json
from .utils import CpyLog,TcktCdeUsr
from django.forms.models import model_to_dict
import logging
from django.contrib import messages
# Create your views here.
User = get_user_model()

def userLogin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username,password=password)
        print('status',get_company_is_active_status)
        if user is not None and user.is_active and user.role == 'U' :
            login(request,user)
            return redirect('user_home')
        else:
            return render(request,'User/userindex.html',{})

    return render(request,'User/userindex.html',{})


@never_cache
@login_required(login_url="/cadmin/admin_login/")
def userHome(request,frmdate=None,todate=None,searchkey = None):

    cur_date = datetime.now()

    prev_date = cur_date - timedelta(days=30)
    
    tickets = None


    if(searchkey is None ):
        tickets = uTickets.objects.filter(Q(issued_on__range=(prev_date, cur_date )) & Q( maker_id = request.user.id) ).order_by('-updated_on')
        frmdate = prev_date.strftime('%Y-%m-%d')
        todate = cur_date.strftime('%Y-%m-%d')
        
    else:
    
        tickets = searchfilter(request.user,frmdate,todate,searchkey)


    # inbox = tickets.filter((Q(status = 'TH') | Q(status = 'PA')) & Q( maker_id = request.user.id)).annotate(count = Count('ticket_no')).order_by('-issued_on') # inbox  count and ticket

    forwarded = tickets.filter( ( Q( status = 'SP') & Q( maker_id =  request.user.id ))).annotate(count = Count('ticket_no')).order_by('-issued_on')

    approved = tickets.exclude(Q(status='SP') | Q(status='RJ') | Q(status='TC')).filter(maker_id=request.user.id).count()  

     

    rejected = tickets.filter( ( Q( status = 'RJ') & Q( maker_id = request.user.id ))).count()
    
    closed = tickets.filter(Q(status = 'TC') & Q(maker_id = request.user.id)).count() # closed tickets count

    return render(request,'User/sUserDashboard.html',{'tickets':forwarded,'approved':approved,'rejected' : rejected ,'closed':closed,'to_date':todate,'prev_date':frmdate,'keyword':searchkey})


@never_cache
@login_required(login_url="/cadmin/admin_login/")
def userSignout(request):
    logout(request)
    return redirect('admin_login')

import logging

# Use the logger to log messages
logger = logging.getLogger(__name__)


@never_cache
@login_required(login_url="/cadmin/admin_login/")
def sUserApproved(request,frmdate=None,todate=None,searchkey = None):
    cur_date = datetime.now()

    prev_date = cur_date - timedelta(days=30)
    
    tickets = None
    print(frmdate,todate)

    if(searchkey is None ):
        tickets = uTickets.objects.filter(Q(issued_on__range=(prev_date, cur_date )) & Q( maker_id = request.user.id)).order_by('-updated_on')

        frmdate = prev_date.strftime('%Y-%m-%d')
        todate = cur_date.strftime('%Y-%m-%d')
        
    else:
    
        tickets = searchfilter(request.user,frmdate,todate,searchkey)


    forwarded = tickets.filter( ( Q( status = 'SP') & Q( maker_id =  request.user.id ))).count() # inbox  count and ticket


    # approved = tickets.exclude(Q(status='SP') | Q(status='RJ') | Q(status='TC')).filter(maker_id=request.user.id).order_by('-ticket_no').annotate(count=Count('ticket_no'))  # count and tickets for forwarded message

    # approved = uTickets.objects.filter(Q(issued_on__range=(prev_date, cur_date))& Q( status = 'AC') & Q(maker_id=request.user.id)).annotate(ticket_status=Subquery(Tickets.objects.filter(old_ticket=OuterRef('ticket_no')).values('status')),
    # reference_ticket=Subquery(
    #     Tickets.objects.filter(old_ticket=OuterRef('ticket_no')).values('ticket_no')[:1]
    # ),   ).order_by('-updated_on')

    approved = uTickets.objects.filter( Q(issued_on__range=(prev_date, cur_date)) &  Q(status='AC') &   Q(maker_id=request.user.id)).annotate(
    ticket_status=Subquery( Tickets.objects.filter( old_ticket=OuterRef('ticket_no')).values('status')[:1] ), reference_ticket=Subquery(Tickets.objects.filter(old_ticket=OuterRef('ticket_no')).values('ticket_no')[:1]), user_approved = Subquery(Tickets.objects.filter(old_ticket=OuterRef('ticket_no')).values('approved_on')[:1])).order_by('-updated_on')
    
    rejected = tickets.filter(( Q( status = 'RJ') & Q( maker_id = request.user.id ))).count()

    closed = tickets.filter(Q(status = 'TC') & Q(maker_id = request.user.id)).count() # closed tickets count
    
    return render(request,'User/sUserApproved.html',{'tickets':approved,'forwarded': forwarded ,'rejected' : rejected ,'closed':closed,'to_date':todate,'prev_date':frmdate,'keyword':searchkey})


@never_cache
@login_required(login_url="/cadmin/admin_login/")
def sUserRejected(request,frmdate=None,todate=None,searchkey = None):

    cur_date = datetime.now()

    prev_date = cur_date - timedelta(days=30)
    
    tickets = None


    if(searchkey is None ):
        tickets = uTickets.objects.filter(Q(issued_on__range=(prev_date, cur_date )) & Q( maker_id = request.user.id) ).order_by('-updated_on')
        frmdate = prev_date.strftime('%Y-%m-%d')
        todate = cur_date.strftime('%Y-%m-%d')
        
    else:   
        tickets = searchfilter(request.user,frmdate,todate,searchkey)

    forwarded = tickets.filter( ( Q( status = 'SP') & Q( maker_id =  request.user.id ))).count() # inbox  count and ticket


    approved = tickets.exclude(Q(status='SP') | Q(status='RJ') | Q(status='TC')).filter(maker_id=request.user.id).count()  # count and tickets for forwarded message
    
    rejected = tickets.filter(( Q( status = 'RJ') & Q( maker_id = request.user.id ))).order_by('-ticket_no').annotate(count=Count('ticket_no'))

    closed = tickets.filter(Q(status = 'TC') & Q(maker_id = request.user.id)).count() # closed tickets count
    
    return render(request,'User/sUserRejected.html',{'tickets':rejected,'forwarded':forwarded ,'approved' : approved ,'closed':closed,'to_date':todate,'prev_date':frmdate,'keyword':searchkey})


@never_cache
@login_required(login_url="/cadmin/admin_login/")
def sUserClosed(request,frmdate=None,todate=None,searchkey = None):

    cur_date = datetime.now()

    prev_date = cur_date - timedelta(days=30)
    
    tickets = None


    if(searchkey is None ):
        tickets = uTickets.objects.filter(Q(issued_on__range=(prev_date, cur_date ))  & Q( maker_id = request.user.id) ).order_by('-updated_on')
        frmdate = prev_date.strftime('%Y-%m-%d')
        todate = cur_date.strftime('%Y-%m-%d')
        
    else:
    
        tickets = searchfilter(request.user,frmdate,todate,searchkey)

    forwarded = tickets.filter( ( Q( status = 'SP') & Q( maker_id =  request.user.id ))).count() # inbox  count and ticket


    approved = tickets.exclude(Q(status='SP') | Q(status='RJ') | Q(status='TC')).filter(maker_id=request.user.id).count()  # count and tickets for forwarded message
    
    rejected = tickets.filter(( Q( status = 'RJ') & Q( maker_id = request.user.id ))).count()

    closed = tickets.filter(Q(status = 'TC') & Q(maker_id = request.user.id)).annotate(
        reference_ticket=Subquery(
            Tickets.objects.filter(old_ticket=OuterRef('ticket_no')).values('ticket_no')[:1]
        ),
        ticket_status=Subquery(
            Tickets.objects.filter(old_ticket=OuterRef('ticket_no')).values('status')[:1]
        ),
        user_approved=Subquery(
            Tickets.objects.filter(old_ticket=OuterRef('ticket_no')).values('approved_on')[:1]
        )
    ).order_by('-ticket_no')


    return render(request,'User/sUserClosed.html',{'tickets':closed,'forwarded':forwarded,'rejected' : rejected ,'approved':approved,'to_date':todate,'prev_date':frmdate,'keyword':searchkey})


@never_cache
@login_required(login_url="/cadmin/admin_login/")
def userInProgress(request,frmdate=None,todate=None,searchkey = None):

    cur_date = datetime.now()

    prev_date = cur_date - timedelta(days=30)
    
    tickets = None


    if(searchkey is None ):
        tickets = Tickets.objects.filter(Q(issued_on__range=(prev_date, cur_date ))).order_by('-updated_on')
        frmdate = prev_date.strftime('%Y-%m-%d')
        todate = cur_date.strftime('%Y-%m-%d')
        
    else:
    
        tickets = searchfilter(request.user,frmdate,todate,searchkey)


    inbox = tickets.filter((Q(status = 'TH') | Q(status = 'PA')) & Q( maker_id = request.user.id)).count() # inbox  count and ticket

    forwarded = tickets.exclude(Q(status='TH') | Q(status='PA') | Q(status='TC')).filter(maker_id=request.user.id).order_by('-ticket_no').annotate(count=Count('ticket_no'))  # count and tickets for forwarded message
    
    closed = tickets.filter(Q(status = 'TC') & Q(maker_id = request.user.id)).count() # closed tickets count
    
    return render(request,'User/userForwarded.html',{'inbox':inbox,'tickets':forwarded,'closed':closed,'to_date':todate,'prev_date':frmdate,'keyword':searchkey})




    
@never_cache
@login_required(login_url="/cadmin/admin_login/")
def sUserRaiseTicket(request):
    ticketform = TicketForm(company = request.user.company) #company = request.user.company
    if request.method == 'POST':
        ticketform = TicketForm(request.POST, request.FILES, company=request.user.company)
        # logger.debug('is valid worked')
        if ticketform.is_valid():
            ticketform_instance = ticketform.save(commit=False)
            ticketform_instance.ticket_no =  TcktCdeUsr(request)
            client = get_object_or_404(CustomUser, id=request.user.id)
            print(client, 'client id', request.user.id)
            ticketform_instance.client = client.company.companyName
            ticketform_instance.maker = client
            ticketform_instance.issued_on = datetime.now()
            ticketform_instance.updated_by = request.user
            ticketform_instance.updated_on = datetime.now()
            ticketform_instance.status = 'SP'
            ticketform_instance.save()
            # CpyLog(ticketform_instance)
            
            # # Get the ID of the inserted row
            # inserted_id = ticketform_instance.id
            # # Update the t_id field with the inserted ID
            # ticketform_instance.t_id = inserted_id
            # ticketform_instance.save()
            from django.contrib import messages
            messages.success(request, 'Ticket registered with ticket number : ' + str(ticketform_instance.ticket_no))
            return redirect('sub_user_home') 
    
    return render(request, 'User/sUserRaiseTicket.html', {'form': ticketform})

@never_cache
@login_required(login_url="/cadmin/admin_login/")
def userActiveDashboard(request,):
    tickets = Tickets.objects.filter(status='A',cli_id = request.user.id)
    
    ticket_data = [
        {
            'ticketid': ticket.t_id,
            'clientid': ticket.cli.username,
            'issue': ticket.head,
            #'priority': ticket.priority.priority,  # Access the related field (name) of the priority model
            'issueddate':Tickets.objects.filter(status='A').order_by('doe').first().doe.strftime('%Y-%m-%d'),
            'DOExp': ticket.exp.strftime('%Y-%m-%d'),
            'category': ticket.ctg.ctgryName, #if ticket.category else None,  Access the related field (name) of the category model
            # 'DOE': TicketActions.objects.get(ticketRef=ticket.ticketId).DOE.strftime('%Y-%m-%d'),
            'issuedesc': ticket.issue,
            'assigned_to': ticket.dev_id,
        }
        for ticket in tickets
    ]
    ticket_count  = {
        'pendings' : Tickets.objects.filter(status = 'P',cli_id = request.user.id).count()

    }

    #logger.info("ticket_data: %s", ticket_data)
    
    t_data = {
        'ticket_data' : ticket_data,
        'ticket_count' : ticket_count,
    } 

    print(t_data)

    data = json.dumps(t_data)
    return JsonResponse(data, safe=False)


def cancelTicket(request):
    pass

@never_cache
@login_required(login_url="/cadmin/admin_login/")
def deleteTicket(request,ticketid):
    try:
        ticket = get_object_or_404(Tickets, ticketId=ticketid)
        ticket.delete()
        from django.contrib import messages
        messages.success(request, 'Deleted!')
        return redirect('user_home')
    except:
        from django.contrib import messages
        messages.success(request, 'Deleted!')
        return redirect('user_home')

@never_cache
@login_required(login_url="/cadmin/admin_login/")
def liveFwd(request,ticket_id):
    ticket =  Ticket.objects.get(ticket_no = ticket_id )
    # CpyLog(ticket)
    ticket.status = 'RC'
    ticket.updated_by = request.user
    ticket.save()
    CpyLog(ticket)
    messages.success(request,'Proceeded to Live')
    return redirect('user_home')

@never_cache
@login_required(login_url="/cadmin/admin_login/")
def usrInbox(request):
    print(request.POST)
    ticket_id = request.POST['updtid']
    ticket = Tickets.objects.get(ticket_no = ticket_id)
    
    
    if ticket.status == 'PA':
        # CpyLog(ticket)
        ticket.updated_by = request.user
        if request.POST['remarks'] != '':
            ticket.remarks = request.POST['remarks']
        if 'rmk_files' in request.FILES:
                ticket.rmrk_files = request.FILES['rmk_files']
        ticket.status = 'RC'
        ticket.save()
        CpyLog(ticket,request.POST['remarks'],request.FILES.get('rmk_files', None))
        messages.success(
            request, 'Request has sent to admin!'
        )
    if ticket.status == 'TH':   #Mark
        # CpyLog(ticket)
        ticket.updated_by = request.user
        ticket.status = 'TA'
        if request.POST['remarks'] != '':
            ticket.remarks = request.POST['remarks']
        if 'rmk_files' in request.FILES:
                ticket.rmrk_files = request.FILES['rmk_files']
        ticket.save()
        CpyLog(ticket,request.POST['remarks'],request.FILES.get('rmk_files', None))
        messages.success(
            request, 'Clarification closed!'
        )
    if 'reject' in request.POST:
        if request.POST['reject'] == 'R': # For canceling live push
            # CpyLog(ticket)
            ticket.updated_by = request.user
            ticket.status = 'CR'
            if request.POST['remarks'] != '':
                ticket.remarks = request.POST['remarks']
            if 'rmk_files' in request.FILES:
                ticket.rmrk_files = request.FILES['rmk_files']
            ticket.save()
            CpyLog(ticket,request.POST['remarks'],request.FILES.get('rmk_files', None))
            messages.success(request, 'Live proceeding postponed.')
    return redirect('user_inprogress')

@never_cache
@login_required(login_url="/cadmin/admin_login/")
def usersearch(request):
    if request.method == 'POST':
        if  request.POST['page_id_val'] == 'F' :

                return redirect('sub_user_home',frmdate = request.POST['fromDateInput'],todate=request.POST['toDateInput'], searchkey =  request.POST['keyword'].strip() or None)

        elif  request.POST['page_id_val'] == 'A':

            return redirect('sub_user_approved',frmdate = request.POST['fromDateInput'],todate=request.POST['toDateInput'], searchkey=  request.POST['keyword'].strip() or None)
        
        elif request.POST['page_id_val'] == 'R':
            return redirect('sub_user_rejected',frmdate = request.POST['fromDateInput'],todate=request.POST['toDateInput'], searchkey=  request.POST['keyword'].strip() or None)

        
        elif  request.POST['page_id_val'] == 'C':

            return redirect('sub_user_closed',frmdate = request.POST['fromDateInput'],todate=request.POST['toDateInput'], searchkey=  request.POST['keyword'].strip() or None)



@never_cache
@login_required(login_url="/cadmin/admin_login/")
def userPendingsDashboard(request,frmdate=None,todate=None,searchkey = None):

    cur_date = datetime.now()

    prev_date = cur_date - timedelta(days=30)
    
    tickets = None


    if(searchkey is None ):
        tickets = Tickets.objects.filter(Q(issued_on__range=(prev_date, cur_date ))).order_by('-updated_on')
        frmdate = prev_date.strftime('%Y-%m-%d')
        todate = cur_date.strftime('%Y-%m-%d')
        
    else:
    
        tickets = searchfilter(request.user,frmdate,todate,searchkey)

    inbox = tickets.filter((Q(status = 'TH') | Q(status = 'PA')) & Q( maker_id = request.user.id)).count # inbox  count and ticket
    forwarded = tickets.exclude(Q(status='TH') | Q(status='PA') | Q(status='TC')).filter(maker_id=request.user.id).order_by('-ticket_no').annotate(count=Count('ticket_no')) # count and tickets for forwarded message
    closed = tickets.filter(Q(status = 'TC') & Q(maker_id = request.user.id)).count() # closed tickets count
    print(frmdate)
    return render(request,'User/sUserDashboard.html',{'inbox':inbox,'forwarded':forwarded,'closed':closed,'to_date':todate,'prev_date':frmdate,'keyword':searchkey})


