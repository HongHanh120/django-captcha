from django import forms
from .fields import CaptchaAnswerInput


class CaptchaForm(forms.Form):
    captcha = forms.CharField(max_length=254, required=True, widget=CaptchaAnswerInput)

    class Meta:
        fields = 'captcha'
