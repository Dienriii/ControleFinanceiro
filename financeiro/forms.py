from django import forms
from .models import Purchase, Income, Card, Category, InvestmentSnapshot, MonthlySavings

class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ['date', 'description', 'category', 'payment_type', 'card', 'total_amount', 'is_fixed', 'is_paid', 'installments_count']
        widgets = {
            "date": forms.DateInput(attrs={"type": "date", "class": "datepicker"}),
            "description": forms.TextInput(attrs={"class": "form-control"}),
            "category": forms.Select(attrs={"class": "form-control"}),
            "payment_type": forms.Select(attrs={"class": "form-control"}),
            "card": forms.Select(attrs={"class": "form-control"}),
            "total_amount": forms.NumberInput(attrs={"class": "form-control"}),
            "installments_count": forms.NumberInput(attrs={"class": "form-control", "set_value": "0", "min": "1", "max": "24"}),
        }

class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ['date', 'description', 'total_amount']
        widgets = {
            "date": forms.DateInput(attrs={"type": "date", "class": "datepicker"}),
            "description": forms.TextInput(attrs={"class": "form-control"}),
            "total_amount": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
        }

class CardForm(forms.ModelForm):
    class Meta:
        model = Card
        fields = ['name', 'closing_day', 'due_day']
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "closing_day": forms.NumberInput(attrs={"class": "form-control", "min": "1", "max": "28"}),
            "due_day": forms.NumberInput(attrs={"class": "form-control", "min": "1", "max": "28"}),
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
        }

class InvestmentForm(forms.ModelForm):
    class Meta:
        model = InvestmentSnapshot
        fields = ['date',  'plataform', 'total_amount']
        widgets = {
            "date": forms.DateInput(attrs={"type": "date", "class": "datepicker"}),
            "plataform": forms.TextInput(attrs={"class": "form-control"}),
            "total_amount": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
        }

class SavingsForm(forms.ModelForm):
    class Meta:
        model = MonthlySavings
        fields = ['month', 'save_amount']
        widgets = {
            "month": forms.DateInput(attrs={"type": "date", "class": "datepicker"}),
            "save_amount": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
        }