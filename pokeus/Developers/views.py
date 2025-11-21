from django.shortcuts import render,get_object_or_404
from django.shortcuts import render,redirect,HttpResponse
from django.views.decorators.cache import never_cache
from django.contrib.auth import login,logout,authenticate
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Q,Count
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.utils.html import format_html
from cAdmin.models import *
from .form import *
from cAdmin.utils import *
from django.views.decorators.cache import cache_control
from datetime import datetime,timedelta
from django.http import JsonResponse,HttpResponseNotAllowed
import json
from django.contrib import messages
# aswin
User = get_user_model()

def devLogin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username,password=password)
        print(user)
        if user is not None and user.is_active and user.role == 'D' :
            login(request,user)
            return redirect('dev_home')
        elif user is not None and user.is_active and user.role == 'T':
            login(request,user)
            return redirect('tester_home')

        else:
            pass
            #return redirect('admin_login')

    return render(request,'developers/developerindex.html',{})


@never_cache
@login_required(login_url="/cadmin/admin_login/")
def dev_home(request,cmpnyId=None,frmdate=None,todate=None,searchkey = None):

    cur_date = datetime.now()

    prev_date = cur_date - timedelta(days=30)
    
    tickets = None

    filter_cname = Company.objects.exclude(companyId = request.user.company_id)

    if(cmpnyId is None ):
        tickets = Tickets.objects.filter(Q(issued_on__range=(prev_date, cur_date ))).order_by('-updated_on')
        frmdate = prev_date.strftime('%Y-%m-%d')
        todate = cur_date.strftime('%Y-%m-%d')
        cmpnyId = "*"
    else:
        if searchkey == 'None':
            searchkey = None
        tickets = searchfilter(cmpnyId,frmdate,todate,searchkey)




    inbox = tickets.filter((Q(status='TA') | Q(status ='RL') | Q(status ='CA')| Q(status = 'BP')) & Q(dev_id = request.user.username )).annotate(count=Count('ticket_no'))
    print(tickets.count)
    # count = Tickets.objects.filter(status='TP').count()
    forwarded = tickets.filter((Q(status = 'DH') | Q(status = 'TH') | Q(status = 'EP') | Q(status = 'EA') | Q(status = 'PP') | Q(status = 'PA') |Q(status = 'RC') | Q(status = 'PC') | Q(status = 'TP') | Q(status = 'EH') | Q(status ='CR')) & Q(dev_id = request.user.username )).count() # forwarded
    closed = tickets.filter(Q(status = 'TC') & Q(dev_id = request.user.username )).count() #closed
    in_progress = tickets.filter((Q(status = 'DA') | Q(status = 'RA') | Q(status ='CD')) & Q(dev_id = request.user.username )).count()
    print(tickets)
    return render(request,'developers/developerDashboard.html',{'tickets':inbox,'inprogress':in_progress,'forwarded':forwarded,'closed':closed,'filter_cname':filter_cname,'to_date':todate,'prev_date':frmdate,'keyword':searchkey,'company_id':cmpnyId})

# @never_cache
# @login_required(login_url="/cadmin/admin_login/")
# def dev_home(request):
#     return render(request,'tester/testerDashboard.html',{})

@never_cache
@login_required(login_url="/cadmin/admin_login/")
def devAccept(request,ticketId,date):
    ticket = Tickets.objects.get(ticket_no=ticketId)
    CpyLog(ticket,)
    ticket.status = 'DA'
    print(ticket)
    ticket.expiry = date
    ticket.updated_on = datetime.now()
    ticket.updated_by = request.user
    ticket.save()
    from django.contrib import messages
    messages.success(request,"Ticket accepted,Moved to In progress bar!")
    return redirect('dev_home')


@never_cache
@login_required(login_url="/cadmin/admin_login/")
def dev_signout(request):
    logout(request)
    return redirect('admin_login')


'''
     For inprogress  listing in developer Board
'''
@never_cache
@login_required(login_url="/cadmin/admin_login/")
def devPendingsDashboard(request,cmpnyId=None,frmdate=None,todate=None,searchkey = None):

    cur_date = datetime.now()

    prev_date = cur_date - timedelta(days=30)
    
    tickets = None

    filter_cname = Company.objects.exclude(companyId = request.user.company_id)

    if(cmpnyId is None ):
        tickets = Tickets.objects.filter(Q(issued_on__range=(prev_date, cur_date ))).order_by('-updated_on')
        frmdate = prev_date.strftime('%Y-%m-%d')
        todate = cur_date.strftime('%Y-%m-%d')
        cmpnyId = "*"
    else:
        if searchkey == 'None':
            searchkey = None
        tickets = searchfilter(cmpnyId,frmdate,todate,searchkey)


    inbox = tickets.filter((Q(status='DA') | Q(status='RA') | Q(status='CD')) & Q(dev_id = request.user.username )).annotate(count=Count('ticket_no')) #inprogress ticket count also annotated with this statement
    open_tickets = tickets.filter((Q(status = 'TA') | Q(status = 'RL') | Q(status = 'CA') | Q(status = 'BP')) & Q(dev_id = request.user.username )).count() # open tickets
    forwarded = tickets.filter((Q(status = 'DH') | Q(status = 'TH') | Q(status = 'EP') | Q(status = 'EA') | Q(status = 'PP') | Q(status = 'PA') |Q(status = 'RC') | Q(status = 'PC') | Q(status = 'TP') | Q(status = 'EH')| Q(status = 'CR')) & Q(dev_id = request.user.username )).count() # forwarded
    closed = tickets.filter(Q(status = 'TC') & Q(dev_id = request.user.username )).count() #closed
    testers = CustomUser.objects.filter(role='T')
    print(testers)
    return render(request,'developers/devprogress.html',{'tickets':inbox,'testers':testers,'open':open_tickets,'forwarded':forwarded,'closed':closed,'filter_cname':filter_cname,'to_date':todate,'prev_date':frmdate,'keyword':searchkey,'company_id':cmpnyId})


@never_cache
@login_required(login_url="/cadmin/admin_login/")
def devForwarded(request,cmpnyId=None,frmdate=None,todate=None,searchkey = None):

    cur_date = datetime.now()

    prev_date = cur_date - timedelta(days=30)
    
    tickets = None

    filter_cname = Company.objects.exclude(companyId = request.user.company_id)

    if(cmpnyId is None ):
        tickets = Tickets.objects.filter(Q(issued_on__range=(prev_date, cur_date ))).order_by('-updated_on')
        frmdate = prev_date.strftime('%Y-%m-%d')
        todate = cur_date.strftime('%Y-%m-%d')
        cmpnyId = "*"
    else:
        if searchkey == 'None':
            searchkey = None
        tickets = searchfilter(cmpnyId,frmdate,todate,searchkey)

    open_tickets = tickets.filter((Q(status='TA') | Q(status='RL')| Q(status = 'CA')| Q(status = 'BP')) & Q(dev_id = request.user.username )).count() #inbox
    inprogress = tickets.filter((Q(status = 'DA') | Q(status = 'RA')| Q(status = 'CD')) & Q(dev_id = request.user.username )).count() # open tickets
    tickets_forwarded = tickets.exclude(status__in = ['TA','RL','DA','RA','TC','CA','CD','BP']).filter(dev_id = request.user.username ).annotate(count = Count('ticket_no'))
    closed = tickets.filter(Q(status = 'TC') & Q(dev_id = request.user.username )).count() #closed
    return render(request,'developers/developerForwarded.html',{'tickets':tickets_forwarded,'open':open_tickets,'inprogress':inprogress,'closed':closed,'filter_cname':filter_cname,'to_date':todate,'prev_date':frmdate,'keyword':searchkey,'company_id':cmpnyId})


@never_cache
@login_required(login_url="/cadmin/admin_login/")
def devClosed(request,cmpnyId=None,frmdate=None,todate=None,searchkey = None):
    cur_date = datetime.now()

    prev_date = cur_date - timedelta(days=30)
    
    tickets = None

    filter_cname = Company.objects.exclude(companyId = request.user.company_id)

    if(cmpnyId is None ):
        tickets = Tickets.objects.filter(Q(issued_on__range=(prev_date, cur_date ))).order_by('-updated_on')
        frmdate = prev_date.strftime('%Y-%m-%d')
        todate = cur_date.strftime('%Y-%m-%d')
        cmpnyId = "*"
    else:
        if searchkey == 'None':
            searchkey = None
        tickets = searchfilter(cmpnyId,frmdate,todate,searchkey)


    open_tickets = tickets.filter((Q(status='TA') | Q(status='RL')| Q(status = 'CA')| Q(status = 'BP')) & Q(dev_id = request.user.username )).count() #inbox
    inprogress = tickets.filter((Q(status = 'DA') | Q(status = 'RA')| Q(status = 'CD')) & Q(dev_id = request.user.username )).count() # open tickets
    forwarded = tickets.exclude(status__in = ['TA','RL','DA','RA','TC','CA','CD','BP']).filter(dev_id = request.user.username ).count()
    closed = tickets.filter(Q(status = 'TC') & Q(dev_id = request.user.username )).annotate(count = Count('ticket_no')) #closed
    return render(request,'developers/developerClosed.html',{'tickets':closed,'inbox':open_tickets,'inprogress':inprogress,'forwarded':forwarded,'filter_cname':filter_cname,'to_date':todate,'prev_date':frmdate,'keyword':searchkey,'company_id':cmpnyId})

