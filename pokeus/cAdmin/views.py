from django.shortcuts import render,get_object_or_404,render,redirect
from django.views.decorators.cache import never_cache
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.decorators import login_required
from django.db.models import Q,Count,F,Min,Max,OuterRef,Subquery,Case, When, Value, CharField
from django.contrib.auth.hashers import make_password,check_password
from django.contrib.auth import get_user_model
from tuser.models import uTickets
from .models import *
from .form import *
from .utils import CpyLog,searchfilter,chat_notification,bell_notification
from datetime import datetime,timedelta
from django.http import JsonResponse
from django.contrib import messages
from django.core.mail import send_mail 

# Create your views here.
 
User = get_user_model()

import threading
class EmailThread(threading.Thread):
    def __init__(self, subject, message, recipient_list):
        self.subject = subject
        self.message = message
        self.recipient_list = recipient_list
        threading.Thread.__init__(self)

    def run(self):
        print('Email sent')
        send_mail(self.subject, self.message, "info@tweedle.co.in", self.recipient_list, fail_silently=False)

@never_cache
def adminLogin(request):
    message = ''
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username,password=password)
        
        if user is not None and user.is_active and user.role == 'A' :
            login(request,user)
            return redirect('admin_home')
        elif user is not None and user.is_active and user.role == 'U' and user.company.is_active :
            login(request,user)
            return redirect('user_home')
        elif user is not None and user.is_active and user.role == 'D':
            login(request,user)
            return redirect('dev_home')
        elif user is not None and user.is_active and user.role == 'T':
            login(request,user)
            return redirect('tester_home')
        elif user is not None and user.is_active and user.role == 'EU':
            login(request, user)
            return redirect('sub_user_home')
    # context parsing 
        else:
            message = "Username or password doesn't match."
    return render(request,'cAdmin/index.html',{'message':message})


@never_cache
@login_required(login_url="/cadmin/admin_login/")
def home(request,cmpnyId='*',frmdate=None,todate=None,searchkey = None , flag = '0'):
    cur_date = datetime.now()
    bell_not = bell_notification(request)
    prev_date = cur_date - timedelta(days=30)
    cur_date = cur_date.strftime('%Y-%m-%d')
    prev_date = prev_date.strftime('%Y-%m-%d')
    tickets = None
    inbox = None 
    in_progress = None 
    forwarded = None 
    closed = None
    filter_cname = Company.objects.exclude(companyId = request.user.company_id)
    ticket_counts = Tickets.objects.aggregate(
            in_progress=Count('ticket_no', filter=Q(status__in=['TA', 'DA', 'EP', 'EA', 'RA', 'RL', 'CD', 'BP'])),
            forwarded=Count('ticket_no', filter=Q(status__in=['TH', 'PA', 'CA'])),
            closed=Count('ticket_no', filter=Q(status='TC'))
                )
    if flag == '0':
        inbox = Tickets.objects.filter(status__in=['TP', 'DH', 'RC', 'PC', 'PP', 'EH', 'CR']).order_by('ticket_no')
        dates = inbox.aggregate(
            first_issued_date=Min('issued_on'),
            last_issued_date=Max('issued_on')
            )
        chat_notification(request,inbox)
        in_progress = ticket_counts['in_progress'] 
        forwarded = ticket_counts['forwarded'] 
        closed = ticket_counts['closed'] 
        todate = dates['last_issued_date']
        todate = todate.date().strftime('%Y-%m-%d') if todate else cur_date
        frmdate = dates['first_issued_date']
        frmdate = frmdate.strftime('%Y-%m-%d') if frmdate else prev_date
    else:
        if searchkey == 'None':
            searchkey = None
        tickets = searchfilter(cmpnyId,frmdate,todate,searchkey)
        inbox = tickets.filter(status__in=['TP', 'DH', 'RC', 'PC', 'PP', 'EH', 'CR']).order_by('ticket_no')
        in_progress = tickets.filter(Q(status__in=['TA', 'DA', 'EP', 'EA', 'RA', 'RL', 'CD', 'BP'])).count()
        forwarded = tickets.filter(Q(status__in=['TH', 'PA', 'CA'])).count()
        closed = tickets.filter(Q(status__in = ['TC'])).count()
        chat_notification(request,inbox)


    from django.db.models import OuterRef, Subquery, IntegerField
    from django.db.models.functions import Coalesce
    ticket_subquery = (
    Tickets.objects
    .filter(dev_id=OuterRef('username'))
    .exclude(status__in=["TC", "TP"])
    .values('dev_id')
    .annotate(count=Count('ticket_no'))
    .values('count')[:1]  # Only need the count value
)
    devs = CustomUser.objects.filter(role='D', is_active=True).annotate(
    ticket_count=Coalesce(Subquery(ticket_subquery, output_field=IntegerField()), 0)
)
    # devs = CustomUser.objects.filter(role='D' , is_active = 1)

    testers = CustomUser.objects.filter(role='T')


    return render(request,'cAdmin/adminDashboard.html',{'tickets':inbox,'testers':testers,'devs':devs,'inprogress':in_progress,'fwd':forwarded,'closed':closed , 'filter_cname':filter_cname,'to_date':todate,'prev_date':frmdate,'keyword':searchkey,'company_id':cmpnyId, 'flag':flag, 'bell_not': bell_not})



