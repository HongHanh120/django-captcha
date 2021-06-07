import json
import base64
import requests
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect

from captchaimages.forms import CaptchaForm
from .forms import SignUpForm


def get_captcha_image(request):
    # Yêu cầu sinh ảnh CAPTCHA là lấy dữ liệu thông qua API '/api/generate-image/'
    try:
        r = requests.get('http://127.0.0.1:8000/api/generate-image/')
        data_image = json.loads(json.dumps(r.json()))['data']
        image_url = data_image['remote_url']
        remote_image_id = data_image['remote_id']
        with open(image_url, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')

        data = {
            'image': image_data,
            'image_id': remote_image_id
        }
        return data
    except requests.HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')

        image_url = '/home/hanh/Desktop/myproject/myproject/static/img/error-symbol.png'
        remote_image_id = None

        with open(image_url, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')

        data = {
            'image': image_data,
            'image_id': remote_image_id
        }
        return data


# def signup(request):
#     image = get_captcha_image(request)
#     image_url = image.image.url
#
#     if request.method == 'POST':
#         form = SignUpForm(request.POST)
#         # captcha_form = CaptchaForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             auth_login(request, user)
#             return redirect('boards:home')
#     else:
#         # request.method GET
#         form = SignUpForm()
#         if request.is_ajax():
#             return JsonResponse({'image_url': image_url}, safe=False)
#     return render(request, 'signup.html', {'form': form, 'image_url': image_url})


def login(request):
    if request.method == "GET":
        data = get_captcha_image(request)
        image = data.get('image')
        request.session['remote_id'] = data.get('image_id')

        form = AuthenticationForm(prefix='login')
        captcha_form = CaptchaForm(prefix='captcha')

        error_image_url = '/home/hanh/Desktop/myproject/myproject/static/img/error-symbol.png'
        with open(error_image_url, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        if image_data == image:
            messages.error(request, 'The captcha webservice is not active. Please come in another time')

        if request.is_ajax():
            return JsonResponse({'image': image}, safe=False)

    else:
        form = AuthenticationForm(request=request, data=request.POST, prefix="login")
        captcha_form = CaptchaForm(request.POST or None, prefix='captcha')

        if form.is_valid() and captcha_form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            answer = captcha_form.cleaned_data.get('captcha')
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
                response = requests.post('http://127.0.0.1:8000/api/validate-captcha/', data=data, headers=headers)
                response.raise_for_status()
                response_json = response.json()['response']

                request.session['result'] = response_json['result']
                request.session['error_code'] = response_json.get('error_code')
            except requests.HTTPError as http_err:
                print(f'HTTP error occurred: {http_err}')
            except Exception as err:
                print(f'Other error occurred: {err}')

            result = request.session.get('result')
            error_code = request.session.get('error_code')

            if result == 'fail' and error_code == 'missing_input_answer':
                return HttpResponse('The answer parameter is missing')
            elif result == 'fail' and error_code == 'missing_input_remote_image_id':
                return HttpResponse('The remote_image_id parameter is missing')
            elif result == 'fail' and error_code == 'invalid_input_remote_image_id':
                return HttpResponse('The remote_image_id parameter is invalid')

            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.is_active:
                    if result == "success" and error_code is None:
                        auth_login(request, user)
                        return HttpResponse(f"You are now logged in as {username}")
                    elif result == "fail" and error_code == "incorrect_input_answer":
                        messages.error(request, 'The captcha code entered is not correct. ' 
                                                'Please try again.')
                    elif result == "fail" and error_code == "timeout_or_duplicate":
                        messages.error(request, 'The captcha code is no longer valid.')

                captcha_form = CaptchaForm(prefix='captcha')

        data = get_captcha_image(request)
        image = data['image']
        request.session['remote_id'] = data['image_id']

    context = {
        'image': image,
        'form': form,
        'captcha_form': captcha_form,
    }
    return render(request, 'login.html', context)