@never_cache
@login_required(login_url="/cadmin/admin_login/") # deprecated
def devClarific(request,ticketId):
    print('dev_clarification called')
    tickets = Tickets.objects.filter((Q(status='DA') | Q(status='RA')) & Q(dev_id = request.user.username )).annotate(count=Count('ticket_no')) #inprogress ticket count also annotated with this statement
    open_tickets = Tickets.objects.filter((Q(status = 'TA') | Q(status = 'RL')) & Q(dev_id = request.user.username )).count() # open tickets
    forwarded = Tickets.objects.filter((Q(status = 'DH') | Q(status = 'TH') | Q(status = 'EP') | Q(status = 'EA') | Q(status = 'PP') | Q(status = 'PA') |Q(status = 'RC') | Q(status = 'PC') | Q(status = 'TD') | Q(status = 'EH')) & Q(dev_id = request.user.username )).count() # forwarded
    closed = Tickets.objects.filter(Q(status = 'TC') & Q(dev_id = request.user.username )).count() #closed
    ticket_no = Ticket.objects.get(ticket_no = ticketId)
    CpyLog(ticketId)
    ticket_no.status = 'DH'
    ticket_no.desc = ''
    ticket_no.updated_by = request.user.username
    return render(request,'developers/devprogress.html',{'tickets':tickets,'open':open_tickets,'forwarded':forwarded,'closed':closed})


@never_cache
@login_required(login_url="/cadmin/admin_login/")
def assignTester(request,testerid,ticketId):
    ticket = Tickets.objects.get(ticket_no = ticketId)
    tickets = Tickets.objects.filter((Q(status='DA') | Q(status='RA')) & Q(dev_id = request.user.username )).annotate(count=Count('ticket_no')) #inprogress ticket count also annotated with this statement
    open_tickets = Tickets.objects.filter((Q(status = 'TA') | Q(status = 'RL')) & Q(dev_id = request.user.username )).count() # open tickets
    forwarded = Tickets.objects.filter((Q(status = 'DH') | Q(status = 'TH') | Q(status = 'EP') | Q(status = 'EA') | Q(status = 'PP') | Q(status = 'PA') |Q(status = 'RC') | Q(status = 'PC') | Q(status = 'TD') | Q(status = 'EH')) & Q(dev_id = request.user.username )).count() # forwarded
    closed = Tickets.objects.filter(Q(status = 'TC') & Q(dev_id = request.user.username )).count() #closed
    CpyLog(ticket)
    ticket.updated_by = request.user
    ticket.tester_id = testerid
    ticket.tester_assigned_date = datetime.now()
    ticket.status = 'EH'
    ticket.save()
    messages.success(request,'Asisgned TO :' + testerid)
    return redirect('dev_pendings') 

