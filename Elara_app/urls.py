from django.urls import path
from . import views

urlpatterns = [
    path('', views.UserFunctions.index, name='index'),
    path('index', views.UserFunctions.index, name='index'),
    path('login', views.UserFunctions.login, name='login'),
    path('signup', views.UserFunctions.signup, name='signup'),
    path('logout', views.UserFunctions.logout, name='logout'),
    path('login_user', views.UserFunctions.login_user, name='login_user'),
    path('signup_user', views.UserFunctions.signup_user, name='signup_user'),
    path('verify_otp', views.UserFunctions.verify_otp, name='verify_otp'),

    path('chat', views.ChatFunctions.chat_with_document, name='chat'),
    path('getChatList', views.ChatFunctions.get_all_files, name='get_all_files'),
    path('uploadFile', views.ChatFunctions.upload_file, name='upload_file'),
    path('uploadFolder', views.ChatFunctions.upload_folder, name='upload_folder'),
    path('showfilesinfolder',views.ChatFunctions.get_all_files_in_folder, name='get_all_files_in_folder'),
    path('createIndex', views.ChatFunctions.create_index, name='create_index'),
    path('clearConversation', views.ChatFunctions.clear_conversation, name='clear_conversation'),
    path('chatHistory', views.ChatFunctions.get_chat_history, name='get_chat_history'),
]
