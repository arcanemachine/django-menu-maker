from django import forms
from django.forms import ModelForm

from .models import Menu, MenuSection, MenuItem


class MenuForm(ModelForm):
    class Meta:
        model = Menu
        fields = ['restaurant', 'name', 'description', 'image']
        widgets = {'restaurant': forms.HiddenInput()}


class MenuSectionForm(ModelForm):
    class Meta:
        model = MenuSection
        fields = ['menu', 'name', 'image', 'note']
        widgets = {'menu': forms.HiddenInput()}


class MenuItemForm(ModelForm):
    class Meta:
        model = MenuItem
        fields = ['menusection', 'name', 'price', 'description']
        widgets = {'menusection': forms.HiddenInput()}