@never_cache
@login_required(login_url="/cadmin/admin_login/")
def devOperations(request,ticket_id = None,status = None,tester_id= None,exp = None,remarks = None):
    
    if request.method == 'POST':
        print(request.POST)
        ticket_id = request.POST['updtid']
        ticket = Tickets.objects.get(ticket_no=ticket_id)
        if ticket.status == 'TA': # New ticket acceptance
            ticket.status = 'DA'
            if  request.POST['exp'] != '' : #or ticket.expiry != None generates an error because the first condion faile but the expiry variable is  '' so it satisfy !=none generates an error
                ticket.expiry = request.POST['exp']
            if request.POST['remarks'] != '':
                ticket.remarks = request.POST['remarks']
            if request.POST['tgt_days'] != '':
                ticket.tgt_days = request.POST['tgt_days']
            if 'rmk_files' in request.FILES:
                ticket.rmrk_files = request.FILES['rmk_files']
            ticket.updated_by = request.user
            ticket.save()
            CpyLog(ticket,request.POST['remarks'],request.FILES.get('rmk_files', None))
            print('c')
            messages.success(request,'Ticket accepted , Moved to In progress bar!')




        # if status == 'TA' :
        #     CpyLog(ticket)
        #     ticket.status = 'DA'
        #     if exp != " ":
        #         ticket.expiry = exp
        #     if remarks != ' ':
        #         ticket.remarks = remarks 
        #     ticket.updated_by = request.user
        #     ticket.save()
        #     messages.success(request,"Ticket accepted,Moved to In progress bar!")

        



        elif ticket.status == 'BP' and ticket.expiry != None: # Developer accepted tester qry and put this to Hold 
            # CpyLog(ticket)
            ticket.status = 'DA'
            ticket.updated_by = request.user
            if request.POST['remarks'] != '':
                ticket.remarks = request.POST['remarks']
            if 'rmk_files' in request.FILES:
                ticket.rmrk_files = request.FILES['rmk_files']
            ticket.save()
            CpyLog(ticket,request.POST['remarks'],request.FILES.get('rmk_files', None))
            messages.success(request,"Ticket accepted,Moved to In progress bar!")


        elif ticket.status == 'DA' and 'chatflag' not in request.POST and 'tqry' not in request.POST: # when developer assign it to tester
            # CpyLog(ticket)
            ticket.updated_by = request.user
            print(request.POST)
            if 'testers' in request.POST:
                ticket.tester_id = request.POST['testers']
            if 'remarks' in request.POST:
                if request.POST['remarks'] != '' :
                    ticket.remarks = request.POST['remarks']
            if 'rmk_files' in request.FILES:
                ticket.rmrk_files = request.FILES['rmk_files']
            # ticket.tester_assigned_date = datetime.now()
            ticket.status = 'EH' # 'EP' 22/11/23
            print(request.POST)
            ticket.save()
            CpyLog(ticket,request.POST['remarks'],request.FILES.get('rmk_files', None))
            messages.success(request,'Asisgned to :' + ticket.tester_id)

        elif ticket.status == 'RL':
            # CpyLog(ticket)
            ticket.status = 'RA'
            if 'remarks' in request.POST:
                if request.POST['remarks'] != '':
                    ticket.remarks = request.POST['remarks']
            if 'rmk_files' in request.FILES:
                ticket.rmrk_files = request.FILES['rmk_files']
            ticket.updated_by = request.user
            ticket.save()
            CpyLog(ticket,request.POST['remarks'],request.FILES.get('rmk_files', None))
            messages.success(request,"Move to Production request accepted! Moved to In progress.")

        elif ticket.status == 'RA':
            # CpyLog(ticket)
            ticket.status = 'PC'
            if 'remarks' in request.POST:
                if request.POST['remarks'] != '':
                    ticket.remarks = request.POST['remarks']
            if 'rmk_files' in request.FILES:
                ticket.rmrk_files = request.FILES['rmk_files']
            ticket.updated_by = request.user
            ticket.save()
            CpyLog(ticket,request.POST.get('remarks'))
            messages.success(request,"Program Copied to live!")
        
        elif ticket.status == 'CA':
            # CpyLog(ticket)
            ticket.status = 'CD'
            if 'remarks' in request.POST:
                if request.POST['remarks'] != '':
                    ticket.remarks = request.POST['remarks']
            if 'rmk_files' in request.FILES:
                ticket.rmrk_files = request.FILES['rmk_files']
            ticket.updated_by = request.user
            ticket.save()
            CpyLog(ticket,request.POST['remarks'],request.FILES.get('rmk_files', None))
            messages.success(request,"Request Accepted!")

        elif 'chatflag' in request.POST: 
            if request.POST['chatflag'] == 'C':
                # CpyLog(ticket)
                ticket.status = 'DH' # Now all queries go through admin , otherwise change status to TH
            print(remarks,'reamrk test')
            if 'remarks' in request.POST:
                if request.POST['remarks'] != '':
                    ticket.remarks = request.POST['remarks']
            if 'rmk_files' in request.FILES:
                ticket.rmrk_files = request.FILES['rmk_files']
            ticket.updated_by = request.user
            ticket.save()
            CpyLog(ticket,request.POST['remarks'],request.FILES.get('rmk_files', None))
            messages.success(request,"Request has sent to admin [ON HOLD].")

        elif 'tqry' in request.POST:
            print('it;s workedddd')
            if request.POST['tqry'] == 'TQ': # Developer accepted tester qry and put this to Hold , comes from devprogress.html page
                # CpyLog(ticket)
                ticket.status = 'EP'
                ticket.updated_by = request.user
                if 'remarks' in request.POST:
                    if request.POST['remarks'] != '':
                        ticket.remarks = request.POST['remarks']
                if 'rmk_files' in request.FILES:
                    ticket.rmrk_files = request.FILES['rmk_files']
                ticket.save()
                CpyLog(ticket,request.POST.get('remarks', None))
                messages.success(request,"Query/Bug report closed!")
        
    return redirect('dev_home')





"""

    ===========================================================================================================
                                         Tester Code

                           
    ===========================================================================================================

"""


