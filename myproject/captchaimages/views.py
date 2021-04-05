from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse

import json
import requests

import sys
import bcrypt
from urllib.parse import urlparse
from subprocess import run, PIPE
from django.core.files.base import ContentFile

from .models import Image
from .forms import CaptchaForm


def home(request):
    return render(request, "base.html")


def upload(request):
    r = requests.get('http://127.0.0.1:8000/data/')
    data = json.loads(json.dumps(r.json()))['data']
    remote_image_url = data['remote_url']
    remote_image_id = data['remote_id']

    # print(data['data'])

    image = Image(remote_id=remote_image_id)
    name = urlparse(remote_image_url).path.split('/')[-1]

    with open(remote_image_url, 'rb') as f:
        image_data = f.read()
    image.image.save(name, ContentFile(image_data))

    return JsonResponse(r.json())


# def display(request):
#     image = upload(request)
#     image_url = image.image.url
#     hashed_captcha = image.text
#     print(hashed_captcha.encode())
#
#     if request.method == "GET":
#         form = CaptchaForm()
#         if request.is_ajax():
#             return JsonResponse({'image_url': image_url}, safe=False)
#         context = {
#             'image_url': image_url,
#             'form': form,
#         }
#         return render(request, 'includes/captcha.html', context)
#     if request.method == "POST":
#         form = CaptchaForm(data=request.POST)
#         if form.is_valid():
#             captcha_text = form.cleaned_data.get('captcha')
#             if bcrypt.checkpw(captcha_text.encode(), image.text.encode()):
#                 print("match")
#             else:
#                 print(captcha_text.encode(), image.text.encode())
#         return redirect('captchaimages:display')
#
#     return redirect('captchaimages:display')
