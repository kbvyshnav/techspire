from django.urls import path,include
from .views import *

urlpatterns = [

    path('user_login/',userLogin,name='user_login'),
    path('user_signout/',userSignout,name='user_signout'),

    path('sub_user_home/',userHome,name='sub_user_home'),
    path('sub_user_home/<frmdate>/<todate>/',userHome,name='sub_user_home'),
    path('sub_user_home/<frmdate>/<todate>/<searchkey>/',userHome,name='sub_user_home'),


    path('sub_user_approved/',sUserApproved,name='sub_user_approved'),
    path('sub_user_approved/<frmdate>/<todate>/',sUserApproved,name='sub_user_approved'),
    path('sub_user_approved/<frmdate>/<todate>/<searchkey>/',sUserApproved,name='sub_user_approved'),

    path('sub_user_rejected/',sUserRejected,name='sub_user_rejected'),
    path('sub_user_rejected/<frmdate>/<todate>/',sUserRejected,name='sub_user_rejected'),
    path('sub_user_rejected/<frmdate>/<todate>/<searchkey>/',sUserRejected ,name ='sub_user_rejected'),


    path('sub_user_closed/',sUserClosed,name='sub_user_closed'),
    path('sub_user_closed/<frmdate>/<todate>/',sUserClosed,name='sub_user_closed'),
    path('sub_user_closed/<frmdate>/<todate>/<searchkey>/',sUserClosed,name='sub_user_closed'),

    path('sub_raise_ticket/',sUserRaiseTicket,name='sub_raise_ticket'),
    path('pendings/',userPendingsDashboard,name='dashboard_pendings'),
    path('del_ticket/<int:ticketid>/',deleteTicket,name='delete_ticket'), 
    path('useractive/',userActiveDashboard,name='active_user_tickets'),
    path('sub_usr_ops/',usrInbox,name='sub_usr_ops'),
    path('usrsrch/',usersearch,name ='usersearch'),
]