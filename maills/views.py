import json
import os
from django.http import Http404, HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt

from maills.forms import EmailForm
from maills.models import Email, File
from django.views.generic import TemplateView
from django.contrib import messages

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

        

def message_list_view(request, email_id):
    email = get_object_or_404(Email, id=email_id)
    messages = email.messages.all().prefetch_related('attachments')
    return render(request, 'maills/message_list.html', {'email': email, 'messages': messages, 'email_type': email.type})
    
def download_attachment(request, attachment_id):
    attachment = get_object_or_404(File, id=attachment_id)
    file_path = attachment.path

    try:
        with open(file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type="application/octet-stream")
            response['Content-Disposition'] = f'attachment; filename="{attachment.name}"'
            return response
    except FileNotFoundError:
        raise Http404("Attachment not found")
    

@csrf_exempt
def update_session(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email_type = data.get('email_type')

            # Check if email_type is valid
            if email_type:
                # Update the session with the new email type
                request.session['email_type'] = email_type
                # Retrieve the current email based on the updated email_type
                email = request.session.get('email')

                if Email.objects.filter(email=email, type=email_type).exists():
                    return JsonResponse({'success': True, 'email': email, 'email_type': email_type})
                else:
                    return JsonResponse({'success': False, 'error': 'Email not found for this type'})

            return JsonResponse({'success': False, 'error': 'Invalid email type'})
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
def add_email(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            email_type = data.get('email_type')
            email_password = data.get('password')

            if email and email_type:
                # Create or get email entry
                email_obj, created = Email.objects.get_or_create(email=email, type=email_type, password=email_password)
                # Update session with the new email
                request.session['email'] = email
                request.session['email_type'] = email_type
                if created:
                    return JsonResponse({'success': True})
                else:
                    return JsonResponse({'success': False, 'error': 'Email already exists'})

            return JsonResponse({'success': False, 'error': 'Invalid input'})
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def email_list_view(request):
    emails = Email.objects.all()
    return render(request, 'maills/emails_list.html', {'emails': emails})