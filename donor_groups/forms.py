from django import forms
from django.core.exceptions import ValidationError

from .models import DonorGroup


class DonorGroupForm(forms.ModelForm):
  """Form for creating and editing donor groups."""

  class Meta:
    model = DonorGroup
    fields = ["name", "description"]
    widgets = {
      "name": forms.TextInput(
        attrs={
          "class": "input input-bordered w-full",
          "placeholder": "Enter group name",
        }
      ),
      "description": forms.Textarea(
        attrs={
          "class": "textarea textarea-bordered w-full",
          "placeholder": "Describe the purpose of this group",
          "rows": 4,
        }
      ),
    }
    labels = {
      "name": "Group Name",
      "description": "Description",
    }


class JoinGroupForm(forms.Form):
  """Form for joining a donor group using a group code."""

  group_code = forms.CharField(
    max_length=8,
    min_length=8,
    widget=forms.TextInput(
      attrs={
        "class": "input input-bordered w-full uppercase",
        "placeholder": "Enter 8-character group code",
        "maxlength": "8",
        "style": "text-transform: uppercase",
      }
    ),
    label="Group Code",
    help_text="Enter the 8-character code to join a group",
  )

  def clean_group_code(self):
    """Validate that the group code exists."""
    group_code = self.cleaned_data.get("group_code", "").upper()

    if not DonorGroup.objects.filter(group_code=group_code).exists():
      raise ValidationError("Invalid group code. Please check and try again.")

    return group_code