@never_cache
@login_required(login_url="/cadmin/admin_login/")
def tester_home(request,cmpnyId=None,frmdate=None,todate=None,searchkey = None):
    cur_date = datetime.now()

    prev_date = cur_date - timedelta(days=30)
    
    tickets = None

    filter_cname = Company.objects.exclude(companyId = request.user.company_id)

    if(cmpnyId is None ):
        tickets = Tickets.objects.filter(Q(issued_on__range=(prev_date, cur_date ))).order_by('-updated_on')
        frmdate = prev_date.strftime('%Y-%m-%d')
        todate = cur_date.strftime('%Y-%m-%d')
        cmpnyId = "*"
    else:
        if searchkey == 'None':
            searchkey = None
        tickets = searchfilter(cmpnyId,frmdate,todate,searchkey)

    inbox = tickets.filter(status='EP' , tester_id=request.user.username).annotate(count=Count('ticket_no'))
    forwarded = tickets.exclude(status__in=['EP', 'EA', 'TC','EH']).filter(tester_id=request.user.username).count() # forwarded
    closed = tickets.filter(Q(status = 'TC') & Q(tester_id = request.user.username )).count() #closed
    in_progress = tickets.filter(status = 'EA',tester_id = request.user.username).count() 
    return render(request,'testers/testerDashboard.html',{'tickets':inbox,'inprogress':in_progress,'forwarded':forwarded,'closed':closed,'filter_cname':filter_cname,'to_date':todate,'prev_date':frmdate,'keyword':searchkey,'company_id':cmpnyId})


@never_cache
@login_required(login_url="/cadmin/admin_login/")
def testerPendings(request,cmpnyId=None,frmdate=None,todate=None,searchkey = None):  # Pending means in progress
    cur_date = datetime.now()

    prev_date = cur_date - timedelta(days=30)
    
    tickets = None

    filter_cname = Company.objects.exclude(companyId = request.user.company_id)

    if(cmpnyId is None ):
        tickets = Tickets.objects.filter(Q(issued_on__range=(prev_date, cur_date ))).order_by('-updated_on')
        frmdate = prev_date.strftime('%Y-%m-%d')
        todate = cur_date.strftime('%Y-%m-%d')
        cmpnyId = "*"
    else:
        if searchkey == 'None':
            searchkey = None
        tickets = searchfilter(cmpnyId,frmdate,todate,searchkey)

    in_progress = tickets.filter(status='EA' , tester_id=request.user.username).annotate(count=Count('ticket_no')) # inprogress
    forwarded = tickets.exclude(status__in=['EP', 'EA', 'TC','EH']).filter(tester_id=request.user.username).count() # forwarded
    closed = tickets.filter(Q(status = 'TC') & Q(tester_id = request.user.username )).count() #closed
    open_tickets = tickets.filter(status = 'EP',tester_id = request.user.username).count() 
    return render(request,'testers/testerprogress.html',{'tickets':in_progress,'open':open_tickets,'forwarded':forwarded,'closed':closed,'filter_cname':filter_cname,'to_date':todate,'prev_date':frmdate,'keyword':searchkey,'company_id':cmpnyId})


@never_cache
@login_required(login_url="/cadmin/admin_login/")
def testerForwarded(request,cmpnyId=None,frmdate=None,todate=None,searchkey = None): 
    cur_date = datetime.now()

    prev_date = cur_date - timedelta(days=30)
    
    tickets = None

    filter_cname = Company.objects.exclude(companyId = request.user.company_id)

    if(cmpnyId is None ):
        tickets = Tickets.objects.filter(Q(issued_on__range=(prev_date, cur_date ))).order_by('-updated_on')
        frmdate = prev_date.strftime('%Y-%m-%d')
        todate = cur_date.strftime('%Y-%m-%d')
        cmpnyId = "*"
    else:
        if searchkey == 'None':
            searchkey = None
        tickets = searchfilter(cmpnyId,frmdate,todate,searchkey)

    inprogress = tickets.filter(status='EA' , tester_id=request.user.username).count() # inprogress
    forwarded = tickets.exclude(status__in=['EP', 'EA', 'TC','EH']).filter(tester_id=request.user.username).annotate(count=Count('ticket_no')) # forwarded
    closed = tickets.filter(Q(status = 'TC') & Q(tester_id = request.user.username )).count() #closed
    open_tickets = tickets.filter(status = 'EP',tester_id = request.user.username).count() 
    return render(request,'testers/testerForwarded.html',{'tickets':forwarded,'open':open_tickets,'inprogress':inprogress,'closed':closed,'filter_cname':filter_cname,'to_date':todate,'prev_date':frmdate,'keyword':searchkey,'company_id':cmpnyId})