@never_cache
@login_required(login_url="/cadmin/admin_login/")
def adminInProgress(request,cmpnyId=None,frmdate=None,todate=None,searchkey = None , flag = '0'):
    bell_not = bell_notification(request)
    print(bell_notification)
    cur_date = datetime.now()
    prev_date = cur_date - timedelta(days=30)
    cur_date = cur_date.strftime('%Y-%m-%d')
    prev_date = prev_date.strftime('%Y-%m-%d')
    tickets = None
    inbox = None 
    in_progress = None 
    forwarded = None 
    closed = None
    filter_cname = Company.objects.exclude(companyId = request.user.company_id)
    ticket_counts = Tickets.objects.aggregate(
            inbox=Count('ticket_no', filter=Q(status__in=['TP', 'DH', 'RC', 'PC', 'PP', 'EH', 'CR'])),
            forwarded=Count('ticket_no', filter=Q(status__in=['TH', 'PA', 'CA'])),
            closed=Count('ticket_no', filter=Q(status='TC'))
                )
    if flag == '0':
        # inbox stat : 'TP', 'DH', 'RC', 'PC', 'PP', 'EH', 'CR'  , in_progress stat : 'TA', 'DA', 'EP', 'EA', 'RA', 'RL', 'CD', 'BP'
        in_progress = Tickets.objects.filter(status__in=['TA', 'DA', 'EP', 'EA', 'RA', 'RL', 'CD', 'BP']).order_by('ticket_no')
        
        dates = in_progress.aggregate(
            first_issued_date=Min('issued_on'),
            last_issued_date=Max('issued_on')
            )  
       
        chat_notification(request, in_progress)
        inbox = ticket_counts['inbox'] 
        forwarded = ticket_counts['forwarded'] 
        closed = ticket_counts['closed'] 
        todate = dates['last_issued_date']
        todate = todate.date().strftime('%Y-%m-%d') if todate else cur_date
        frmdate = dates['first_issued_date']
        frmdate = frmdate.strftime('%Y-%m-%d') if frmdate else prev_date
    else:

        if searchkey == 'None':
            searchkey = None
        tickets = searchfilter(cmpnyId,frmdate,todate,searchkey)
        inbox = tickets.filter(Q(status__in=['TP', 'DH', 'RC', 'PC', 'PP', 'EH', 'CR'])).count()
        in_progress = tickets.filter(status__in=['TA', 'DA', 'EP', 'EA', 'RA', 'RL', 'CD', 'BP'])
        forwarded = tickets.filter(Q(status__in=['TH', 'PA', 'CA'])).count()
        closed = tickets.filter(Q( status__in = ['TC'])).count()
    devs = CustomUser.objects.filter(role='D' , is_active = 1)
    return render(request,'cAdmin/adminProgress.html',{'tickets':in_progress,'inbox':inbox,'forwarded':forwarded,'closed':closed,'filter_cname':filter_cname,'to_date':todate,'prev_date':frmdate,'keyword':searchkey,'company_id':cmpnyId, 'flag': flag , 'bell_not': bell_not, 'devs' : devs })



@never_cache
@login_required(login_url="/cadmin/admin_login/")
def adminForwarded(request,cmpnyId=None,frmdate=None,todate=None,searchkey = None , flag = '0'):
    bell_not = bell_notification(request)
    cur_date = datetime.now()
    prev_date = cur_date - timedelta(days=30)
    cur_date = cur_date.strftime('%Y-%m-%d')
    prev_date = prev_date.strftime('%Y-%m-%d')
    tickets = None
    inbox = None 
    in_progress = None 
    forwarded = None 
    closed = None
    filter_cname = Company.objects.exclude(companyId = request.user.company_id)
    ticket_counts = Tickets.objects.aggregate(
            inbox=Count('ticket_no', filter=Q(status__in=['TP', 'DH', 'RC', 'PC', 'PP', 'EH', 'CR'])),
            in_progress =Count('ticket_no', filter=Q(status__in=['TA', 'DA', 'EP', 'EA', 'RA', 'RL', 'CD', 'BP'])),
            closed=Count('ticket_no', filter=Q(status='TC'))
                )
    if flag == '0':
        #inprogress stat : ['TA', 'DA', 'EP', 'EA', 'RA', 'RL', 'CD', 'BP'] Forwarded : ['TH', 'PA', 'CA']
        forwarded = Tickets.objects.filter(status__in=['TH', 'PA', 'CA']).order_by('issued_on')
        dates = forwarded.aggregate(
            first_issued_date=Min('issued_on'),
            last_issued_date=Max('issued_on')
            )  
        chat_notification(request, forwarded)

        inbox = ticket_counts['inbox'] 
        in_progress = ticket_counts['in_progress'] 
        closed = ticket_counts['closed'] 
        todate = dates['last_issued_date']
        todate = todate.date().strftime('%Y-%m-%d') if todate else cur_date
        frmdate = dates['first_issued_date']
        frmdate = frmdate.strftime('%Y-%m-%d') if frmdate else prev_date
    else:

        if searchkey == 'None':
            searchkey = None
        tickets = searchfilter(cmpnyId,frmdate,todate,searchkey)
        inbox = tickets.filter(Q(status__in=['TP', 'DH', 'RC', 'PC', 'PP', 'EH', 'CR'])).count()
        in_progress = tickets.filter(status__in=['TA', 'DA', 'EP', 'EA', 'RA', 'RL', 'CD', 'BP']).count()
        forwarded = tickets.filter(Q(status__in=['TH', 'PA', 'CA']))
        closed = tickets.filter(Q( status__in = ['TC'])).count()
        chat_notification(request, forwarded)


    return render(request,'cAdmin/adminForwarded.html',{'tickets':forwarded,'inbox':inbox,'closed':closed,'inprogress':in_progress,'filter_cname':filter_cname,'to_date':todate,'prev_date':frmdate,'keyword':searchkey,'company_id':cmpnyId,'flag':flag, 'bell_not': bell_not })


