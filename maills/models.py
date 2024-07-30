from django.db import models

# Create your models here.
from django.db import models


class File(models.Model):
    
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    path = models.CharField(max_length=255)
    message = models.ForeignKey(
        "Message",
        on_delete=models.CASCADE,
        related_name='attachments',
        null=True
    )

    def __str__(self):
        return self.name
       

class Email(models.Model):
    id = models.AutoField(primary_key=True)
    email = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    type = models.CharField(max_length=255, default="gmail.com", null=False)
    
    messages = models.ManyToManyField('Message',  default=1)

    def __str__(self):
        return self.email
    
 
class Message(models.Model):
    id = models.AutoField(primary_key=True)
    message_id = models.CharField(max_length=255)
    heading = models.CharField(max_length=255)
    date_sent = models.DateTimeField(null=True)
    date_got = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    

   

    def __str__(self):
        return self.heading
    
    def short_content(self):
        return self.content[:50]
   