from django.shortcuts import render,get_object_or_404
from django.shortcuts import render,redirect,HttpResponse
from django.views.decorators.cache import never_cache
from django.contrib.auth import login,logout,authenticate
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Q,Count,OuterRef,Subquery
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .utils import get_company_is_active_status,searchfilter,inqueueSearchFilter
from .models import *
from cAdmin.models import *
from django.core.mail import send_mail 
from .form import *
from tuser.models import uTickets
from datetime import datetime,timedelta
from django.http import JsonResponse
import json
from cAdmin.utils import CpyLog,TcktCde
from django.forms.models import model_to_dict
import logging
from django.contrib import messages
from cAdmin.utils import bell_notification,chat_notification
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
    bell_notification(request)
    cur_date = datetime.now()
    prev_date = cur_date - timedelta(days=30)
    tickets = None
    inqueue = None
    if(searchkey is None or searchkey == 'None' ):
        tickets = Tickets.objects.filter(Q(issued_on__range=(prev_date, cur_date ))).order_by('-updated_on') #filter(Q(issued_on__range=(prev_date, cur_date )))
        inqueue = uTickets.objects.filter(Q(issued_on__range=(prev_date, cur_date )) & Q( status = 'SP')).order_by('-updated_on').count()
        frmdate = prev_date.strftime('%Y-%m-%d')
        todate = cur_date.strftime('%Y-%m-%d')
        chat_notification(request,tickets)
        print('testt' , inqueue)
        
    else:
        tickets = searchfilter(request.user,frmdate,todate,searchkey)
        chat_notification(request,tickets)
        inqueue = inqueueSearchFilter(request.user,frmdate,todate).count()
    
    for ticket in tickets:
        print(ticket.ticket_no,'|',ticket.status)

    # inqueue = uTickets.objects.filter(Q(issued_on__date__range=(frmdate, todate)) & Q( status = 'SP')).order_by('-updated_on').count()

    inbox = tickets.filter((Q(status = 'TH') | Q(status = 'PA')) & Q( maker_id = request.user.id)).annotate(count = Count('ticket_no')).order_by('-issued_on') # inbox  count and ticket
    forwarded = tickets.exclude(Q(status='TH') | Q(status='RJ ') | Q(status='SP') |Q(status='PA') | Q(status='TC')).filter(maker_id=request.user.id).count()  # count for forwarded message

    closed = tickets.filter(Q(status = 'TC') & Q(maker_id = request.user.id)).count() # closed tickets count

    return render(request,'User/userDashboard.html',{'tickets':inbox,'forwarded':forwarded,'closed':closed,'to_date':todate,'prev_date':frmdate,'keyword':searchkey,'inqueue' : inqueue})


@never_cache
@login_required(login_url="/cadmin/admin_login/")
def userSignout(request):
    logout(request)
    return redirect('admin_login')

import logging

# Use the logger to log messages
logger = logging.getLogger(__name__)
import threading
class EmailThread(threading.Thread):
    def __init__(self, subject, message, recipient_list):
        self.subject = subject
        self.message = message
        self.recipient_list = recipient_list
        threading.Thread.__init__(self)

    def run(self):
        send_mail(self.subject, self.message, "info@tweedle.co.in", self.recipient_list, fail_silently=False)

@never_cache
@login_required(login_url="/cadmin/admin_login/")
def raiseTicket(request):
    ticketform = TicketForm(company = request.user.company) #company = request.user.company
    if request.method == 'POST':
        ticketform = TicketForm(request.POST, request.FILES, company=request.user.company)
        logger.debug('is valid worked')
        if ticketform.is_valid():
            ticketform_instance = ticketform.save(commit=False)
            ticketform_instance.ticket_no =  TcktCde(request)
            # client = get_object_or_404(CustomUser, id=request.user.id)
            ticketform_instance.client = request.user.company.companyName
            ticketform_instance.maker = request.user
            ticketform_instance.updated_by = request.user
            ticketform_instance.issued_on = datetime.now()
            ticketform_instance.updated_on = datetime.now()
            ticketform_instance.status = 'TP'
            ticketform_instance.save()
            CpyLog(ticketform_instance)
            EmailThread("Subject here", "jtest", ["jinoyks.mefs@gmail.com"]).start()
            # send_mail(    "Subject here",    "jtest",  "info@tweedle.co.in",    ["jinoyks.mefs@gmail.com"],    fail_silently=False,)
            from django.contrib import messages
            messages.success(request, 'Ticket registered with ticket number : ' + str(ticketform_instance.ticket_no))
            return redirect('user_home') 
    
    return render(request, 'User/userRaiseTicket.html', {'form': ticketform})


