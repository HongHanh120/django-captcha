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
    context = upload_image(request)
    image_url = context['image_url']
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
    context = upload_image(request)
    dataJSON = context['data']
    image_url = context['image_url']
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

    return render(request, 'login.html', {'form': form, 'image_url': image_url, 'data': dataJSON})


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

    if request.method == 'GET':
        image = Image.objects.get(text=text)

    image_url = image.image.url
    data = {
        'url': image_url
    }
    dataJSON = json.dumps(data)

    context = {
        'data': dataJSON,
        'image_url': image_url,
        'name': name,
    }
    return context


def display_image(request):
    context = upload_image(request)
    image_url = context['image_url']
    # print(image_url)
    name = context['name']
    data = {
        'url': image_url,
        'name': name,
    }
    dataJSON = json.dumps(data)

    return render(request, 'includes/captcha.html', {'data': dataJSON, 'image_url': image_url})