@never_cache
@login_required(login_url="/cadmin/admin_login/")
def testerClosed(request,cmpnyId=None,frmdate=None,todate=None,searchkey = None):  # Pending means in progress
    cur_date = datetime.now()

    prev_date = cur_date - timedelta(days=30)
    
    tickets = None

    filter_cname = Company.objects.exclude(companyId = request.user.company_id)

    if(cmpnyId is None ):
        tickets = Tickets.objects.filter(Q(issued_on__range=(prev_date, cur_date ))).order_by('-updated_on')
        frmdate = prev_date.strftime('%Y-%m-%d')
        todate = cur_date.strftime('%Y-%m-%d')
        cmpnyId = "*"
    else:
        if searchkey == 'None':
            searchkey = None
        tickets = searchfilter(cmpnyId,frmdate,todate,searchkey)

    inprogress = tickets.filter(status='EA' , tester_id=request.user.username).count() # inprogress
    forwarded = tickets.exclude(status__in=['EP', 'EA', 'TC','EH']).filter(tester_id=request.user.username).count()
    closed = tickets.filter(Q(status = 'TC') & Q(tester_id = request.user.username )).annotate(count=Count('ticket_no'))
    open_tickets = tickets.filter(status = 'EP',tester_id = request.user.username).count() 
    return render(request,'testers/testerClosed.html',{'tickets':closed,'inbox':open_tickets,'forwarded':forwarded,'inprogress':inprogress,'filter_cname':filter_cname,'to_date':todate,'prev_date':frmdate,'keyword':searchkey,'company_id':cmpnyId})

@never_cache
@login_required(login_url="/cadmin/admin_login/")
def testerAccept(request):
    if request.method == 'POST':
        print(request.POST)
        ticket= Tickets.objects.get(ticket_no=request.POST['updtid'])
        if 'remarks' in request.POST:
            if request.POST['remarks'] != '':
                ticket.remarks = request.POST['remarks']
        if 'exp' in request.POST:
            ticket.expiry = request.POST['exp']
        if 'tgt_days' in request.POST:
            ticket.tgt_days = request.POST['tgt_days']
        if 'rmk_files' in request.POST:
                ticket.remarkfile = request.POST['rmk_files']
        ticket.status = 'EA'
        ticket.updated_by  = request.user
        # CpyLog(ticket)
        ticket.save()
        print(request.POST['remarks'],'jinoy remark testting')
        CpyLog(ticket,request.POST['remarks'],request.FILES.get('rmk_files', None))
        messages.success(request,'Ticket Accepted,Moved to Progress bar !')
        return redirect('tester_home')


@never_cache
@login_required(login_url="/cadmin/admin_login/")
def testerPush(request):
    
    if request.method == 'POST':
        
        ticket = Tickets.objects.get(ticket_no = request.POST['tcktno'] , tester_id = request.user.username)
        # CpyLog(ticket)
        ticket.status = 'PP'
        ticket.updated_by  = request.user
        ticket.save()
        CpyLog(ticket)
        messages.success(request,'Ticket forwarded to admin!')
        return redirect('tester_home')

@never_cache
@login_required(login_url="/cadmin/admin_login/")
def testerQry(request,):
    if request.method == 'POST':
        ticket = Tickets.objects.get(ticket_no = request.POST['qrybtn'] , tester_id = request.user.username)
        # CpyLog(ticket)
        ticket.status = 'BP'
        ticket.updated_by  = request.user
        ticket.save()
        CpyLog(ticket)
        messages.success(request,'Query request sent to developer!')
        return redirect('tester_home') 


@never_cache
@login_required(login_url="/cadmin/admin_login/")
def devSearch(request,):

    if request.method == 'POST':
 
        # if  request.POST['key'] != 't':
        if request.user.role == 'D':

            if  request.POST['page_id_val'] == 'P' :

                return redirect('dev_home',cmpnyId = request.POST['companyDropdown'],frmdate = request.POST['fromDateInput'],todate=request.POST['toDateInput'], searchkey =  request.POST['keyword'].strip() or None)

            elif  request.POST['page_id_val'] == 'I':

                return redirect('dev_pendings',cmpnyId = request.POST['companyDropdown'],frmdate = request.POST['fromDateInput'],todate=request.POST['toDateInput'], searchkey=  request.POST['keyword'].strip() or None)

            elif  request.POST['page_id_val'] == 'F':

                return redirect('dev_forwarded',cmpnyId = request.POST['companyDropdown'],frmdate = request.POST['fromDateInput'],todate=request.POST['toDateInput'], searchkey=  request.POST['keyword'].strip() or None)

            elif  request.POST['page_id_val'] == 'C':

                return redirect('dev_closed',cmpnyId = request.POST['companyDropdown'],frmdate = request.POST['fromDateInput'],todate=request.POST['toDateInput'], searchkey=  request.POST['keyword'].strip() or None)

        elif request.user.role == 'T':

            if  request.POST['page_id_val'] == 'P' :

                return redirect('tester_home',cmpnyId = request.POST['companyDropdown'],frmdate = request.POST['fromDateInput'],todate=request.POST['toDateInput'], searchkey =  request.POST['keyword'].strip() or None)

            elif  request.POST['page_id_val'] == 'I':

                return redirect('tester_pendings',cmpnyId = request.POST['companyDropdown'],frmdate = request.POST['fromDateInput'],todate=request.POST['toDateInput'], searchkey=  request.POST['keyword'].strip() or None)

            elif  request.POST['page_id_val'] == 'F':

                return redirect('tester_forwarded',cmpnyId = request.POST['companyDropdown'],frmdate = request.POST['fromDateInput'],todate=request.POST['toDateInput'], searchkey=  request.POST['keyword'].strip() or None)

            elif  request.POST['page_id_val'] == 'C':

                return redirect('tester_closed',cmpnyId = request.POST['companyDropdown'],frmdate = request.POST['fromDateInput'],todate=request.POST['toDateInput'], searchkey=  request.POST['keyword'].strip() or None)