@never_cache
@login_required(login_url="/cadmin/admin_login/")
def adminClosed(request,cmpnyId=None,frmdate=None,todate=None,searchkey = None ,  flag = '0'):
    cur_date = datetime.now()
    bell_not = bell_notification(request)
    prev_date = cur_date - timedelta(days=30)
    cur_date = cur_date.strftime('%Y-%m-%d')
    prev_date = prev_date.strftime('%Y-%m-%d')
    tickets = None
    inbox = None 
    in_progress = None 
    forwarded = None 
    closed = None
    filter_cname = Company.objects.exclude(companyId = request.user.company_id)
    ticket_counts = Tickets.objects.aggregate(
            inbox=Count('ticket_no', filter=Q(status__in=['TP', 'DH', 'RC', 'PC', 'PP', 'EH', 'CR'])),
            in_progress =Count('ticket_no', filter=Q(status__in=['TA', 'DA', 'EP', 'EA', 'RA', 'RL', 'CD', 'BP'])),
            forwarded =Count('ticket_no', filter=Q(status__in=['TH', 'PA', 'CA']))
                )
    if flag == '0':
        #inprogress stat : ['TA', 'DA', 'EP', 'EA', 'RA', 'RL', 'CD', 'BP'] Forwarded : ['TH', 'PA', 'CA']
        closed = Tickets.objects.filter(status = 'TC').order_by('issued_on')
        dates = closed.aggregate(
            first_issued_date=Min('issued_on'),
            last_issued_date=Max('issued_on')
            )  
        inbox = ticket_counts['inbox'] 
        in_progress = ticket_counts['in_progress'] 
        forwarded = ticket_counts['forwarded'] 
        todate = dates['last_issued_date']
        todate = todate.date().strftime('%Y-%m-%d') if todate else cur_date
        frmdate = dates['first_issued_date']
        frmdate = frmdate.strftime('%Y-%m-%d') if frmdate else prev_date
    else:

        if searchkey == 'None':
            searchkey = None
        tickets = searchfilter(cmpnyId,frmdate,todate,searchkey)
        inbox = tickets.filter(Q(status__in=['TP', 'DH', 'RC', 'PC', 'PP', 'EH', 'CR'])).count()
        in_progress = tickets.filter(status__in=['TA', 'DA', 'EP', 'EA', 'RA', 'RL', 'CD', 'BP']).count()
        forwarded = tickets.filter(Q(status__in=['TH', 'PA', 'CA'])).count()
        closed = tickets.filter(Q( status__in = ['TC']))

    return render(request,'cAdmin/adminClosed.html',{'tickets':closed,'inbox':inbox,'forwarded':forwarded,'inprogress':in_progress,'filter_cname':filter_cname,'to_date':todate,'prev_date':frmdate,'keyword':searchkey,'company_id':cmpnyId, 'flag' : flag, 'bell_not': bell_not})



@never_cache
def admin_sigout(request):
    logout(request)
    return redirect('admin_login')

@login_required(login_url="/cadmin/admin_login/")
@never_cache

def companyManagement(request): 
    cmpnyList = Company.objects.exclude(companyId=request.user.company_id ,)
    cmpnyList = cmpnyList.filter(is_active=True)  # Corrected line
    return render(request, 'cAdmin/companyManagement.html',{'cmpnylist':cmpnyList})

@never_cache
@login_required(login_url="/cadmin/admin_login/")
def addcompany(request,cmpId=None):
    #admn_id = request.session['_auth_user_id']
    CDF = PCTN = SCTN = 0
    cmpnyadd = addCompany()
    if request.method == 'POST':
        cmpnyadd = addCompany(request.POST)
        if cmpnyadd.is_valid():
            company_instance = cmpnyadd.save(commit=False)
            company_instance.is_active = True
            cmpnyadd.save()
            admn_id = request.session['_auth_user_id']
            admin_company_id = User.objects.values('company_id').get(id=request.session['_auth_user_id'])['company_id']
            cmpnyList_temp = Company.objects.exclude(companyId=admin_company_id)
            cmpnyList = cmpnyList_temp.filter(is_active = True)
            messages.success(request, 'Saved!')
            return render(request, 'cAdmin/companyManagement.html',{'cmpnylist':cmpnyList,})
    
    return render(request, 'cAdmin/addCompany.html', {'form': cmpnyadd,'CDF':CDF})

@never_cache
@login_required(login_url="/cadmin/admin_login/")
def editCompanyDetails(request,cmpId=None):
    data = get_object_or_404(Company, companyId=cmpId)
    edit = editCompany(instance=data)
    #LoggedUser = get_object_or_404(CompanyAdmin,admnId=request.session['_auth_user_id'])
    if request.method == 'POST':
        form = editCompany(request.POST, instance=data)
        if form.is_valid():
            form.save()
            admn_id = request.session['_auth_user_id']
            admin_company_id = User.objects.values('company_id').get(id=request.session['_auth_user_id'])['company_id']
            cmpnyList = Company.objects.exclude(companyId=admin_company_id)
            messages.success(request, 'Saved!')
            return render(request, 'cAdmin/companyManagement.html',{'cmpnylist':cmpnyList,})
        else:
            print(form.errors)
    return render(request, 'cAdmin/editCompany.html', {'form': edit,})


