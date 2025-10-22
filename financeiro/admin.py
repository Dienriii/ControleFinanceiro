from django.contrib import admin
from .models import Category, Card, Purchase, Installment, Income, RecurringIncome, InvestmentSnapshot, MonthlySavings

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ['name', 'closing_day', 'due_day']

class InstallmentInline(admin.TabularInline):
    model = Installment
    extra = 0
    readonly_fields = ("number", "due_date", "amount", "paid")

@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('date', 'description', 'category', 'payment_type', 'total_amount', 'installments_count', 'card')
    list_filter = ('payment_type', 'category')
    inlines = [InstallmentInline]

@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ('date', 'description', 'total_amount')

@admin.register(RecurringIncome)
class RecurringIncomeAdmin(admin.ModelAdmin):
    list_display = ('description', 'amount', 'day_of_month', 'active')
    list_editable = ('active',)

@admin.register(InvestmentSnapshot)
class InvestimentSnapshotAdmin(admin.ModelAdmin):
    list_display = ('date', 'plataform', 'total_amount')

@admin.register(MonthlySavings)
class MonthlySavingsAdmin(admin.ModelAdmin):
    list_display = ('month', 'save_amount')