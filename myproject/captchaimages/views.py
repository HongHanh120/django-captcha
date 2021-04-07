import json
import requests
from django.shortcuts import render, redirect
from django.http import JsonResponse
from urllib.parse import urlparse
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

    return image


def display(request):
    if request.method == "GET":
        image = upload(request)
        image_url = image.image.url
        request.session['remote_id'] = image.remote_id
        form = CaptchaForm()
        if request.is_ajax():
            return JsonResponse({'image_url': image_url}, safe=False)
        context = {
            'image_url': image_url,
            'form': form,
        }
        return render(request, 'includes/captcha.html', context)

    if request.method == "POST":
        form = CaptchaForm(data=request.POST)
        if form.is_valid():
            response = form.cleaned_data.get('captcha')
            remote_image_id = request.session['remote_id']

            data = json.dumps({
                'response': response,
                'remote_image_id': remote_image_id,
            })
            print(data)

            headers = {
                'Content-type': 'application/json',
                'Accept': 'text/plain'
            }

            try:
                response = requests.post('http://127.0.0.1:8000/check/', data=data, headers=headers)
                response.raise_for_status()
                response_json = response.json()
                print(response_json)

            except requests.HTTPError as http_err:
                print(f'HTTP error occurred: {http_err}')
            except Exception as err:
                print(f'Other error occurred: {err}')
            else:
                print('Success!')

            # return JsonResponse({'data': data}, safe=False)
        return redirect('captchaimages:display')
