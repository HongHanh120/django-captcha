import base64
import json
import requests
from datetime import datetime
from django.shortcuts import render, redirect
from django.http import JsonResponse
from urllib.parse import urlparse
from django.core.files.base import ContentFile

from .forms import CaptchaForm


def home(request):
    return render(request, "base.html")


# def get_captcha_image(request):
#     r = requests.get('http://127.0.0.1:8000/api/generate-image/')
#     data = json.loads(json.dumps(r.json()))['data']
#     remote_image_url = data['remote_url']
#     remote_image_id = data['remote_id']
#
#     # print(data['data'])
#     # image = Image(remote_id=remote_image_id)
#     name = urlparse(remote_image_url).path.split('/')[-1]
#
#     with open(remote_image_url, 'rb') as f:
#         # image_data = base64.b64encode(f.read()).decode('utf-8')
#         image_data = f.read()
#     image = Image()
#     image.image.save(name, ContentFile(image_data))
#
#     data = {
#         # 'image': image_data,
#         'image': image,
#         'image_id': remote_image_id
#     }
#
#     return data
#
#
# def display_image(request):
#     if request.method == "GET":
#         data = get_captcha_image(request)
#         image = data['image']
#         image_url = image.image.url
#         print(image_url)
#         request.session['remote_id'] = data["image_id"]
#
#         form = CaptchaForm()
#
#         if request.is_ajax():
#             return JsonResponse({'image_url': image_url}, safe=False)
#         context = {
#             # 'image': image,
#             'image_url': image_url,
#             'form': form,
#         }
#         return render(request, 'test.html', context)
#
#     if request.method == "POST":
#         form = CaptchaForm(data=request.POST)
#         if form.is_valid():
#             answer = form.cleaned_data.get('captcha')
#             remote_image_id = request.session['remote_id']
#
#             data = json.dumps({
#                 'answer': answer,
#                 'remote_image_id': remote_image_id,
#             })
#             # print(data)
#             headers = {
#                 'Content-type': 'application/json',
#                 'Accept': 'text/plain'
#             }
#
#             try:
#                 response = requests.post('http://127.0.0.1:8000/api/check-answer/', data=data, headers=headers)
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


def get_captcha_image(request):
    # r = requests.get('http://127.0.0.1:8000/api/generate-image/')

    try:
        r = requests.get('http://127.0.0.1:8000/api/generate-image/')
        request.session['response'] = r
        print(r.json())
    except requests.HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')
    response = request.session.get('response')
    if response is not None:
        data_image = json.loads(json.dumps(response.json())).get('data')
        image_url = data_image['remote_url']
        # print(image_url)
        remote_image_id = data_image['remote_id']
    else:
        image_url = '/home/hanh/Desktop/myproject/myproject/static/img/error-symbol.png'
        remote_image_id = None

    # data = json.loads(json.dumps(r.json()))['data']
    # remote_image_url = data['remote_url']
    # remote_image_id = data['remote_id']

    # print(data['data'])
    # image = Image(remote_id=remote_image_id)
    # name = urlparse(remote_image_url).path.split('/')[-1]

    with open(image_url, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
        # image_data = f.read()
    # image = Image()
    # image.image.save(name, ContentFile(image_data))

    data = {
        'image': image_data,
        # 'image': image,
        'image_id': remote_image_id
    }

    return data


def display_image(request):
    if request.method == "GET":
        data = get_captcha_image(request)
        image = data['image']
        # image_url = image.image.url
        # print(image_url)
        request.session['remote_id'] = data["image_id"]

        form = CaptchaForm()

        if request.is_ajax():
            return JsonResponse({'image': image}, safe=False)
        context = {
            'image': image,
            'form': form,
        }
        return render(request, 'test.html', context)

    if request.method == "POST":
        form = CaptchaForm(data=request.POST)
        if form.is_valid():
            answer = form.cleaned_data.get('captcha')
            remote_image_id = request.session['remote_id']

            data = json.dumps({
                'answer': answer,
                'remote_image_id': remote_image_id,
            })
            # print(data)
            headers = {
                'Content-type': 'application/json',
                'Accept': 'text/plain'
            }

            try:
                response = requests.post('http://127.0.0.1:8000/api/validate-captcha/', data=data, headers=headers)
                response.raise_for_status()
                response_json = response.json()
                # result = response_json['response']
                print(response_json)

            except requests.HTTPError as http_err:
                print(f'HTTP error occurred: {http_err}')
            except Exception as err:
                print(f'Other error occurred: {err}')

        return redirect('captchaimages:display')
