from django import forms


class CaptchaForm(forms.Form):
    captcha = forms.CharField(max_length=16, label='Captcha', required=True)

    class Meta:
        fields = 'captcha'
