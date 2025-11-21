from django.urls import path,include
from .views import *

urlpatterns = [ path('chtbx/<ticket_no>/',chatpop,name = 'chtbx'),
                 path('chtbx/<ticket_no>/<flag>/',chatpop,name = 'chtbx'),
                path('chtbx/',sndMsg,name = 'send_msg'),
                path('chtbxusr/<ticket_no>/',chatpopuser,name = 'chtbxusr'),
                path('chtbxusr/<ticket_no>/<flag>/',chatpopuser,name = 'chtbxusr'),
                path('chtbxusr/',sndUsrMsg,name = 'send_msg_usr'),
              
]