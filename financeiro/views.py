from datetime import date
from dateutil.relativedelta import relativedelta
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import TemplateView, CreateView
from django.db.models import Sum, F
from .models import Card, Category, Purchase, Installment, Income, RecurringIncome,InvestmentSnapshot, MonthlySavings
from .forms import PurchaseForm, IncomeForm, CardForm, CategoryForm, InvestmentForm, SavingsForm
from datetime import date
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from django.views.generic import TemplateView
from django.db.models import Sum, F
from .models import Installment, Income, RecurringIncome


def _month_range(year=None, month=None):
    if year is None or month is None:
        today = timezone.localdate()
        year, month = today.year, today.month
    start = date(year, month, 1)
    end = start + relativedelta(months=+1)
    return start, end


def _recurring_incomes_for_month(start):
    items = []
    for r in RecurringIncome.objects.filter(active=True):
        d = date(start.year, start.month, min(r.day_of_month, 28))
        items.append({"date": d, "description": r.description, "amount": r.amount})
    return items

class MonthOverviewView(TemplateView):
    template_name = "month_overview.html"

    def _month_bounds(self, base):
        start = date(base.year, base.month, 1)
        end = start + relativedelta(months=+1)
        return start, end

    def _month_block(self, month_start):
        start, end = self._month_bounds(month_start)

        qs_inst = (Installment.objects
           .filter(due_date__gte=start, due_date__lt=end)
           .select_related("purchase", "purchase__category", "purchase__card"))

        fixed = [i for i in qs_inst if i.purchase.is_fixed]
        var   = [i for i in qs_inst if not i.purchase.is_fixed]

        total_fixed = sum(i.amount for i in fixed)
        total_var   = sum(i.amount for i in var)

        # Entradas efetivadas
        qs_inc = Income.objects.filter(date__gte=start, date__lt=end)
        inc_total = qs_inc.aggregate(total=Sum("total_amount"))["total"] or 0

        # Entradas recorrentes (projeção)
        recs = []
        for r in RecurringIncome.objects.filter(active=True):
            d = date(start.year, start.month, min(r.day_of_month, 28))
            recs.append({"date": d, "description": r.description, "amount": r.amount})
        rec_total = sum(x["amount"] for x in recs) if recs else 0

        # Poupança (guardado no mês)
        sv = MonthlySavings.objects.filter(month=start).first()
        saved_amount = sv.saved_amount if sv else 0

        total_out = total_fixed + total_var
        balance   = (inc_total + rec_total) - total_out

        return {
            "label": start,
            "entries": list(qs_inc),
            "recs": recs,
            "fixed": fixed,
            "var": var,
            "totals": {
                "incomes": inc_total,
                "recs": rec_total,
                "fixed": total_fixed,
                "var": total_var,
                "out": total_out,
                "balance": balance,
                "saved": saved_amount,
            }
        }

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        # Se veio /month/<year>/<month>/ usa esse; senão mês atual
        year = self.kwargs.get("year")
        month = self.kwargs.get("month")
        if not year or not month:
            today = timezone.localdate()
            year, month = today.year, today.month

        base = date(year, month, 1)
        months = [base + relativedelta(months=+i) for i in range(4)]  # atual + 3 próximos

        blocks = [self._month_block(m) for m in months]

        ctx.update({
            "blocks": blocks,
        })
        return ctx


class DashboardView(TemplateView):
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        last_inv = InvestmentSnapshot.objects.order_by("-date").first()

        start, _ = _month_range()
        savings = MonthlySavings.objects.filter(month=start).first()

        ninety = timezone.localdate() - relativedelta(days=90)
        top_cats = (Installment.objects
                    .filter(due_date__gte=ninety)
                    .values(cat=F("purchase__category__name"))
                    .annotate(total=Sum("amount"))
                    .order_by("-total")[:5])

        ctx.update({
            "last_inv": last_inv,
            "savings": savings,
            "top_cats": top_cats,
        })
        return ctx

class PurchaseCreateView(CreateView):
    model = Purchase
    form_class = PurchaseForm
    template_name = "purchase_form.html"
    success_url = reverse_lazy("month_overview")

class IncomeCreateView(CreateView):
    model = Income
    form_class = IncomeForm
    template_name = "income_form.html"
    success_url = reverse_lazy("month_overview")

class CardCreateView(CreateView):
    form_class = CardForm
    template_name = "card_form.html"
    success_url = reverse_lazy("month_overview")
    def get_queryset(self):
        return Installment.objects.none()  # não usado; apenas para satisfazer GenericView

class CategoryCreateView(CreateView):
    form_class = CategoryForm
    template_name = "category_form.html"
    success_url = reverse_lazy("purchase_create")

    def get_queryset(self):
        return Installment.objects.none()

class InvestmentCreateView(CreateView):
    form_class = InvestmentForm
    template_name = "investment_form.html"
    success_url = reverse_lazy("dashboard")

    def get_queryset(self):
        return Installment.objects.none()

class SavingsCreateView(CreateView):
    form_class = SavingsForm
    template_name = "savings_form.html"
    success_url = reverse_lazy("dashboard")

    def get_queryset(self):
        return Installment.objects.none()