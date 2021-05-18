from django import forms


class CaptchaForm(forms.Form):
    captcha = forms.CharField(max_length=16, label='Captcha', required=True,
                              help_text="The CAPTCHA code is valid for two minutes")

    class Meta:
        fields = 'captcha'
