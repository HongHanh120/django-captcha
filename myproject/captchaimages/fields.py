from django.forms.widgets import TextInput


class CaptchaAnswerInput(TextInput):
    def build_attrs(self, *args, **kwargs):
        attrs = super(CaptchaAnswerInput, self).build_attrs(*args, **kwargs)
        attrs["autocapitalize"] = "off"
        attrs["autocomplete"] = "off"
        # attrs["autocorrect"] = "off"
        return attrs
