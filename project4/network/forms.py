from django import forms
from django.forms import ModelForm
from .models import userPost

class NewPost(ModelForm):

    class Meta:
        model = userPost
        fields = ["content"]
        #fileds = '__all__'

class Edit(forms.Form):
    textarea = forms.CharField(widget=forms.Textarea(), label='')
