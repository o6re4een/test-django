def set_user_session(request, form):
    request.session['email'] = form.cleaned_data['email']
    request.session['password'] = form.cleaned_data['password']
    request.session['email_type'] = form.cleaned_data['type']
    