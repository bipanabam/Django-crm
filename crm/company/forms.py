from django import forms

from .models import Branch, User, Employee

class BranchForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = ['company', 'name', 'country', ]

    def __init__(self, *args, **kwargs):
        super(BranchForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['placeholder'] = 'Enter your Branch Name'
        self.fields['country'].widget.attrs['placeholder'] = 'Enter the Country Name'

class UserForm(forms.ModelForm):
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    branch = forms.ModelChoiceField(queryset=Branch.objects.none(), empty_label="Select your Branch", required=False)
    class Meta:
        model = User
        fields = ['username','email', 'first_name', 'last_name', 'password', 'confirm_password', 'branch', 'role']
        widgets = {
            'password': forms.PasswordInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['branch'].queryset = Branch.objects.all()
        self.fields['username'].widget.attrs['placeholder'] = 'Enter your Username'
        self.fields['email'].widget.attrs['placeholder'] = 'Enter your Email'
        self.fields['first_name'].widget.attrs['placeholder'] = 'Enter your First Name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Enter your Last Name'
        self.fields['password'].widget.attrs['placeholder'] = 'Enter your Password'
        self.fields['confirm_password'].widget.attrs['placeholder'] = 'Confirm your Password'
        # self.fields['role'].widget.attrs['empty_label'] = 'Select access level'

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        branch = cleaned_data.get('branch')
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if role == "manager":
            existing_manager = Employee.objects.filter(branch=branch, user__role="manager").exclude(id=self.instance.id if self.instance else None)
            if existing_manager.exists():
                self.add_error('role', "Only one manager can be assigned to a branch.")

        if password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match")
        return cleaned_data