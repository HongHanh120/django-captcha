import sys
from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth import authenticate
from django.template import RequestContext
from urllib.parse import urlparse
from subprocess import run, PIPE
from django.core.files.base import ContentFile

from .forms import SignUpForm
from .models import Image


# Create your views here.
def signup(request):
    image = upload_image(request)
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('boards:home')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form, 'image': image})


def login(request):
    image = upload_image(request)
    username = password = ''
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                auth_login(request, user)
                return redirect('boards:home')
    return render(request, 'login.html', {'username': username, 'image': image})


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

    return image

# def display_image(request):
#     if request.method == 'GET':
#         image = upload_image(request)
#     return render(request, 'includes/captcha.html', {'image': image})
