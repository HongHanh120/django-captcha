from django import forms
from .fields import CaptchaAnswerInput


class CaptchaForm(forms.Form):
    # error_messages = {
    #     'answer_mismatch': 'The captcha fields was not correct'
    # }
    captcha = forms.CharField(max_length=254, label='Captcha', required=True)

    class Meta:
        fields = 'captcha'
