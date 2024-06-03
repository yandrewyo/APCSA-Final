from django import forms
from main.models import Info


class InfoForm(forms.ModelForm):
    class Meta:
        model = Info
        fields = ["name", "team", "events", "meets", "pbs", "best_performances", "goals"]
      