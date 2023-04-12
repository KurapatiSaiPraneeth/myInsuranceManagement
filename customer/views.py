import datetime

from django.shortcuts import render,redirect,reverse
from . import forms,models
from django.db.models import Sum
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib import messages
from django.conf import settings
from datetime import date, timedelta
from django.db.models import Q
from django.core.mail import send_mail
from insurance import models as CMODEL
from insurance import forms as CFORM
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.http import HttpResponse


def customerclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'customer/customerclick.html')


def customer_signup_view(request):
    userForm=forms.CustomerUserForm()
    customerForm=forms.CustomerForm()
    mydict={'userForm':userForm,'customerForm':customerForm}
    if request.method=='POST':
        userForm=forms.CustomerUserForm(request.POST)
        customerForm=forms.CustomerForm(request.POST,request.FILES)
        if userForm.is_valid() and customerForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            customer=customerForm.save(commit=False)
            customer.user=user
            customer.save()
            my_customer_group = Group.objects.get_or_create(name='CUSTOMER')
            my_customer_group[0].user_set.add(user)
        return HttpResponseRedirect('customerlogin')
    return render(request,'customer/customersignup.html',context=mydict)


def is_customer(user):
    return user.groups.filter(name='CUSTOMER').exists()


@login_required(login_url='customerlogin')
def customer_dashboard_view(request):
    dict = {
        'customer':models.Customer.objects.get(user_id=request.user.id),
        'available_policy': CMODEL.Policy.objects.all().count(),
        'applied_policy': CMODEL.PolicyRecord.objects.all().filter(customer=models.Customer.objects.get(user_id=request.user.id)).count(),
        'total_category': CMODEL.Category.objects.all().count(),
        'total_question': CMODEL.Question.objects.all().filter(customer=models.Customer.objects.get(user_id=request.user.id)).count(),

    }
    return render(request, 'customer/customer_dashboard.html', context=dict)


def apply_policy_view(request):
    customer = models.Customer.objects.get(user_id=request.user.id)
    policies = CMODEL.Policy.objects.all()
    return render(request, 'customer/apply_policy.html', {'policies': policies, 'customer': customer})


def apply_view(request, pk):
    customer = models.Customer.objects.get(user_id=request.user.id)
    policy = CMODEL.Policy.objects.get(id=pk)
    records = CMODEL.PolicyRecord.objects.all().filter(customer_id=customer.id, Policy_id=pk)
    for rec in records:
        if (datetime.date.today() - rec.creation_date).days <= 365 and rec.status in ['Approved', 'Pending']:
            messages.error(request, "The applied policy is already approved or waiting for approval.")
            return redirect('history')
    policyrecord = CMODEL.PolicyRecord()
    policyrecord.Policy = policy
    policyrecord.customer = customer
    policyrecord.save()
    return redirect('history')


def history_view(request):
    customer = models.Customer.objects.get(user_id=request.user.id)
    policies = CMODEL.PolicyRecord.objects.all().filter(customer=customer)
    return render(request, 'customer/history.html', {'policies': policies, 'customer': customer})

def apply_claim(request):
    customer = models.Customer.objects.get(user_id=request.user.id)
    policies = CMODEL.PolicyRecord.objects.filter(customer=customer)
    policy_names = CMODEL.Policy.objects.filter(id__in = [p.Policy_id for p in policies])
    response = render(request, 'customer/apply_claim.html', {'policies': policy_names, 'customer': customer})
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response

def apply_claim_view(request):
    customer = models.Customer.objects.get(user_id=request.user.id)
    policy = request.POST.get("policy")
    doc_upload = request.FILES.get("doc_upload")
    customer = models.Customer.objects.get(user_id=request.user.id)
    claim_record = CMODEL.Claim()
    claim_record.customer = customer
    claim_record.policy = policy
    claim_record.proof_doc = doc_upload
    claim_record.save()
    return redirect('claim')

def claim_view(request):
    customer = models.Customer.objects.get(user_id=request.user.id)
    claim_details = CMODEL.Claim.objects.filter(customer=customer)
    return render(request, 'customer/claim.html', {'claims': claim_details, 'customer': customer})


def ask_question_view(request):
    customer = models.Customer.objects.get(user_id=request.user.id)
    questionForm = CFORM.QuestionForm()
    
    if request.method == 'POST':
        questionForm = CFORM.QuestionForm(request.POST)
        if questionForm.is_valid():
            
            question = questionForm.save(commit=False)
            question.customer = customer
            question.save()
            return redirect('question-history')
    return render(request, 'customer/ask_question.html', {'questionForm': questionForm, 'customer': customer})


def question_history_view(request):
    customer = models.Customer.objects.get(user_id=request.user.id)
    questions = CMODEL.Question.objects.all().filter(customer=customer)
    return render(request, 'customer/question_history.html', {'questions': questions, 'customer': customer})


def download_file(request, pk):
    MyModel = CMODEL.Claim
    my_model = get_object_or_404(MyModel, pk=pk)
    if my_model.proof_doc:
        response = HttpResponse(my_model.proof_doc, content_type='application/octet-stream')
        return response
    else:
        return HttpResponse("File not found.")


@login_required(login_url='customerlogin')
def approve_auto_renew(request, customer_id, policy_id):
    policy_record = CMODEL.PolicyRecord.objects.get(customer = customer_id, Policy = policy_id)
    policy_record.auto_renew = True
    policy_record.save()
    context = {'message': 'Hello, Your Policy Auto renewal has been activated !!!'}
    return render(request, 'customer/approve_auto_renew.html', context)

