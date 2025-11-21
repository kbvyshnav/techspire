from django.shortcuts import render,redirect
from .models import tcktChat
from cAdmin.models import TicketLogs,Tickets
from django.db.models import F
from itertools import chain
from django.views.decorators.cache import never_cache




@never_cache
def chatpop(request,ticket_no,flag=None): #inuse main 
    print('Flag',flag,ticket_no)
    messages = tcktChat.objects.filter(ticket_no = ticket_no)
    for message in messages:
        if request.user.role in message.seen:
            message.seen = message.seen.replace(request.user.role, '')
            message.save()
    logs = TicketLogs.objects.filter(ticket_no=ticket_no)
    combined_queryset = list(chain(messages, logs))
    ticket = Tickets.objects.get(ticket_no =ticket_no)
    sorted_combined_queryset = sorted(combined_queryset, key=lambda x: x.updated_on)
    context = {'ticket' :ticket,'messages': sorted_combined_queryset,'flag':flag}
    return render(request,'chatf.html',context)

import threading
from django.core.mail import send_mail 
class EmailThread(threading.Thread):
    def __init__(self, subject, message, recipient_list):
        self.subject = subject
        self.message = message
        self.recipient_list = recipient_list
        threading.Thread.__init__(self)

    def run(self):
        send_mail(self.subject, self.message, "info@tweedle.co.in", self.recipient_list, fail_silently=False)


@never_cache
def sndMsg(request):
    print('*************',request.POST)
    content = None
    tckt_val = Tickets.objects.get(ticket_no = request.POST.get('ticke  t_no'))
    if request.method == 'POST': 
        userType = request.user.role
        flag = None
        if userType == 'A':
            flag = 'UDT'
        elif userType == 'U':
            flag = 'ADT'
        elif userType == 'T':
            flag = 'ADU'
        elif userType == 'D':
            flag = 'AUT'

    subject = f"Tweedle Update on Ticket #{request.POST['ticket_no']} SUB: { tckt_val.subject }"
    email_body = f"""
    Dear Client,

    An important message has been added by the admin in the chat section of your ticket.

    🔹 Ticket ID: {request.POST['ticket_no']}

    📩 New Message:
    "{request.POST['msg']}"

    Please log in to your account to review and respond as needed.

    Best Regards,
    Tweedle Support Team
    """     
    print(tckt_val.maker.email)

    if request.POST.get('email') == 'on':
        EmailThread( subject , email_body , [tckt_val.maker.email]).start()

    tckt_msg = tcktChat.objects.create(user_id = request.user , msg = request.POST['msg'] , ticket_no = request.POST['ticket_no'],atchmnt = request.FILES.get("file-input",None), seen = flag)
    messages = tcktChat.objects.filter(ticket_no = request.POST['ticket_no'])
    context = {'ticket_no':request.POST['ticket_no'],'messages': messages}    
    return redirect('chtbx',ticket_no = request.POST['ticket_no'] )


@never_cache
def chatpopuser(request,ticket_no,flag=None): # this flag's purpose is to let to know if it's close page
    print('Flag',flag,ticket_no)
    messages = tcktChat.objects.filter(ticket_no = ticket_no)
    logs = TicketLogs.objects.filter(ticket_no=ticket_no)
    combined_queryset = list(chain(messages, logs))
    print(combined_queryset)
    sorted_combined_queryset = sorted(combined_queryset, key=lambda x: x.updated_on)
    print('sorted,',sorted_combined_queryset)
    context = {'ticket_no' :ticket_no,'messages': sorted_combined_queryset,'flag':flag}
    return render(request,'chat-client.html',context)

@never_cache
def sndUsrMsg(request):
    if request.method == 'POST': 
        tckt_msg = tcktChat.objects.create(user_id = request.user , msg = request.POST['msg'] , ticket_no = request.POST['ticket_no'] )
        messages = tcktChat.objects.filter(ticket_no = request.POST['ticket_no'])
        print(request.POST)
        context = {'ticket_no':request.POST['ticket_no'],'messages': messages}    
        return redirect('chtbx',ticket_no = request.POST['ticket_no'] )
        

        