# @never_cache
# @login_required(login_url="/cadmin/admin_login/")
# def userPendingsDashboard(request,frmdate=None,todate=None,searchkey = None):

#     cur_date = datetime.now()

#     prev_date = cur_date - timedelta(days=30)
    
#     tickets = None


#     if(searchkey is None ):
#         tickets = Tickets.objects.filter(Q(issued_on__range=(prev_date, cur_date ))).order_by('-updated_on')
        
#         frmdate = prev_date.strftime('%Y-%m-%d')
#         todate = cur_date.strftime('%Y-%m-%d')
        
#     else:
    
#         tickets = searchfilter(request.user,frmdate,todate,searchkey)
#         inqueue = inqueueSearchFilter(request.user,frmdate,todate).count()


#     inbox = tickets.filter((Q(status = 'TH') | Q(status = 'PA')) & Q( maker_id = request.user.id)).count # inbox  count and ticket
#     forwarded = tickets.exclude(Q(status='TH') | Q(status='SP') |Q(status='RJ') | Q(status='PA') | Q(status='TC')).filter(maker_id=request.user.id).order_by('-ticket_no').annotate(count=Count('ticket_no')) # count and tickets for forwarded message
#     closed = tickets.filter(Q(status = 'TC') & Q(maker_id = request.user.id)).count() # closed tickets count
#     print(frmdate)
#     return render(request,'User/userDashboard.html',{'inbox':inbox,'forwarded':forwarded,'closed':closed,'to_date':todate,'prev_date':frmdate,'keyword':searchkey})

@never_cache
@login_required(login_url="/cadmin/admin_login/") #user forwarded
def userInProgress(request,frmdate=None,todate=None,searchkey = None):

    cur_date = datetime.now()


    prev_date = cur_date - timedelta(days=30)
    
    tickets = None


    if(searchkey is None or searchkey == 'None'):
        # tickets = Tickets.objects.filter(Q(issued_on__range=(prev_date, cur_date ))).order_by('-updated_on')
        tickets =  (Tickets.objects.filter(Q(issued_on__date__range=(frmdate, todate))).annotate(maker_ids=Subquery(uTickets.objects.filter(ticket_no=OuterRef('old_ticket')).values('maker_id__username')[:1])).order_by('-updated_on'))
        inqueue = uTickets.objects.filter(Q(issued_on__date__range=(frmdate, todate)) & Q( status = 'SP')).order_by('-updated_on').count()
        frmdate = prev_date.strftime('%Y-%m-%d')
        todate = cur_date.strftime('%Y-%m-%d')
        
    else:
    
        tickets = searchfilter(request.user,frmdate,todate,searchkey)
        inqueue = inqueueSearchFilter(request.user,frmdate,todate).count()


    inbox = tickets.filter((Q(status = 'TH') | Q(status = 'PA')) & Q( maker_id = request.user.id)).count() # inbox  count and ticket

    forwarded = tickets.exclude(Q(status='TH') | Q(status='SP') |Q(status='RJ') | Q(status='PA') | Q(status='TC')).filter(maker_id=request.user.id).order_by('-ticket_no').annotate(count=Count('ticket_no'))  # count and tickets for forwarded message
    
    closed = tickets.filter(Q(status = 'TC') & Q(maker_id = request.user.id)).count() # closed tickets count
    
    return render(request,'User/userForwarded.html',{'inbox':inbox,'tickets':forwarded,'closed':closed,'to_date':todate,'prev_date':frmdate,'keyword':searchkey, 'inqueue':inqueue})