# def devSearch(request):
#     tickets = Tickets.objects.none()
#     filter_cname = Company.objects.exclude(companyId = request.user.company_id)

#     srchkey = request.POST['keyword'].strip()
#     fromdate = request.POST['fromDateInput']
#     todate = request.POST['toDateInput']
#     page_id  = request.POST['page_id']
#     print(srchkey,fromdate,todate)
    
#     if srchkey != '' and fromdate != '' and todate != '' :
#         tickets = Tickets.objects.filter(ticket_no__icontains= srchkey)
#     elif srchkey == '' and fromdate != '' and todate != '':
#         tickets = Tickets.objects.filter(issued_on__date__range=(fromdate,todate))
#         print(tickets)
#     elif srchkey != '' and fromdate == '' and todate == '':
#         tickets = Tickets.objects.filter(ticket_no__icontains = srchkey)

#     if tickets.exists():

#         if request.user.role == 'D':
#             if page_id == 'P':
#                 inbox = tickets.filter((Q(status='TA') | Q(status ='RL') | Q(status ='CA')| Q(status = 'BP')) & Q(dev_id = request.user.username )).annotate(count=Count('ticket_no'))
#                 forwarded = tickets.filter((Q(status = 'DH') | Q(status = 'TH') | Q(status = 'EP') | Q(status = 'EA') | Q(status = 'PP') | Q(status = 'PA') |Q(status = 'RC') | Q(status = 'PC') | Q(status = 'TP') | Q(status = 'EH') | Q(status ='CR')) & Q(dev_id = request.user.username )).count() # forwarded
#                 closed = tickets.filter(Q(status = 'TC') & Q(dev_id = request.user.username )).count() #closed
#                 in_progress = tickets.filter((Q(status = 'DA') | Q(status = 'RA') | Q(status ='CD')) & Q(dev_id = request.user.username )).count()
#                 return render(request,'developers/developerDashboard.html',{'tickets':inbox,'inprogress':in_progress,'forwarded':forwarded,'closed':closed,'filter_cname':filter_cname})

        
#             elif page_id == 'I':
#                 in_progress = tickets.filter((Q(status='DA') | Q(status='RA') | Q(status='CD')) & Q(dev_id = request.user.username )).annotate(count=Count('ticket_no')) #inprogress ticket count also annotated with this statement
#                 open_tickets = tickets.filter((Q(status = 'TA') | Q(status = 'RL') | Q(status = 'CA') | Q(status = 'BP')) & Q(dev_id = request.user.username )).count() # open tickets
#                 forwarded = tickets.filter((Q(status = 'DH') | Q(status = 'TH') | Q(status = 'EP') | Q(status = 'EA') | Q(status = 'PP') | Q(status = 'PA') |Q(status = 'RC') | Q(status = 'PC') | Q(status = 'TP') | Q(status = 'EH')| Q(status = 'CR')) & Q(dev_id = request.user.username )).count() # forwarded
#                 closed = tickets.filter(Q(status = 'TC') & Q(dev_id = request.user.username )).count() #closed
#                 testers = CustomUser.objects.filter(role='T')
#                 return render(request,'developers/devProgress.html',{'tickets':in_progress,'testers':testers,'open':open_tickets,'forwarded':forwarded,'closed':closed,'filter_cname':filter_cname})

