from datetime import datetime, timedelta

from django.db import models
from django.contrib.auth.models import User
from customer.models import Customer


class Category(models.Model):
    category_name = models.CharField(max_length=20)
    creation_date = models.DateField(auto_now=True)

    def __str__(self):
        return self.category_name


class Policy(models.Model):
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    policy_name = models.CharField(max_length=200)
    sum_assurance = models.PositiveIntegerField()
    premium = models.PositiveIntegerField()
    tenure = models.PositiveIntegerField()
    benefits = models.CharField(max_length=500, default="1. Cover against Uncertainties  \n2. Cash Flow Management  "
                                                        "\n3. Investment Opportunities")
    creation_date = models.DateField(auto_now=True)

    def __str__(self):
        return self.policy_name


def return_date_time():
    now = datetime.now()
    return now.replace(year=now.year+1)


class PolicyRecord(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    Policy = models.ForeignKey(Policy, on_delete=models.CASCADE)
    status = models.CharField(max_length=100, default='Pending')
    creation_date = models.DateField(auto_now=True)
    endDate = models.DateField(default=return_date_time)


class Question(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    description = models.CharField(max_length=500)
    admin_comment = models.CharField(max_length=200,default='Nothing')
    asked_date = models.DateField(auto_now=True)

    def __str__(self):
        return self.description

class Claim(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    policy = models.CharField(max_length=200)
    status = models.CharField(max_length=100, default='Pending')
    proof_doc = models.FileField(upload_to='proofs/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
