from django.urls import path,include
from .views import *

urlpatterns = [

    path('user_login/',userLogin,name='user_login'),
    path('user_signout/',userSignout,name='user_signout'),

    path('user_home/',userHome,name='user_home'),
    path('user_home/<frmdate>/<todate>/',userHome,name='user_home'),
    path('user_home/<frmdate>/<todate>/<searchkey>/',userHome,name='user_home'),


    path('user_inprogress/',userInProgress,name='user_inprogress'),
    path('user_inprogress/<frmdate>/<todate>/',userInProgress,name='user_inprogress'),
    path('user_inprogress/<frmdate>/<todate>/<searchkey>/',userInProgress,name='user_inprogress'),

    path('user_inqueue/',subQueryDashboard,name='user_inqueue'),
    path('user_inqueue/<frmdate>/<todate>/',subQueryDashboard,name='user_inqueue'),
    path('user_inqueue/<frmdate>/<todate>/<searchkey>/',subQueryDashboard,name='user_inqueue'),
 
    path('user_closed/',userClosed,name='user_closed'),
    path('user_closed/<frmdate>/<todate>/',userClosed,name='user_closed'),
    path('user_closed/<frmdate>/<todate>/<searchkey>/',userClosed,name='user_closed'),
    path('subusr_is_active/<item_id>/',update_is_active,name='subusr_is_active'),

    path('maker_management' ,subUserManagement , name = 'sub_user_management' ),
    path('rejected_tickets' ,rejectedTickets , name = 'rejected_tickets' ),
    path('subUserEdit/<usr_id>/',subUserEdit, name = 'subUserEdit'),
    path('addSubUser/',addSubUser, name = 'add_sub_user'),
    path('sub_user_add' , subUserEdit , name = 'sub_user_add'),
    path('raise_ticket/',raiseTicket,name='raise_ticket'),
    # path('pendings/',userPendingsDashboard,name='dashboard_pendings'),
    path('del_ticket/<int:ticketid>/',deleteTicket,name='delete_ticket'), 
    path('useractive/',userActiveDashboard,name='active_user_tickets'),
    path('usr_ops/',usrInbox,name='usr_ops'),
    path('usrsrchs/',usersearch,name ='usersrch'),
]