#             elif page_id == 'F':
#                 open_tickets = tickets.filter((Q(status='TA') | Q(status='RL')| Q(status = 'CA')| Q(status = 'BP')) & Q(dev_id = request.user.username )).count() #inbox
#                 inprogress = tickets.filter((Q(status = 'DA') | Q(status = 'RA')| Q(status = 'CD')) & Q(dev_id = request.user.username )).count() # open tickets
#                 tickets_forwarded = tickets.exclude(status__in = ['TA','RL','DA','RA','TC','CA','CD','BP']).filter(dev_id = request.user.username ).annotate(count = Count('ticket_no'))
#                 closed = tickets.filter(Q(status = 'TC') & Q(dev_id = request.user.username )).count() #closed
#                 return render(request,'developers/developerForwarded.html',{'tickets':tickets_forwarded,'open':open_tickets,'inprogress':inprogress,'closed':closed,'filter_cname':filter_cname})



#             elif page_id == 'C':
#                 open_tickets = tickets.filter((Q(status='TA') | Q(status='RL')| Q(status = 'CA')| Q(status = 'BP')) & Q(dev_id = request.user.username )).count() #inbox
#                 inprogress = tickets.filter((Q(status = 'DA') | Q(status = 'RA')| Q(status = 'CD')) & Q(dev_id = request.user.username )).count() # open tickets
#                 forwarded = tickets.exclude(status__in = ['TA','RL','DA','RA','TC','CA','CD','BP']).filter(dev_id = request.user.username ).count()
#                 closed = tickets.filter(Q(status = 'TC') & Q(dev_id = request.user.username )).annotate(count = Count('ticket_no')) #closed
#                 return render(request,'developers/developerClosed.html',{'tickets':closed,'inbox':open_tickets,'inprogress':inprogress,'forwarded':forwarded,'filter_cname':filter_cname})

#         elif request.user.role == 'T':
#             if page_id == 'P':

#                 inbox = Tickets.objects.filter(status='EP' , tester_id=request.user.username).annotate(count=Count('ticket_no'))
#                 forwarded = Tickets.objects.exclude(status__in=['EP', 'EA', 'TC','EH']).filter(tester_id=request.user.username).count() # forwarded
#                 closed = Tickets.objects.filter(Q(status = 'TC') & Q(tester_id = request.user.username )).count() #closed
#                 in_progress = Tickets.objects.filter(status = 'EA',tester_id = request.user.username).count() 
#                 return render(request,'testers/testerDashboard.html',{'tickets':inbox,'inprogress':in_progress,'forwarded':forwarded,'closed':closed,'filter_cname':filter_cname})
            
#             elif page_id == 'I':

#                 in_progress = tickets.filter(status='EA' , tester_id=request.user.username).annotate(count=Count('ticket_no')) # inprogress
#                 forwarded = tickets.exclude(status__in=['EP', 'EA', 'TC','EH']).filter(tester_id=request.user.username).count() # forwarded
#                 closed = tickets.filter(Q(status = 'TC') & Q(tester_id = request.user.username )).count() #closed
#                 open_tickets = tickets.filter(status = 'EP',tester_id = request.user.username).count() 
#                 return render(request,'testers/testerprogress.html',{'tickets':in_progress,'open':open_tickets,'forwarded':forwarded,'closed':closed,'filter_cname':filter_cname})

#             elif page_id == 'F':

#                 inprogress = Tickets.filter(status='EA' , tester_id=request.user.username).count() # inprogress
#                 forwarded = Tickets.exclude(status__in=['EP', 'EA', 'TC','EH']).filter(tester_id=request.user.username).annotate(count=Count('ticket_no')) # forwarded
#                 closed = Tickets.filter(Q(status = 'TC') & Q(tester_id = request.user.username )).count() #closed
#                 open_tickets = Tickets.filter(status = 'EP',tester_id = request.user.username).count() 
#                 return render(request,'testers/testerForwarded.html',{'tickets':forwarded,'open':open_tickets,'inprogress':inprogress,'closed':closed,'filter_cname':filter_cname})

#             elif page_id == 'C':

#                 inprogress = Tickets.filter(status='EA' , tester_id=request.user.username).count() # inprogress
#                 forwarded = Tickets.exclude(status__in=['EP', 'EA', 'TC','EH']).filter(tester_id=request.user.username).count()
#                 closed = Tickets.filter(Q(status = 'TC') & Q(tester_id = request.user.username )).annotate(count=Count('ticket_no'))
#                 open_tickets = Tickets.filter(status = 'EP',tester_id = request.user.username).count() 
#                 return render(request,'testers/testerClosed.html',{'tickets':closed,'inbox':open_tickets,'forwarded':forwarded,'inprogress':inprogress,'filter_cname':filter_cname})

#     else:
#         if request.user.role == 'T':
#             if page_id == 'P':
#                 return render(request,'developers/developerDashboard.html',{'tickets':inbox,'inprogress':in_progress,'forwarded':forwarded,'closed':closed,'filter_cname':filter_cname,'flag':1})

#         return render(request,'User/userClosed.html',{'flag':1})
