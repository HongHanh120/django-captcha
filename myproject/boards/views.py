from django.shortcuts import render, redirect
from django.http import HttpResponse

import sys
from urllib.parse import urlparse
from subprocess import run, PIPE
from django.core.files.base import ContentFile

from .models import Image


def home(request):
    return render(request, "base.html")


def external(request):
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

    if request.method == 'GET':
        image = Image.objects.get(text=text)

    return render(request, 'base.html', {'image': image})

