from django.shortcuts import render

# Create your views here.

def userLogin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username,password=password)
        print('status',get_company_is_active_status)
        if user is not None and user.is_active and user.role == 'TU' :
            login(request,user)
            return redirect('user_home')
        else:
            return render(request,'User/userindex.html',{})

    return render(request,'User/userindex.html',{})



@never_cache
@login_required(login_url="/cadmin/admin_login/")
def raiseTicket(request):
    ticketform = TicketForm(company = request.user.company) #company = request.user.company
    if request.method == 'POST':
        ticketform = TicketForm(request.POST, request.FILES, company=request.user.company)
        logger.debug('is valid worked')
        if ticketform.is_valid():
            logger.debug('is valid worked')
            print('is valid worked')
            ticketform_instance = ticketform.save(commit=False)
            ticketform_instance.ticket_no =  TcktCde(request)
            client = get_object_or_404(CustomUser, id=request.user.id)
            print(client, 'client id', request.user.id)
            ticketform_instance.client = client.company.companyName
            ticketform_instance.maker = client
            ticketform_instance.updated_by = request.user
            ticketform_instance.updated_on = datetime.now()
            ticketform_instance.status = 'TP'
            ticketform_instance.save()
            CpyLog(ticketform_instance) 
            # # Get the ID of the inserted row
            # inserted_id = ticketform_instance.id
            # # Update the t_id field with the inserted ID
            # ticketform_instance.t_id = inserted_id
            # ticketform_instance.save()
            from django.contrib import messages
            messages.success(request, 'Ticket registered with ticket number : ' + str(ticketform_instance.ticket_no))
            return redirect('user_home') 
    
    return render(request, 'User/userRaiseTicket.html', {'form': ticketform})

 
@never_cache
@login_required(login_url="/cadmin/admin_login/")
def userHome(request,frmdate=None,todate=None,searchkey = None):

    cur_date = datetime.now()

    prev_date = cur_date - timedelta(days=30)
    
    tickets = None


    if(searchkey is None ):
        tickets = Tickets.objects.filter(Q(issued_on__range=(prev_date, cur_date ))).order_by('-updated_on')
        frmdate = prev_date.strftime('%Y-%m-%d')
        todate = cur_date.strftime('%Y-%m-%d')
        
    else:
    
        tickets = searchfilter(request.user,frmdate,todate,searchkey)


    inbox = tickets.filter((Q(status = 'TH') | Q(status = 'PA')) & Q( maker_id = request.user.id)).annotate(count = Count('ticket_no')).order_by('-issued_on') # inbox  count and ticket
    forwarded = tickets.exclude(Q(status='TH') | Q(status='PA') | Q(status='TC')).filter(maker_id=request.user.id).count()  # count for forwarded message
    
    print(forwarded)
    closed = tickets.filter(Q(status = 'TC') & Q(maker_id = request.user.id)).count() # closed tickets count

    return render(request,'User/userDashboard.html',{'tickets':inbox,'forwarded':forwarded,'closed':closed,'to_date':todate,'prev_date':frmdate,'keyword':searchkey})


@never_cache
@login_required(login_url="/cadmin/admin_login/")
def userSignout(request):
    logout(request)
    return redirect('admin_login')

import logging

# Use the logger to log messages
logger = logging.getLogger(__name__)
