from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.MonthOverviewView.as_view(), name='month_overview'),
    path('month/<int:year>/<int:month>/', views.MonthOverviewView.as_view(), name='month_overview_specific'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('purchase/new/', views.PurchaseCreateView.as_view(), name='purchase_create'),
    path('income/new/', views.IncomeCreateView.as_view(), name='income_create'),
    path('card/new/', views.CardCreateView.as_view(), name='card_create'),
    path('category/new/', views.CategoryCreateView.as_view(), name='category_create'),
    path('investment/new/', views.InvestmentCreateView.as_view(), name='investment_create'),
    path('savings/new/', views.SavingsCreateView.as_view(), name='savings_create'),
]