from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse

import sys
from urllib.parse import urlparse
from subprocess import run, PIPE
from django.core.files.base import ContentFile

from .models import Image


def home(request):
    return render(request, "base.html")


def upload(request):
    out = run([sys.executable, '//home//hanh//Desktop//captcha//mass_captcha//generate_mass_captcha.py'], shell=False,
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


def display(request):
    image = upload(request)
    image_url = image.image.url

    if request.method == "GET":
        if request.is_ajax():
            return JsonResponse({'image_url': image_url}, safe=False)
        else:
            context = {
                'image_url': image_url
            }
            return render(request, 'includes/captcha.html', context)