@never_cache
@login_required(login_url="/cadmin/admin_login/")
def userClosed(request,frmdate=None,todate=None,searchkey = None):

    cur_date = datetime.now()
    prev_date = cur_date - timedelta(days=30)  
    tickets = None
    if(searchkey is None or searchkey == 'None' ):
        tickets = Tickets.objects.filter(Q(issued_on__range=(prev_date, cur_date ))).order_by('-updated_on')
        inqueue = uTickets.objects.filter(Q(issued_on__date__range=(frmdate, todate)) & Q( status = 'SP')).order_by('-updated_on').count()
        frmdate = prev_date.strftime('%Y-%m-%d')
        todate = cur_date.strftime('%Y-%m-%d')
        
    else:

        tickets = searchfilter(request.user,frmdate,todate,searchkey)
        inqueue = inqueueSearchFilter(request.user,frmdate,todate).count()


    # inqueue = tickets.filter(Q( status = 'SP') ).count()

    # inqueue = uTickets.objects.filter(Q(issued_on__date__range=(frmdate, todate)) & Q( status = 'SP')).order_by('-updated_on').count()
    inbox = tickets.filter((Q(status = 'TH') | Q(status = 'PA')) & Q( maker_id = request.user.id)).count() # inbox  count and ticket
    forwarded = tickets.exclude(Q(status='SP') |Q(status='RJ') |Q(status='TH') | Q(status='PA') | Q(status='TC')).filter(maker_id=request.user.id).count()  # count and tickets for forwarded message
    
    closed = tickets.filter(Q(status = 'TC') & Q(maker_id = request.user.id)).annotate(count=Count('ticket_no')) # closed tickets count

    return render(request,'User/userClosed.html',{'inbox':inbox,'forwarded':forwarded,'tickets':closed,'to_date':todate,'prev_date':frmdate,'keyword':searchkey, 'inqueue':inqueue})
    

@never_cache
@login_required(login_url="/cadmin/admin_login/")
def subQueryDashboard(request,frmdate=None,todate=None,searchkey = None):
    cur_date = datetime.now()

    prev_date = cur_date - timedelta(days=30)
    
    tickets = None
    inqueue = None

    if(searchkey is None or searchkey == 'None'):
        tickets = Tickets.objects.filter(Q(issued_on__range=(prev_date, cur_date ))).order_by('-updated_on')
        inqueue = uTickets.objects.filter(Q(issued_on__date__range=(frmdate, todate)) & Q( status = 'SP'))

        frmdate = prev_date.strftime('%Y-%m-%d')
        todate = cur_date.strftime('%Y-%m-%d')
        
    else:
        inqueue = inqueueSearchFilter(request.user,frmdate,todate)
        tickets = searchfilter(request.user,frmdate,todate,searchkey,db = True)

    inbox = tickets.filter((Q(status = 'TH') | Q(status = 'PA')) & Q( maker_id = request.user.id)).count() # inbox  count and ticket
    forwarded = tickets.exclude(Q(status='SP') |Q(status='RJ') |Q(status='TH') | Q(status='PA') | Q(status='TC')).filter(maker_id=request.user.id).count()  # count and tickets for forwarded message
    closed = tickets.filter(Q(status = 'TC') & Q(maker_id = request.user.id)).count()
  
    return render(request,'User/userInQueue.html',{'inbox':inbox,'forwarded':forwarded,'tickets':inqueue.annotate(count=Count('ticket_no')),'to_date':todate,'prev_date':frmdate,'keyword':searchkey,'closed':closed})






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
       
        messages.success(request, 'Deleted!')
        return redirect('user_home')
    except:
        
        messages.success(request, 'Deleted!')
        return redirect('user_home')