@never_cache
@login_required(login_url="/cadmin/admin_login/")
def companySettings(request,cmpnyId):
    cmpny = get_object_or_404(Company,companyId=cmpnyId)
    return render(request,'cAdmin/companysettings.html',{'cmpnyId':cmpny,})
@never_cache
@login_required(login_url="/cadmin/admin_login/")
def addDepartment(request,companyId):
    LoggedUser = get_object_or_404(User,id=request.session['_auth_user_id'])
    deptadd = addDepartmentf()
    if request.method == 'POST':
        deptadd = addDepartmentf(request.POST)
        if deptadd.is_valid():
            deptadd.instance.companyId_id = companyId
            deptadd.save()
            depts = Department.objects.filter(companyId_id = companyId)
            messages.success(request, 'Saved!')
            return render(request,'cAdmin/departmentManagement.html',{'depts':depts,'cmpnyId':companyId})
    return render(request,'cAdmin/addDepartment.html',{'form':deptadd,})

@never_cache
@login_required(login_url="/cadmin/admin_login/")
def departmentManagement(request,companyId):
    try:
        depts = Department.objects.filter(companyId_id = companyId)
    except:
        depts=None
    return render(request,'cAdmin/departmentManagement.html',{'depts':depts,'cmpnyId':companyId})

@never_cache
@login_required(login_url="/cadmin/admin_login/")

def addCategory(request,companyId):
    # LoggedUser = get_object_or_40 4(User,id=request.session['_auth_user_id'])
    category_add = addCategoryf()
    if request.method == 'POST':
        cateadd = addCategoryf(request.POST)
        if cateadd.is_valid():
            cateadd.instance.company_id = companyId
            cateadd.instance.is_active = 1
            cateadd.save()
            category = Category.objects.filter(company_id = companyId, is_active = True)
            messages.success(request, 'Category Saved!')
            return redirect('category_management', companyId=companyId)                   
    else:
        return render(request,'cAdmin/addCategory.html',{'form':category_add,})

@never_cache
@login_required(login_url="/cadmin/admin_login/")
def categoryManagement(request,companyId):
    
    try:
        category = Category.objects.filter(company_id = companyId, is_active = True)

        
    except:
        depts=None

    category_add = addCategoryf()
    if request.method == 'POST':
        cateadd = addCategoryf(request.POST)
        if cateadd.is_valid():
            cateadd.instance.company_id = companyId
            cateadd.instance.is_active = True
            cateadd.save()
            category = Category.objects.filter(company_id = companyId)
            messages.success(request, 'Category Saved!')
            return redirect('category_management',companyId = companyId)
    return render(request,'cAdmin/categoryManagement.html',{'category':category,'cmpnyId':companyId,'form':category_add})
    

def categoryRedDir(request,category=None,cmpnyId=None,):
    category = Category.objects.filter(company_id = cmpnyId)
    category_add = addCategoryf()
    return render(request,'cAdmin/categoryManagement.html',{'category':category,'cmpnyId':cmpnyId,'form':category_add})


def developersManagement(request):
    pass

@never_cache
@login_required(login_url="/cadmin/admin_login/")
def userManagement(request,cmpId=None):
    UsersList=User.objects.filter(company_id=cmpId , role = 'U')
    
    context={'Users':UsersList,
             'cmpnyId':cmpId,
                }
    return render(request,'cAdmin/userManagement.html',context)




@never_cache
@login_required(login_url="/cAdmin/")
def addUser(request,companyId=None):
    company_instance = get_object_or_404(Company, companyId=companyId)
    UserForm = UserAdd() 
    # UserForm.fields['department'].queryset = Department.objects.filter(companyId_id=companyId)  
    if request.method == 'POST':
        UserForm=UserAdd(request.POST)
        if UserForm.is_valid():
            password = UserForm.cleaned_data.get('password')
            UserForm.instance.password = make_password(password)
            UserForm.instance.company = company_instance
            UserForm.instance.role = 'U'
            UserForm.save()
            # UsersList=User.objects.filter(company_id=companyId)
            # context={'Users':UsersList,'cmpnyId':companyId,}
            return redirect('users_list',cmpnyId=companyId)
    print(UserForm.errors)
    context={'form':UserForm }
    return render(request,'cAdmin/userAdd.html',context)

@never_cache
@login_required(login_url="/cadmin/admin_login/")
def usersListredir(request,cmpnyId):
    Users = User.objects.filter(company_id=cmpnyId)
    return render(request,'cAdmin/userManagement.html',{'Users':Users,'cmpnyId':cmpnyId})

@never_cache
@login_required(login_url="/cadmin/admin_login/")
def adminPendingsDashboard(request):
    tickets = Tickets.objects.filter(status='TP')

    return render(request,'cAdmin/adminDashboard.html',{'tickets':tickets})
    
@never_cache
@login_required(login_url="/cadmin/admin_login/")
def categoryDelete(request) :
    if request.method == 'POST':
        category_id = int(request.POST['category_id'])
        category_qry = Category.objects.get(ctgryId = category_id )
        category_qry.is_active = False
        category_qry.save()
        messages.success(request,'Successfully deleted '+category_qry.ctgryName,)
        return redirect('category_management',companyId= request.POST['company_id'])



