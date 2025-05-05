from django import forms

from .models import Demand, DemandUrgencyChoices

from documentation.services import get_all_countries

class DemandForm(forms.ModelForm):
    class Meta:
        model = Demand
        fields = ['job_name', 'country', 'no_of_vacancy', 'skill_required', 'salary_min', 'salary_max','demand_urgency']
        labels = {
            'country': 'Country',
            'job_name': 'Job Name',
            'no_of_vacancy': 'No. of Vacancy',
            'skill_required': 'Skill Required',
            'demand_urgency': 'Demand',
        }
    
    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super(DemandForm, self).__init__(*args, **kwargs)
        self.fields['job_name'].widget.attrs['placeholder'] = 'Enter Job Name'
        self.fields['no_of_vacancy'].widget.attrs['placeholder'] = 'Total number of Vacancy'
        self.fields['skill_required'].widget.attrs['placeholder'] = 'All required skills'
        # self.fields['salary_offered'].widget.attrs['placeholder'] = 'Salary Range (if any)'
        self.fields['salary_min'].widget.attrs['placeholder'] = 'Min'
        self.fields['salary_max'].widget.attrs['placeholder'] = 'Max'
        self.fields['demand_urgency'].choices = [('', 'Select the urgency of demand')] + list(DemandUrgencyChoices.choices)

        if request:
            self.fields['country'].queryset = get_all_countries(request)
            self.fields['country'].empty_label = "Select country"

    def clean(self):
        cleaned_data = super().clean()
        min_salary = cleaned_data.get("salary_min")
        max_salary = cleaned_data.get("salary_max")
        if min_salary and max_salary and min_salary > max_salary:
            self.add_error('salary_min', "Minimum salary cannot be greater than maximum salary.")

        return cleaned_data