@never_cache
@login_required(login_url="/cadmin/admin_login/")
def liveFwd(request,ticket_id):
    ticket =  Tickets.objects.get(ticket_no = ticket_id )
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
    ticket_id = request.POST['updtid'] 
    print(request.POST)

    if 'Accept-status' in request.POST :
        print(request.user)
        ticket_no =  TcktCde(request)
        ticket = uTickets.objects.get(ticket_no = ticket_id)
        client = get_object_or_404(CustomUser, id=request.user.id)
        tckt_values = Tickets.objects.create(
            ticket_no =  ticket_no,
            client = client.company.companyName,
            maker = client,
            updated_by = request.user,
            updated_on = datetime.now(),
            status = 'TP',
            desc = ticket.desc,
            file = ticket.file,
            issued_on = datetime.now(),
            subject = ticket.subject,
            priority = ticket.priority,
            category = ticket.category,
            old_ticket = ticket.ticket_no,
            approved_on = datetime.now()
            
        )

        # ticket.old_ticket = ticket_no
        ticket.approved_on = datetime.now()
        ticket.status = 'AC'
        ticket.save()
        CpyLog(tckt_values)
        
        messages.success(request, 'Ticket registered with ticket number : ' + str(ticket_no))  
        return redirect('user_home')
    
    if 'reject' in request.POST :
        print(request.user)
        # ticket_no =  TcktCde(request)
        ticket = uTickets.objects.get(ticket_no = ticket_id)
        ticket.status = 'RJ'
        ticket.closed_by = request.user.username
        ticket.closed_on = datetime.now()
        ticket.remarks = request.POST['remarks']
        ticket.save()
        # client = get_object_or_404(CustomUser, id=request.user.id)
        # tckt_values = uTickets.objects.create(
        #     ticket_no =  ticket_no,
        #     client = client.company.companyName,
        #     maker = client,
        #     updated_by = request.user,
        #     updated_on = datetime.now(),
        #     status = 'TC',
        #     desc = ticket.desc,
        #     file = ticket.file,
        #     subject = ticket.subject,
        #     priority = ticket.priority,
        #     category = ticket.category,
        # )
        # CpyLog(tckt_values)
        # tckt_values.status = 'TC'
        # tckt_values.updated_by = request.user
        # tckt_values.updated_on = datetime.now()
        # tckt_values.closed_by =  request.user.username
        # tckt_values.closed_on =  datetime.now()
        # tckt_values.save()
        # ticket.status = 'RJ'
        # ticket.closed_on = tckt_values.closed_on
        # ticket.closed_by = tckt_values.closed_by
        # ticket.save()


        
        messages.success(request, str(ticket.ticket_no) + ' Ticket rejected ' )  
        return redirect('user_home')
    
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
    print(request.POST)

    if request.method == 'POST':
        if  request.POST['page_id_val'] == 'P' :

                return redirect('user_home',frmdate = request.POST['fromDateInput'],todate=request.POST['toDateInput'], searchkey =  request.POST['keyword'].strip() or None)

        elif  request.POST['page_id_val'] == 'F':

            return redirect('user_inprogress',frmdate = request.POST['fromDateInput'],todate=request.POST['toDateInput'], searchkey=  request.POST['keyword'].strip() or None)

        
        elif  request.POST['page_id_val'] == 'C':

            return redirect('user_closed',frmdate = request.POST['fromDateInput'],todate=request.POST['toDateInput'], searchkey=  request.POST['keyword'].strip() or None)
        
        elif  request.POST['page_id_val'] == 'IQ':

            return redirect('user_inqueue',frmdate = request.POST['fromDateInput'],todate=request.POST['toDateInput'], searchkey=  request.POST['keyword'].strip() or None)
        


@never_cache
@login_required(login_url="/cadmin/admin_login/")
def subUserManagement(request,cmpId=None):
    UsersList=User.objects.filter(company = request.user.company.companyId , role = 'EU')
    print(UsersList)
    context={'Users':UsersList,}
    return render(request,'User/subUserManagement.html',context)

@never_cache
@login_required(login_url="/cadmin/admin_login/")
def subUserEdit(request,usr_id = None):    
    usr_data = CustomUser.objects.get(id = usr_id)
    form = editUsrForm(instance=usr_data)
    if request.method == 'POST':
        form = editUsrForm(request.POST, instance=usr_data)
        if form.is_valid():
            if form.has_changed():
                usr_data = form.save()
                messages.success(request, 'Saved!')
                # return render(request, 'User/subUserManagement.html',)
                return redirect('sub_user_management')

    return render(request, 'User/subUserEdit.html', {'form': form})

@never_cache
@login_required(login_url="/cAdmin/")
def addSubUser(request,companyId=None):
    company_instance = get_object_or_404(Company, companyId = request.user.company.companyId )
    UserForm = subUserAdd() 
    # UserForm.fields['department'].queryset = Department.objects.filter(companyId_id=companyId)  
    if request.method == 'POST':
        UserForm=subUserAdd(request.POST)
        if UserForm.is_valid():
            password = UserForm.cleaned_data.get('password')
            UserForm.instance.password = make_password(password)
            UserForm.instance.company = company_instance
            UserForm.instance.role = 'EU'
            UserForm.save()
            # UsersList=User.objects.filter(company_id=companyId)
            # context={'Users':UsersList,'cmpnyId':companyId,}
            return redirect('sub_user_management')

    print(UserForm.errors)
    context={'form':UserForm }
    return render(request,'User/subUserAdd.html',context)

@never_cache
@login_required(login_url="/cAdmin/")
def rejectedTickets(request):
    utickets = uTickets.objects.filter(status = 'RJ')
    print(utickets)
    return render(request , 'User/rejectedTickets.html', {'utickets' : utickets})

@never_cache
@login_required(login_url="/cadmin/admin_login/")
def update_is_active(request, item_id):
    if request.method == "POST" and request.headers.get("Content-Type") == "application/json":
        print(item_id)
        try:
            item = CustomUser.objects.get(id=item_id)
            if item.is_active == True:
                item.is_active = False
            else:
                item.is_active = True
            item.save()

            return JsonResponse({"success": True})
        except item_id.DoesNotExist:
            return JsonResponse({"success": False, "error": "Item not found."})
    else:
        return JsonResponse({"success": False, "error": "Invalid  ."})