def deleteTicket(request,ticketid):
    try:
        ticket = get_object_or_404(Tickets, ticketId=ticketid)
        ticket.delete()
        messages.success(request, 'Rejected!')
        return redirect('admin_home')
    except:
        messages.success(request, 'Rejected!')
        return redirect('admin_home')    

@never_cache
@login_required(login_url="/cadmin/admin_login/")
def developersManagement(request,):
    try:
        devs = CustomUser.objects.filter(Q(role='D') | Q(role='T') )

    except:
        dev=None
    return render(request,'cAdmin/developersManagement.html',{'devs':devs,})

@never_cache
@login_required(login_url="/cadmin/admin_login/")
def addDev(request):
    #devform = addDeveloper(request.POST)
    if request.method == 'POST':
        devform = addDeveloper(request.POST)
        if devform.is_valid():
            dev_instance = devform.save(commit=False)
            dev_instance.role = devform.cleaned_data['slct_role']
            password = devform.cleaned_data['password']
            dev_instance.password = make_password(password)
            dev_instance.company = request.user.company
            dev_instance.save()
            messages.success(request, 'Saved!')
            return redirect('developer_management')
    return render(request,'cAdmin/addDeveloper.html',{'form':devform})

@never_cache
@login_required(login_url="/cadmin/admin_login/")
def update_is_active(request, item_id):
    if request.method == "POST" and request.headers.get("Content-Type") == "application/json":
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


@never_cache
@login_required(login_url="/cadmin/admin_login/")
def assignTicketList(request,ticket_id,):

    devs = CustomUser.objects.filter(Q(role='D') & Q(is_active=True))
    return render(request,'cAdmin/assignTicket.html',{'devs':devs,'ticket_id':ticket_id})


@never_cache
@login_required(login_url="/cadmin/admin_login/")   
def assignTicket(request):
    ticket = Tickets.objects.get(ticket_no = request.POST['updtid'])
    temp_stat = 'TA'
    if ticket.status == 'TA' or ticket.status == 'TRA' :
         temp_stat = 'TRA' # Ticket reassigne TRA
    # if ticket.dev_is None and ticket.tester_id is None:
    ticket.approved_by = request.user.username
    ticket.approved_on = datetime.now()
    ticket.updated_by = request.user
    if request.POST['remarks'] != '':
        ticket.remarks = request.POST['remarks']
        rflag = 1
    # if 'rmk_files' in request.POST:
    #     ticket.remarkfile = request.POST['rmk_files']

    ticket.updated_on = datetime.now()
    ticket.dev_assigned_date = datetime.now()
    ticket.dev_id = request.POST['devassign']
    ticket.status = temp_stat 
    CpyLog(ticket,request.POST['remarks']) 
    ticket.status = 'TA'     
    ticket.expiry = None 
    ticket.save()
    mail_subject = f'Ticket Assignment Notification. TICKET NUMBER : {ticket.ticket_no}'
    mail_assgn_ticket = f'''
    Dear Developer,

    A new ticket has been assigned to you. Please review the details and take the necessary action.
    
    🔹 Ticket ID: {ticket.ticket_no}


    Please log in to your account to review and respond as needed.

    Best Regards,
    Tweedle Support Team

 '''
    if(request.POST['mail_reminder_flag'] == 'on'):
        EmailThread(mail_subject, mail_assgn_ticket, ["jinoyks.mefs@gmail.com"]).start()
    messages.success(request, 'Assigned to : ' + ticket.dev_id )
    if request.POST.get('page_id') == 'I':
        return redirect('admin_inprogress')    
    return redirect('admin_home')
    


@never_cache                                             #flagged NB: No
@login_required(login_url="/cadmin/admin_login/")
def tstrAdmnAcpt(request,ticket_id):
    ticket = Tickets.objects.get(ticket_no = ticket_id)
    # CpyLog(ticket)
    ticket.approved_by = request.user.username
    ticket.approved_on = datetime.now()
    ticket.updated_by = request.user
    ticket.status = 'PA'       
    ticket.save()
    CpyLog(ticket,request.POST['remarks'])
    messages.success(
        request, 'Forwarded to client!'
    )
    return redirect('admin_home')

    

