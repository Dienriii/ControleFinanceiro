from django.db import models
from django.utils import timezone
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta 

class Category(models.Model):
    name = models.CharField(max_length=60, unique=True)
    
    def __str__(self):
        return self.name
    
class Card(models.Model):
    name = models.CharField(max_length=60)
    closing_day = models.PositiveSmallIntegerField(help_text="Dia do fechamento da fatura (1-28)")
    due_day = models.PositiveSmallIntegerField(help_text="Dia do vencimento da fatura (1-28)")

    def __str__(self):
        return self.name

class Purchase(models.Model):
    payment_types = [
        ("credit", "Crédito"),
        ("debit", "Débito"),
        ("cash", "Dinheiro"),
        ("pix", "Pix"),
        ("transfer", "Transferência"),
    ]

    date = models.DateField(default=timezone.now)
    description = models.CharField(max_length=150)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    payment_type = models.CharField(max_length=15, choices=payment_types)
    card = models.ForeignKey(Card, on_delete=models.PROTECT, blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_fixed = models.BooleanField(default=False)
    is_paid = models.BooleanField(default=False)
    installments_count =  models.PositiveSmallIntegerField(default=1)

    def __str__(self):
        return f"{self.description} - R${self.total_amount} - {self.date}"
    
    def save(self, *args, **kwargs):
        creating = self.pk is None
        super().save(*args, **kwargs)
        if creating:
            self.generate_installments()

    def first_bill_due_date(self):
        if not self.card:
            return self.date
        closing = self.card.closing_day
        due = self.card.due_day
        
        base = date(self.date.year, self.date.month, min(self.date.day, 28))
        months_to_add = 1 if self.date.day <= closing else 2
        # if self.date.day <= closing:
        #     months_to_add = 1
        # else:
        #     months_to_add = 2

        first_month = base + relativedelta(day=due, months=+months_to_add)

        return first_month
    
    def generate_installments(self):
        if self.installments_count < 1:
            self.installments_count = 1

        cents = int(round(float(self.total_amount) * 100))
        base = cents // self.installments_count
        remainder = cents % self.installments_count

        if self.payment_type == "credit":
            first_due = self.first_bill_due_date()
            for i in range(self.installments_count):
                part = base + (1 if i < remainder else 0)
                amt = part / 100.0
                due = first_due + relativedelta(months=+i)
                Installment.objects.create(
                    purchase=self,
                    number=i+1,
                    due_date=due,
                    amount=amt,
                    paid=False
                )

        else:
            Installment.objects.create(
                purchase=self,
                number=1,
                due_date=self.date,
                amount=float(cents)/100.0,
                paid=False
            )

class Installment(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.PROTECT)
    number = models.PositiveSmallIntegerField()
    due_date = models.DateField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    paid = models.BooleanField(default=False)

    class Meta:
        unique_together = ('purchase', 'number')
        ordering = ['due_date', 'purchase_id', 'number']

    def __str__(self):
        return f"{self.purchase.description} - R${self.amount} - {self.due_date}"
    

class Income(models.Model):
    date = models.DateField(default=timezone.now)
    description = models.CharField(max_length=150)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.description} - R${self.total_amount} - {self.date}"
    
class RecurringIncome(models.Model):
    description = models.CharField(max_length=150)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    day_of_month = models.PositiveSmallIntegerField(help_text="1-28 (use p/ meses menores)")
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"self.description (todo dia {self.day_of_month})"
    

class InvestmentSnapshot(models.Model):
    date = models.DateField(default=timezone.now)
    plataform = models.CharField(max_length=150, help_text="Plataforma de investimento", blank = True)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)

    def __str__(self):
        return f" {self.date} - R${self.total_amount}"
    
class MonthlySavings(models.Model):
    month = models.DateField(help_text="Use o primeiro dia do mês, ex.: 2025-10-01")
    save_amount = models.DecimalField(max_digits=15, decimal_places=2)

    class Meta:
        unique_together = ('month',)

    def __str__(self):
        return f" {self.date} - R${self.save_amount}"
    