
from django import forms

class EmailForm(forms.Form):
    email = forms.CharField(max_length=255, label="email") 
    password = forms.CharField(max_length=255, label="password")
    type = forms.ChoiceField(choices=(("gmail.com", "gmail.com"), ("mail.ru", "mail.ru"), ("yandex.ru", "yandex.ru")))