@never_cache
@login_required(login_url="/cadmin/admin_login/")
def testerOperations(request,): # Tester Assign and tester change or tester status changes will be marked
    ticket = Tickets.objects.get(ticket_no = request.POST['updtid'])
    # CpyLog(ticket)
 

    if ticket.status == 'EH' :
        ticket.approved_by = request.user.username
        ticket.updated_by = request.user
        if 'tstr_drpdwn' in request.POST:
            ticket.tester_id = request.POST['tstr_drpdwn']
        if 'rmk_files' in request.FILES:
            ticket.rmrk_files = request.FILES['rmk_files']
            rflag = 1
        if 'rmk_files' in request.FILES:
            ticket.rmrk_files = request.FILES['rmk_files']

        ticket.status = 'EP'
        ticket.tester_assigned_date = datetime.now()
        ticket.save()
        CpyLog(ticket,request.POST['remarks'],request.FILES.get('rmk_files', None))
        messages.success(
            request, 'Forwarded to tester!'
        )

    

    elif ticket.status == 'PP' and request.POST['flag'] == '0' :
        ticket.approved_by = request.user.username
        ticket.updated_by = request.user
        if request.POST['remarks'] != '':
            ticket.remarks = request.POST['remarks']
        if 'rmk_files' in request.POST:
            ticket.rmrk_files = request.POST['rmk_files']

            rflag =1
        ticket.status = 'PA'
        ticket.save()
        CpyLog(ticket,request.POST['remarks'],request.FILES.get('rmk_files', None))
        messages.success(
        request, 'Forwarded to client!'
            )

    elif ticket.status == 'PP' and request.POST['flag'] == '1' : # this flag =1 refers if the admin wants go for one more testing he can re assign  if this set to 1 then it'll be assigned to desired tester again
        ticket.approved_by = request.user.username
        ticket.updated_by = request.user
        ticket.tester_id = request.POST['tstr_drpdwn']
        if request.POST['remarks'] != '':
            ticket.remarks = request.POST['remarks']
            rflag=1
        if 'tstr_drpdwn' in request.POST:
            ticket.tester_id = request.POST['tstr_drpdwn']
        if 'rmk_files' in request.POST:
            ticket.rmrk_files = request.POST['rmk_files']

        ticket.status = 'EP'
        ticket.tester_assigned_date = datetime.now()
        ticket.save()
        CpyLog(ticket,request.POST['remarks'],request.FILES.get('rmk_files', None))
        messages.success(
            request, 'Forwarded to tester!'
        )
    return redirect('admin_inprogress')

@never_cache
@login_required(login_url="/cadmin/admin_login/")
def devOperations(request,):
    ticket = Tickets.objects.get(ticket_no = request.POST['updtid'])
    if ticket.status == 'RC':
        ticket.approved_by = request.user.username
        ticket.updated_by = request.user
        if request.POST['remarks'] != '':
            ticket.remarks = request.POST['remarks']
            rflag=1
        if 'rmk_files' in request.FILES:
            ticket.rmrk_files = request.FILES['rmk_files']
        ticket.status = 'RL'
        ticket.save()
        CpyLog(ticket,request.POST['remarks'],request.FILES.get('rmk_files', None))
        messages.success(
            request, 'Proceeded to copy!'
        )
        return redirect('admin_inprogress')


    elif ticket.status == 'PC':
        if ticket.old_ticket is not None:
            sticket = uTickets.objects.get(ticket_no = ticket.old_ticket)
            sticket.status = 'TC'
            sticket.closed_on = datetime.now()
            sticket.closed_by = request.user.username
            sticket.save()

        ticket.approved_by = request.user.username
        ticket.updated_by = request.user
        ticket.status = 'TC'
        if request.POST['remarks'] != '':
            ticket.remarks = request.POST['remarks']
            rflag=1
        if 'rmk_files' in request.FILES:
            ticket.rmrk_files = request.FILES['rmk_files']
        ticket.closed_on = datetime.now()
        ticket.closed_by = request.user.username
        ticket.save()
        CpyLog(ticket,request.POST['remarks'],request.FILES.get('rmk_files', None))
        messages.success(
            request, 'Ticket Closed!!'
        )
        return redirect('admin_home')

    elif ticket.status == 'DH':
        ticket.approved_by = request.user.username
        ticket.updated_by = request.user
        if request.POST['remarks'] != '':
            ticket.remarks = request.POST['remarks']
            rflag=1
        if 'dev_drpdwn' in request.POST:
            ticket.dev_id = request.POST['dev_drpdwn']
        if 'rmk_files' in request.FILES:
            ticket.rmrk_files = request.FILES['rmk_files']
        ticket.status = 'TH'
        ticket.save()
        CpyLog(ticket,request.POST['remarks'],request.FILES.get('rmk_files', None))
        messages.success(
            request, 'Forwarded to client!'
        )
        return redirect('admin_home')
    
    elif ticket.status == 'TP': # important program chat related one
        ticket.approved_by = request.user.username
        ticket.updated_by = request.user
        if request.POST['remarks'] != '':
            ticket.remarks = request.POST['remarks']
            rflag=1
        if 'rmk_files' in request.FILES:
            ticket.rmrk_files = request.FILES['rmk_files']
        ticket.status = 'TA'
        ticket .save()
        CpyLog(ticket,request.POST['remarks'],request.FILES.get('rmk_files', None))
        messages.success(
            request, 'Approved to developer!'
        )
        return redirect('admin_home' )
    elif ticket.status == 'CR': # important program chat related one
        ticket.approved_by = request.user.username
        ticket.updated_by = request.user
        if request.POST['remarks'] != '':
            ticket.remarks = request.POST['remarks']
            rflag=1
        if 'rmk_files' in request.FILES:
            ticket.rmrk_files = request.FILES['rmk_files']
        ticket.status = 'CA'
        ticket .save()
        CpyLog(ticket,request.POST['remarks'],request.FILES.get('rmk_files', None))
        messages.success(
            request, 'Forwarded to developer!'
        )
        return redirect('admin_home' )



@never_cache
@login_required(login_url="/cadmin/admin_login/")
def logs(request,ticket_id): #for oulook data
    logs =  TicketLogs.objects.filter(ticket_no = ticket_id).order_by('updated_on')
    ticket_details = TicketLogs.objects.filter(ticket_no = ticket_id).order_by('updated_on').first()
    return render(request,'cAdmin/timeline3.html',{'logs':logs,'ticket_id':ticket_id})


