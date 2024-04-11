from django.forms import ModelForm
from .models import userPost

class NewPost(ModelForm):

    class Meta:
        model = userPost
        fields = ["content"]
        #fileds = '__all__'
