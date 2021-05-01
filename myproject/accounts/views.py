import sys, os
import json
import requests
from urllib.parse import urlparse
from subprocess import run, PIPE
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.core.files.base import ContentFile
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import AuthenticationForm

from .forms import SignUpForm

from captchaimages.models import Image
from captchaimages.forms import CaptchaForm


# Create your views here.
def signup(request):
    image = get_captcha_image(request)
    image_url = image.image.url

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        # captcha_form = CaptchaForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('boards:home')
    else:
        # request.method GET
        form = SignUpForm()
        if request.is_ajax():
            return JsonResponse({'image_url': image_url}, safe=False)
    return render(request, 'signup.html', {'form': form, 'image_url': image_url})


def login(request):
    image = get_captcha_image(request)
    image_url = image.image.url
    # request.session['remote_id'] = image.remote_id

    if request.method == 'POST':
        form = AuthenticationForm(request=request, data=request.POST, prefix="login")
        captcha_form = CaptchaForm(request.POST, prefix='captcha')

        if form.is_valid() and captcha_form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)

            answer = captcha_form.cleaned_data.get('captcha')
            remote_image_id = image.remote_id
            data = json.dumps({
                'answer': answer,
                'remote_image_id': remote_image_id
            })

            headers = {
                'Content-type': 'application/json',
                'Accept': 'text/plain'
            }
            try:
                response = requests.post('http://127.0.0.1:8000/api/check-answer/', data=data, headers=headers)
                response.raise_for_status()
                response_json = response.json()
                request.session['result'] = response_json['result']
            except requests.HTTPError as http_err:
                print(f'HTTP error occurred: {http_err}')
            except Exception as err:
                print(f'Other error occurred: {err}')

            result = request.session['result']

            if result == "Fail":
                messages.error(request, 'The captcha fields was not correct')
            elif user is not None and result == "Success":
                if user.is_active:
                    auth_login(request, user)
                    messages.info(request, f"You are now logged in as {username}")
                    return redirect('boards:home')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')

    # request.method == "GET"
    else:
        form = AuthenticationForm(prefix='login')
        # print(form.as_p())
        captcha_form = CaptchaForm(prefix='captcha')
        # print(captcha_form.as_p())
        if request.is_ajax():
            return JsonResponse({'image_url': image_url}, safe=False)

    context = {
        'form': form,
        'image_url': image.image.url,
        'captcha_form': captcha_form
    }
    return render(request, 'login.html', context)


def get_captcha_image(request):
    r = requests.get('http://127.0.0.1:8000/api/generate-image/')
    data_image = json.loads(json.dumps(r.json()))['data']
    remote_image_url = data_image['remote_url']
    remote_image_id = data_image['remote_id']

    # print(data['data'])
    image = Image(remote_id=remote_image_id)
    name = urlparse(remote_image_url).path.split('/')[-1]
    #
    with open(remote_image_url, 'rb') as f:
        image_data = f.read()
    image.image.save(name, ContentFile(image_data))

    return image

# def display_image(request):
#     if request.method == "GET":
#         image = get_captcha_image(request)
#         image_url = image.image.url
#         request.session['remote_id'] = image.remote_id
#
#         form = CaptchaForm()
#         if request.is_ajax():
#             return JsonResponse({'image_url': image_url}, safe=False)
#         context = {
#             'image_url': image_url,
#             'form': form,
#         }
#         return render(request, 'includes/captcha.html', context)
#
#     if request.method == "POST":
#         form = CaptchaForm(data=request.POST)
#         if form.is_valid():
#             response = form.cleaned_data.get('captcha')
#             remote_image_id = request.session['remote_id']
#
#             data = json.dumps({
#                 'response': response,
#                 'remote_image_id': remote_image_id,
#             })
#             # print(data)
#             headers = {
#                 'Content-type': 'application/json',
#                 'Accept': 'text/plain'
#             }
#
#             try:
#                 response = requests.post('http://127.0.0.1:8000/check-answer/', data=data, headers=headers)
#                 response.raise_for_status()
#                 response_json = response.json()
#                 result = response_json['result']
#                 print(result)
#
#             except requests.HTTPError as http_err:
#                 print(f'HTTP error occurred: {http_err}')
#             except Exception as err:
#                 print(f'Other error occurred: {err}')
#
#         return redirect('captchaimages:display')