@never_cache
@login_required(login_url="/cadmin/admin_login/")
def tcktFilter(request,):

    if request.method == 'POST':    
        # if  request.POST['key'] != 't':
        if request.user.role == 'A':
            if  request.POST['page_id_val'] == 'P' :
                return redirect('admin_home',cmpnyId = request.POST['companyDropdown'],frmdate = request.POST['fromDateInput'],todate=request.POST['toDateInput'], searchkey =  request.POST['keyword'].strip() or None , flag = request.POST['flag'] )

            elif  request.POST['page_id_val'] == 'I':
                return redirect('admin_inprogress',cmpnyId = request.POST['companyDropdown'],frmdate = request.POST['fromDateInput'],todate=request.POST['toDateInput'], searchkey=  request.POST['keyword'].strip() or None , flag = request.POST['flag'] )

            elif  request.POST['page_id_val'] == 'F':
                return redirect('admin_forwarded',cmpnyId = request.POST['companyDropdown'],frmdate = request.POST['fromDateInput'],todate=request.POST['toDateInput'], searchkey=  request.POST['keyword'].strip() or None , flag = request.POST['flag'])

            elif  request.POST['page_id_val'] == 'C':
                return redirect('admin_closed',cmpnyId = request.POST['companyDropdown'],frmdate = request.POST['fromDateInput'],todate=request.POST['toDateInput'], searchkey=  request.POST['keyword'].strip() or None , flag = request.POST['flag'])



@never_cache
@login_required(login_url="/cadmin/admin_login/")
def admnRjct(request,tno = None,remarks = None):
    ticket = Tickets.objects.get(ticket_no = tno)
    ticket.status = 'TC'
    if remarks != '~' :
        ticket.remarks = remarks
        rflag=1
    if 'rmk_files' in request.FILES:
            ticket.rmrk_files = request.FILES['rmk_files']
    ticket.closed_on = datetime.now()
    ticket.closed_by = request.user.username
    if ticket.old_ticket is not None:
            sticket = uTickets.objects.get(ticket_no = ticket.old_ticket)
            sticket.status = 'TC'
            sticket.closed_on = datetime.now()
            sticket.closed_by = request.user.username
            sticket.save()
    ticket.save()
    CpyLog(ticket,remarks,request.FILES.get('rmk_files', None))
    messages.success(
            request, 'Ticket Closed!'
        )
    return redirect('admin_home')


@never_cache
@login_required(login_url="/cadmin/admin_login/")
def admnQryClse(request,tno,remarks=None):
    if remarks is None :
        remarks=''
    ticket_id = Tickets.objects.get(ticket_no = tno)
    if ticket_id.status == 'DH':
        ticket_id.status = 'TA'
        ticket_id.updated_by = request.user
        if remarks != '~' or remarks != '' :
            ticket_id.remarks = remarks
        else:
            ticket_id.remarks = None
        if 'rmk_files' in request.FILES:
            ticket_id.rmrk_files = request.FILES['rmk_files']
            rflag=1
        ticket_id.save()
        CpyLog(ticket_id,remarks)
        messages.success(
            request, 'Clarification sent!'
        )
        return redirect('admin_home')

@never_cache
@login_required(login_url="/cadmin/admin_login/")
def adminReports(request):
    return render(request,'cAdmin/adminreports.html',{})

@never_cache
@login_required(login_url="/cadmin/admin_login/")
def developerEdit(request,dev_id = None):  
    dev_data = CustomUser.objects.get(id = dev_id)
    form = editDevForm(instance=dev_data)
    if request.method == 'POST':
        form = editDevForm(request.POST, instance=dev_data)
        if form.is_valid():
            # Compare form data with existing data
            for field in form.fields:
                if form.cleaned_data[field] != getattr(dev_data, field):
                    setattr(dev_data, field, form.cleaned_data[field])
            # Save only the updated fields
            dev_data.save()
            messages.success(request,'Saved!')
            return redirect('developer_management')
    return render(request,'cAdmin/developerEdit.html',{'form' : form})

@never_cache
@login_required(login_url="/cadmin/admin_login/")
def userEdit(request,usr_id = None):
    usr_data = CustomUser.objects.get(id = usr_id)
    form = editUsrForm(instance=usr_data)
    if request.method == 'POST':
        form = editUsrForm(request.POST, instance=usr_data)
        if form.is_valid():
            if form.has_changed():
                usr_data = form.save()
                messages.success(request, 'Saved!')
                return redirect('user_management', cmpId=int(usr_data.company_id))
    return render(request, 'cAdmin/userEdit.html', {'form': form})

@never_cache
@login_required(login_url="/cadmin/admin_login/")
def deleteCompany(request):
    cmpnyId = request.POST['cmpnyId']
    cmpny = Company.objects.get(companyId = cmpnyId )
    cmpny.is_active = False
    cmpny.save()
    messages.success(request, 'Company deleted successfully!')
    return redirect('company_management')
    
@never_cache
@login_required(login_url="/cadmin/admin_login/")
def psswdReset(request):

    if request.method == 'POST':

        new_psswd = request.POST.get('new_psswd')
        psswd = request.POST.get('psswd')


        # Check if the entered password is correct
        password_is_correct = check_password(psswd, request.user.password)

        if password_is_correct:
            
            request.user.set_password(new_psswd)
            request.user.save()

            messages.success(request, 'Password changed successfully! Now you will be loged out.')
            
            
            return redirect('admin_login')
        else:
            messages.success(request, 'Incorrect current password. Please try again.')
    if request.user.role == 'A':
        return render(request,'cAdmin/adminPsswdReset.html',{}) 
    elif request.user.role == 'D':
        return render(request,'developers/devPsswdReset.html',{}) 
    elif request.user.role == 'T':
        return render(request,'testers/testerPsswdReset.html',{}) 
    elif request.user.role == 'U':
        return render(request,'User/userPsswdReset.html',{})
    elif request.user.role == 'EU':
        return render(request,'User/sUserPsswdReset.html',{})  
    
