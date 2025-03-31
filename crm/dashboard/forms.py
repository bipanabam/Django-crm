from django import forms

class UserLoginForm(forms.Form):
    email = forms.EmailField(
        label='Email Address',
        widget=forms.EmailInput(attrs={
            'placeholder': 'Enter your email address',
        })
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Enter your password',
        })
    )

    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['placeholder'] = 'Enter your email address'
        self.fields['password'].widget.attrs['placeholder'] = 'Enter your password'
