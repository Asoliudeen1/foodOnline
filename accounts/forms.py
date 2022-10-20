from wsgiref.validate import validator
from django import forms
from .models import User, UserProfile
from .validators import allow_only_images

class UserForm (forms.ModelForm):
    
    # We created pass and confirm pass cos we customize our User Model
    password= forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password']

    # this method confirm if password and confirm_password Match  (non field error)
    def clean(self):
        cleaned_data = super(UserForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get ('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError(
                "Password does not match"
            )


class UserProfileForm(forms.ModelForm):

    #style the image Field with Css
    address = forms.CharField(widget=forms.TextInput(attrs={'required': 'required'}))
    profile_picture = forms.FileField(widget=forms.FileInput(attrs={'class': 'btn btn-info'}), validators=[allow_only_images])
    cover_photo = forms.FileField(widget=forms.FileInput(attrs={'class': 'btn btn-info'}), validators=[allow_only_images])
    
    
    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'cover_photo', 'address', 'country', 'state', 'city', 'pin_code', 'latitude', 'longitude']


    # make longitude and latitude Field to be Read Only
    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            if field == 'latitude' or field == 'longitude':
                self.fields[field].widget.attrs['readonly'] = 'readonly'