@login_required(login_url="/cadmin/admin_login/")
def check_session(request):
    if not request.user.is_authenticated:  # If session expired
        return JsonResponse({"session_expired": True})
    return JsonResponse({"session_expired": False})

 # Reports =========================================================================================
@never_cache
@login_required(login_url="/cadmin/admin_login/")
def ticketsReport(request, frmdate=None, todate=None, status=None, developer=None, client=None, report=None):
    query_filter = Q()

    # Handle date range safely
    if not frmdate:
        frmdate = datetime.now().date()
    else:
        frmdate = datetime.strptime(frmdate, "%Y-%m-%d").date()

    if not todate:
        todate = datetime.now().date()
    else:
        todate = datetime.strptime(todate, "%Y-%m-%d").date()

    query_filter &= Q(issued_on__date__range=(frmdate, todate))

    # Status categories
    inbox_statuses = ['TP', 'DH', 'RC', 'PC', 'PP', 'EH', 'CR']
    in_progress_statuses = ['TA', 'DA', 'EP', 'EA', 'RA', 'RL', 'CD', 'BP']
    forwarded_statuses = ['TH', 'PA', 'CA']
    closed_status = ['TC']

    # Subquery to fetch `issued_on` from `uTickets`
    subquery = uTickets.objects.filter(
        ticket_no=OuterRef('old_ticket')
    ).values('issued_on')[:1]

    stat_array = ['A', 'B', 'C', 'D']

    if status in stat_array:
        flag_val = None
        if status == 'A':
            query_filter &= Q(status__in=inbox_statuses)
            flag_val = 'INBOX'
        elif status == 'B':
            query_filter &= Q(status__in=in_progress_statuses)
            flag_val = 'IN PROGRESS'
        elif status == 'C':
            query_filter &= Q(status__in=forwarded_statuses)
            flag_val = 'FORWARDED'
        elif status == 'D':
            query_filter &= Q(status__in=closed_status)
            flag_val = 'CLOSED'

        results = Tickets.objects.filter(query_filter).annotate(
            tmp_issued_on=Subquery(subquery),
            status_flag=Value(flag_val or '', output_field=CharField())
        )
    else:
        results = Tickets.objects.filter(query_filter).annotate(
            tmp_issued_on=Subquery(subquery),
            status_flag=Case(
                When(status__in=inbox_statuses, then=Value('INBOX')),
                When(status__in=in_progress_statuses, then=Value('IN PROGRESS')),
                When(status__in=forwarded_statuses, then=Value('FORWARDED')),
                When(status__in=closed_status, then=Value('CLOSED')),
                default=Value(''),
                output_field=CharField(),
            )
        )

    # 🔹 Developer filter
    if developer and developer != "ALL":
        query_filter &= Q(dev_id=developer)

    # 🔹 Client filter
    if client and client != "ALL":
        query_filter &= Q(client=client)

    # Apply filters
    results = Tickets.objects.filter(query_filter).annotate(
        tmp_issued_on=Subquery(subquery)
    )

    # Add TAT dynamically
    for result in results:
        if result.closed_on and result.approved_on:
            result.tat = (result.closed_on - result.approved_on).days

    developers = Tickets.objects.exclude(dev_id__isnull=True).exclude(dev_id='').values_list('dev_id', flat=True).distinct()
    clients = Tickets.objects.exclude(client__isnull=True).exclude(client='').values_list('client', flat=True).distinct()


    return render(request, 'cAdmin/reports.html', {
        'tickets': results,
        'frmdate': frmdate,
        'todate': todate,
        'status': status,
        'developer': developer,
        'client': client,
        'developers': developers,
        'clients': clients,
    })






# @never_cache
# @login_required(login_url="/cadmin/admin_login/")
# def ticketsReport(request):
#     subquery = uTickets.objects.filter(ticket_no=OuterRef('old_ticket')).values('issued_on')[:1]
#     # results = Tickets.objects.annotate(tmp_issued_on=Subquery(subquery)).all().annotate()
#     inbox_statuses = ['TP', 'DH', 'RC', 'PC', 'PP', 'EH', 'CR']
    
#     results = Tickets.objects.annotate(
#         tmp_issued_on=Subquery(subquery),
#         status_flag=Case(
#             When(status__in=allowed_statuses, then=Value('IN')),
#             default=Value(''),
#             output_field=CharField(),
#         )
#     ).all()
    
#     return render(request,'cAdmin/reports.html',{'tickets':results, })
#     pass


#  ticket_counts = Tickets.objects.aggregate(
#             in_progress=Count('ticket_no', filter=Q(status__in=['TA', 'DA', 'EP', 'EA', 'RA', 'RL', 'CD', 'BP'])),
#             forwarded=Count('ticket_no', filter=Q(status__in=['TH', 'PA', 'CA'])),
#             closed=Count('ticket_no', filter=Q(status='TC'))
#                 )
#     if flag == '0':
#         inbox = Tickets.objects.filter(status__in=['TP', 'DH', 'RC', 'PC', 'PP', 'EH', 'CR']).order_by('ticket_no')