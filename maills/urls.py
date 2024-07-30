from django.urls import path

from . import views

urlpatterns = [
    path('', views.UserView.as_view(), name='message-list'),
    path('attachments/<int:attachment_id>/', views.download_attachment, name='download_attachment'),
    path('messages/', views.MessageListView.as_view(), name='message-list'),

]