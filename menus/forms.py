from django import forms
from django.forms import ModelForm

from .models import Menu, MenuSection, MenuItem


class MenuForm(ModelForm):
    class Meta:
        model = Menu
        fields = ['restaurant', 'name']
        widgets = {'restaurant': forms.HiddenInput()}


class MenuSectionCreateForm(ModelForm):
    class Meta:
        model = MenuSection
        fields = ['menu', 'name']
        widgets = {'menu': forms.HiddenInput()}


class MenuItemForm(ModelForm):
    class Meta:
        model = MenuItem
        fields = ['menusection', 'name', 'description']
        widgets = {'menusection': forms.HiddenInput()}
