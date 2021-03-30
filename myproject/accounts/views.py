import sys
import json
from urllib.parse import urlparse
from subprocess import run, PIPE
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.core.files.base import ContentFile
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import AuthenticationForm

from .forms import SignUpForm
from .models import Image


# Create your views here.
def signup(request):
    image = upload_image(request)
    image_url = image.image.url

    if request.method == "GET":
        if request.is_ajax():
            return JsonResponse({'image_url': image_url}, safe=False)

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('boards:home')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form, 'image_url': image_url})


def login(request):
    image = upload_image(request)
    image_url = image.image.url

    if request.method == "GET":
        if request.is_ajax():
            return JsonResponse({'image_url': image_url}, safe=False)

    if request.method == 'POST':
        form = AuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.is_active:
                    auth_login(request, user)
                    messages.info(request, f"You are now logged in as {username}")
                    return redirect('boards:home')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form, 'image_url': image.image.url})


def upload_image(request):
    out = run([sys.executable, '//home//hanh//Desktop//captcha//mass_captcha//generate_mass_captcha.py'],
              shell=False,
              stdout=PIPE)

    data = "".join(map(chr, out.stdout)).split('\n')
    for obj in data:
        if obj == '':
            data.remove(obj)

    text = data[0]
    remote_image_url = data[1]

    image = Image(text=text)
    name = urlparse(remote_image_url).path.split('/')[-1]

    with open(remote_image_url, 'rb') as f:
        image_data = f.read()
    image.image.save(name, ContentFile(image_data))

    return image


# def display_image(request):
#     image = upload_image(request)
#     image_url = image.image.url
#
#     if request.method == "GET":
#         if request.is_ajax():
#             return JsonResponse({'image_url': image_url}, safe=False)
#         else:
#             context = {
#                 'image_url': image_url
#             }
#             return render(request, 'includes/captcha.html', context)
