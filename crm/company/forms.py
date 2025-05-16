from django import forms

from .models import Branch, User, AccessLevel, Employee, RoleChoices

from .services import get_branches, get_all_access_levels

class BranchForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = ['name', 'country', ]

    def __init__(self, *args, **kwargs):
        super(BranchForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['placeholder'] = 'Enter your Branch Name'
        self.fields['country'].widget.attrs['placeholder'] = 'Enter the Country Name'

class UserForm(forms.ModelForm):
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    branch = forms.ModelChoiceField(queryset=Branch.objects.none(), empty_label="Select your Branch", required=False)
    access_level = forms.ModelMultipleChoiceField(
        queryset=AccessLevel.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    class Meta:
        model = User
        fields = ['username','email', 'first_name', 'last_name', 'password', 'confirm_password', 'branch', 'role', 'access_level']
        widgets = {
            'password': forms.PasswordInput(),
        }

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['placeholder'] = 'Enter your Username'
        self.fields['email'].widget.attrs['placeholder'] = 'Enter your Email'
        self.fields['first_name'].widget.attrs['placeholder'] = 'Enter your First Name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Enter your Last Name'
        self.fields['password'].widget.attrs['placeholder'] = 'Enter your Password'
        self.fields['confirm_password'].widget.attrs['placeholder'] = 'Confirm your Password'
        self.fields['branch'].queryset = get_branches(request)
        self.fields['access_level'].queryset = get_all_access_levels(request)

        # Role filtering
        if request:
            if request.user.is_superuser:
                self.fields['role'].choices = RoleChoices.choices
            else:
                current_role = request.user.role
                if current_role == 'admin':
                    self.fields['role'].choices = [
                        (key, label) for key, label in RoleChoices.choices if key != 'admin'
                    ]
                elif current_role == 'manager' or current_role == 'team manager':
                    self.fields['role'].choices = [
                        (key, label) for key, label in RoleChoices.choices if key not in ['admin', 'manager']
                    ]
                else:
                    self.fields['role'].choices = None

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
    
class UserUpdateForm(forms.ModelForm):
    access_level = forms.ModelMultipleChoiceField(
        queryset=AccessLevel.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    class Meta:
        model = User
        fields = ['username','email', 'first_name', 'last_name', 'role', 'access_level']

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        if request:
            self.fields['access_level'].queryset = get_all_access_levels(request)

        # Role filtering
        if request:
            if request.user.is_superuser:
                self.fields['role'].choices = RoleChoices.choices
            else:
                current_role = request.user.role
                if current_role == 'admin':
                    self.fields['role'].choices = [
                        (key, label) for key, label in RoleChoices.choices if key != 'admin'
                    ]
                elif current_role == 'manager' or current_role == 'team manager':
                    self.fields['role'].choices = [
                        (key, label) for key, label in RoleChoices.choices if key not in ['admin', 'manager']
                    ]
                else:
                    self.fields['role'].choices = None

class UserSettingForm(forms.ModelForm):
    new_password = forms.CharField(widget=forms.PasswordInput, required=False)
    confirm_new_password = forms.CharField(widget=forms.PasswordInput, required=False)

    class Meta:
        model = User
        fields = ['username','email', 'first_name', 'last_name', 'new_password', 'confirm_new_password']
        widgets = {
            'new_password': forms.PasswordInput(),
            'confirm_new_password': forms.PasswordInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password'].widget.attrs['placeholder'] = 'Enter new Password'
        self.fields['confirm_new_password'].widget.attrs['placeholder'] = 'Confirm new Password'

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_new_password = cleaned_data.get("confirm_new_password")

        if not new_password and not confirm_new_password:
            return cleaned_data

        if new_password and not confirm_new_password:
            self.add_error('confirm_new_password', "Please confirm your new password.")

        if new_password and confirm_new_password and new_password != confirm_new_password:
            self.add_error('confirm_new_password', "Passwords do not match")
        return cleaned_data

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['name', 'date_of_birth', 'gender', 'blood_type', 'marital_status', 'citizenship_number', 'pan_number', 'current_address', 'permanent_address', 'email', 'phone_number', 'mobile_number', 'emergency_contact_name', 'emergency_contact_number', 'emergency_contact_relationship', 'emergency_contact_email', 'photo', 'signature']
        labels = {
            'date_of_birth': 'Date of Birth [AD]',
            'gender': 'Gender',
            'blood_type': 'Blood Group',
            'marital_status': 'Marital Status',
            'citizenship_number': 'Citizenship Number',
            'pan_number': 'PAN Number',
            'current_address': 'Current Address',
            'permanent_address': 'Permanent Address',
            'email': 'Email',
            'phone_number': 'Contact Number (Home)',
            'mobile_number': 'Mobile Number',
            'emergency_contact_name': 'Emergency Contact Name',
            'emergency_contact_number': 'Contact Number',
            'emergency_contact_relationship': 'Relation',
            'emergency_contact_email': 'Email (Optional)',
            'photo': 'Photo',
            'signature': 'Signature',
        }
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }