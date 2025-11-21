from django.urls import path,include
from .views import *

urlpatterns = [
    path('dev_login',devLogin,name='dev_login'),
    path('dev_signout/',dev_signout,name='dev_signout'),
    
    path('dev_accept/<ticketId>/<date>/',devAccept,name = 'dev_accepted'),

    
    path('dev_home/',dev_home,name='dev_home'),
    path('dev_home/<cmpnyId>/<frmdate>/<todate>/',dev_home,name='dev_home'),
    path('dev_home/<cmpnyId>/<frmdate>/<todate>/<searchkey>/',dev_home,name='dev_home'),


    path('dev_pendings/',devPendingsDashboard,name='dev_pendings'),
    path('dev_pendings/<cmpnyId>/<frmdate>/<todate>/',devPendingsDashboard,name='dev_pendings'),
    path('dev_pendings/<cmpnyId>/<frmdate>/<todate>/<searchkey>/',devPendingsDashboard,name='dev_pendings'),
      
    path('dev_forwarded/',devForwarded,name='dev_forwarded'),
    path('dev_forwarded/<cmpnyId>/<frmdate>/<todate>/',devForwarded,name='dev_forwarded'),
    path('dev_forwarded/<cmpnyId>/<frmdate>/<todate>/<searchkey>/',devForwarded,name='dev_forwarded'),



    path('dev_closed/',devClosed,name='dev_closed'),
    path('dev_closed/<cmpnyId>/<frmdate>/<todate>/',devClosed,name='dev_closed'),
    path('dev_closed/<cmpnyId>/<frmdate>/<todate>/<searchkey>/',devClosed,name='dev_closed'),

    path('tester_home/',tester_home,name='tester_home'),
    path('tester_home/<cmpnyId>/<frmdate>/<todate>/',tester_home,name='tester_home'),
    path('tester_home/<cmpnyId>/<frmdate>/<todate>/<searchkey>/',tester_home,name='tester_home'),

    path('tester_penidngs/',testerPendings,name='tester_pendings'),
    path('tester_penidngs/<cmpnyId>/<frmdate>/<todate>/',testerPendings,name='tester_pendings'),
    path('tester_penidngs/<cmpnyId>/<frmdate>/<todate>/<searchkey>/',testerPendings,name='tester_pendings'),

    path('tester_forwarded/',testerForwarded,name='tester_forwarded'),
    path('tester_forwarded/<cmpnyId>/<frmdate>/<todate>/',testerForwarded,name='tester_forwarded'),
    path('tester_forwarded/<cmpnyId>/<frmdate>/<todate>/<searchkey>/',testerForwarded,name='tester_forwarded'),

    path('tester_closed/',testerClosed,name='tester_closed'),
    path('tester_closed/<cmpnyId>/<frmdate>/<todate>',testerClosed,name='tester_closed'),
    path('tester_closed/<cmpnyId>/<frmdate>/<todate>/<searchkey>/',testerClosed,name='tester_closed'),


    path('assign_tester/<testerid>/<ticketId>/',assignTester,name='assign_tester'),
    path('tester_forwarded/',testerForwarded,name='tester_forwarded'),
    
    
    path('tstropen/',testerAccept,name='tester_open'),
    # path('tstropen/<tno>',testerAccept,name='tester_open'),
    path('tstrpsh/',testerPush,name='tester_push'),
    path('dev_ops/',devOperations,name='dev_ops'),
    path('dev_ops/<ticket_id>/<status>/<tester_id>/<exp>/<remarks>',devOperations,name='dev_ops'),
    path('tstr_qry/',testerQry,name='tstrqry'),
    path('devsearch/',devSearch , name= 'dev_search'),
    #path('useractive/',userActiveDashboard,name='active_user_tickets'),
]