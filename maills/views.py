import os
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render

from maills.forms import EmailForm
from maills.models import Email, File
from django.views.generic import TemplateView

from maills.utils.session import set_user_session


class UserView(TemplateView):
    template_name = 'maills/user.html'

    def post(self, request, *args, **kwargs):
        form = EmailForm(request.POST)

        if form.is_valid():
            print(form.cleaned_data)
            is_email_exists = Email.objects.filter(email=form.cleaned_data['email']).exists()
            if(is_email_exists):
                set_user_session(request, form)
                return redirect('message-list')
            else:
                email = Email(email=form.cleaned_data['email'], password=form.cleaned_data['password'], type=form.cleaned_data['type'])
                email.save()
                set_user_session(request, form)
                return redirect('message-list')
        else:
            print(form.errors)
            return HttpResponseRedirect('user')
    def get(self, request, *args, **kwargs):
        return render(request, 'maills/user.html', {'form': EmailForm()})

        

class MessageListView(TemplateView):
    template_name = 'maills/message-list.html'

    def get_context_data(self, **kwargs):
        
       
        context = super().get_context_data(**kwargs)
        email = self.request.session.get('email')
        email_type = self.request.session.get('email_type')
        print("EMAIL: ", email, "TYPE: ", email_type)
        found_email = Email.objects.filter(email=email, type=email_type)

        messages = found_email.get().messages.all().prefetch_related('attachments')
        context['messages'] = messages

        context['email'] = email
        context['email_type'] = email_type
        return context
    
    
    
def download_attachment(request, attachment_id):
    # # Fetch the attachment record from the database
    # try:
    #     attachment = File.objects.get(id=attachment_id)
    # except File.DoesNotExist:
    #     raise Http404("Attachment does not exist")

    # # File path
    # file_path = attachment.path

    # # Check if the file exists
    # if not os.path.exists(file_path):
    #     raise Http404("File not found")

    # # Open and serve the file
    # with open(file_path, 'rb') as file:
    #     response = HttpResponse(file.read(), content_type='application/octet-stream')
    #     response['Content-Disposition'] = f'attachment; filename={attachment.name}'
    #     return response
    attachment = get_object_or_404(File, id=attachment_id)
    file_path = attachment.path

    try:
        with open(file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type="application/octet-stream")
            response['Content-Disposition'] = f'attachment; filename="{attachment.name}"'
            return response
    except FileNotFoundError:
        raise Http404("Attachment not found")