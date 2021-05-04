import json
import base64
from urllib.parse import urlparse

import requests
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from django.core.files.base import ContentFile
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect

from captchaimages.forms import CaptchaForm
from captchaimages.models import Image
from .forms import SignUpForm


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
    if request.method == "GET":
        # image = get_captcha_image(request)
        # image_url = image.image.url
        data = get_captcha_image(request)
        image = data['image']

        # request.session['remote_id'] = image.remote_id
        # request.session['image_url'] = image_url
        request.session['remote_id'] = data['image_id']

        form = AuthenticationForm(prefix='login')
        captcha_form = CaptchaForm(prefix='captcha')

        if request.is_ajax():
            return JsonResponse({'image': image}, safe=False)

    else:
        form = AuthenticationForm(request=request, data=request.POST, prefix="login")
        captcha_form = CaptchaForm(request.POST or None, prefix='captcha')

        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            if captcha_form.is_valid():
                answer = captcha_form.cleaned_data['captcha']
                remote_image_id = request.session['remote_id']
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
                print(result)

                user = authenticate(request, username=username, password=password)
                if user is not None:
                    if user.is_active:
                        if result == "Success":
                            auth_login(request, user)
                            # messages.success(request, "Login successful")
                            return HttpResponse(f"You are now logged in as {username}")
                        else:
                            captcha_form.add_error('captcha', 'Please enter the correct captcha')
                            # captcha_form = CaptchaForm(prefix='captcha')
                else:
                    captcha_form = CaptchaForm(prefix='captcha')
            else:
                captcha_form = CaptchaForm(prefix='captcha')

        # image = get_captcha_image(request)
        # image_url = image.image.url
        # request.session['remote_id'] = image.remote_id
        # request.session['image_url'] = image_url
        data = get_captcha_image(request)
        image = data['image']
        request.session['remote_id'] = data['image_id']

    context = {
        # 'form': form,
        # 'captcha_form': captcha_form,
        # 'image_url': request.session['image_url'],
        'image': image,
        'form': form,
        'captcha_form': captcha_form,
    }
    return render(request, 'login.html', context)


def get_captcha_image(request):
    r = requests.get('http://127.0.0.1:8000/api/generate-image/')
    data_image = json.loads(json.dumps(r.json()))['data']
    remote_image_url = data_image['remote_url']
    remote_image_id = data_image['remote_id']

    # image = Image(remote_id=remote_image_id)
    # name = urlparse(remote_image_url).path.split('/')[-1]

    with open(remote_image_url, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
        # image_data = f.read()
    # image.image.save(name, ContentFile(image_data))

    data = {
        'image': image_data,
        'image_id': remote_image_id
    }

    return data
