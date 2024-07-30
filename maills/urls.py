from django.urls import path

from . import views

urlpatterns = [
    # path('', views.UserView.as_view(), name='message-list'),
    path('messages/<int:email_id>/', views.message_list_view, name='view_messages'),
    path('attachments/<int:attachment_id>/', views.download_attachment, name='download_attachment'),
    path('', views.email_list_view, name='emails_list'),
    path('update-session/', views.update_session, name='update_session'),
    path('add-email/', views.add_email, name='add_email'),

]