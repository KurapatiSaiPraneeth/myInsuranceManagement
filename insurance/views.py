from django.shortcuts import render,redirect,reverse
from . import forms, models
from django.db.models import Sum
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required,user_passes_test
from django.conf import settings
from datetime import date, timedelta
from django.db.models import Q
from django.core.mail import EmailMessage
from django.contrib.auth.models import User
from customer import models as CMODEL
from customer import forms as CFORM

from django.core.mail import send_mail
from django.template.loader import render_to_string

from django.conf import settings

from celery import shared_task
from django.utils import timezone



def home_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')  
    return render(request, 'insurance/index.html')


def is_customer(user):
    return user.groups.filter(name='CUSTOMER').exists()


def afterlogin_view(request):
    if is_customer(request.user):
        return redirect('customer/customer-dashboard')
    else:
        return redirect('admin-dashboard')


def adminclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return HttpResponseRedirect('adminlogin')


@login_required(login_url='adminlogin')
def admin_dashboard_view(request):
    dict={
        'total_user':CMODEL.Customer.objects.all().count(),
        'total_policy':models.Policy.objects.all().count(),
        'total_category':models.Category.objects.all().count(),
        'total_question':models.Question.objects.all().count(),
        'total_policy_holder':models.PolicyRecord.objects.all().count(),
        'approved_policy_holder':models.PolicyRecord.objects.all().filter(status='Approved').count(),
        'disapproved_policy_holder':models.PolicyRecord.objects.all().filter(status='Disapproved').count(),
        'waiting_policy_holder':models.PolicyRecord.objects.all().filter(status='Pending').count(),
        'claims':models.Claim.objects.all().count(),
    }
    return render(request, 'insurance/admin_dashboard.html', context=dict)


@login_required(login_url='adminlogin')
def admin_view_customer_view(request):
    customers = CMODEL.Customer.objects.all()
    return render(request, 'insurance/admin_view_customer.html', {'customers': customers})


@login_required(login_url='adminlogin')
def update_customer_view(request,pk):
    customer=CMODEL.Customer.objects.get(id=pk)
    user=CMODEL.User.objects.get(id=customer.user_id)
    userForm=CFORM.CustomerUserForm(instance=user)
    customerForm=CFORM.CustomerForm(request.FILES,instance=customer)
    mydict={'userForm':userForm,'customerForm':customerForm}
    if request.method=='POST':
        userForm=CFORM.CustomerUserForm(request.POST,instance=user)
        customerForm=CFORM.CustomerForm(request.POST,request.FILES,instance=customer)
        if userForm.is_valid() and customerForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            customerForm.save()
            return redirect('admin-view-customer')
    return render(request,'insurance/update_customer.html',context=mydict)


@login_required(login_url='adminlogin')
def delete_customer_view(request,pk):
    customer=CMODEL.Customer.objects.get(id=pk)
    user=User.objects.get(id=customer.user_id)
    user.delete()
    customer.delete()
    return HttpResponseRedirect('/admin-view-customer')


def admin_category_view(request):
    return render(request,'insurance/admin_category.html')


def admin_add_category_view(request):
    categoryForm=forms.CategoryForm() 
    if request.method=='POST':
        categoryForm=forms.CategoryForm(request.POST)
        if categoryForm.is_valid():
            categoryForm.save()
            return redirect('admin-view-category')
    return render(request,'insurance/admin_add_category.html',{'categoryForm':categoryForm})


def admin_view_category_view(request):
    categories = models.Category.objects.all()
    return render(request,'insurance/admin_view_category.html',{'categories':categories})


def admin_delete_category_view(request):
    categories = models.Category.objects.all()
    return render(request,'insurance/admin_delete_category.html',{'categories':categories})


def delete_category_view(request,pk):
    category = models.Category.objects.get(id=pk)
    category.delete()
    return redirect('admin-delete-category')


def admin_update_category_view(request):
    categories = models.Category.objects.all()
    return render(request,'insurance/admin_update_category.html',{'categories':categories})


@login_required(login_url='adminlogin')
def update_category_view(request,pk):
    category = models.Category.objects.get(id=pk)
    categoryForm=forms.CategoryForm(instance=category)
    
    if request.method=='POST':
        categoryForm=forms.CategoryForm(request.POST,instance=category)
        
        if categoryForm.is_valid():

            categoryForm.save()
            return redirect('admin-update-category')
    return render(request,'insurance/update_category.html',{'categoryForm':categoryForm})
  

def admin_policy_view(request):
    return render(request,'insurance/admin_policy.html')


def admin_add_policy_view(request):
    policyForm=forms.PolicyForm() 
    
    if request.method=='POST':
        policyForm=forms.PolicyForm(request.POST)
        if policyForm.is_valid():
            categoryid = request.POST.get('category')
            category = models.Category.objects.get(id=categoryid)
            
            policy = policyForm.save(commit=False)
            policy.category=category
            policy.save()
            return redirect('admin-view-policy')
    return render(request,'insurance/admin_add_policy.html',{'policyForm':policyForm})


def admin_view_policy_view(request):
    policies = models.Policy.objects.all()
    return render(request,'insurance/admin_view_policy.html',{'policies':policies})


def admin_update_policy_view(request):
    policies = models.Policy.objects.all()
    return render(request,'insurance/admin_update_policy.html',{'policies':policies})


@login_required(login_url='adminlogin')
def update_policy_view(request,pk):
    policy = models.Policy.objects.get(id=pk)
    policyForm=forms.PolicyForm(instance=policy)
    
    if request.method=='POST':
        policyForm=forms.PolicyForm(request.POST,instance=policy)
        
        if policyForm.is_valid():

            categoryid = request.POST.get('category')
            category = models.Category.objects.get(id=categoryid)
            
            policy = policyForm.save(commit=False)
            policy.category=category
            policy.save()
           
            return redirect('admin-update-policy')
    return render(request,'insurance/update_policy.html',{'policyForm':policyForm})
  
  
def admin_delete_policy_view(request):
    policies = models.Policy.objects.all()
    return render(request,'insurance/admin_delete_policy.html',{'policies':policies})


def delete_policy_view(request,pk):
    policy = models.Policy.objects.get(id=pk)
    policy.delete()
    return redirect('admin-delete-policy')


def admin_view_policy_holder_view(request):
    policyrecords = models.PolicyRecord.objects.all()
    return render(request,'insurance/admin_view_policy_holder.html',{'policyrecords':policyrecords})


def admin_view_approved_policy_holder_view(request):
    policyrecords = models.PolicyRecord.objects.all().filter(status='Approved')
    return render(request,'insurance/admin_view_approved_policy_holder.html',{'policyrecords':policyrecords})


def admin_view_disapproved_policy_holder_view(request):
    policyrecords = models.PolicyRecord.objects.all().filter(status='Disapproved')
    return render(request,'insurance/admin_view_disapproved_policy_holder.html',{'policyrecords':policyrecords})


def admin_view_waiting_policy_holder_view(request):
    policyrecords = models.PolicyRecord.objects.all().filter(status='Pending')
    return render(request,'insurance/admin_view_waiting_policy_holder.html',{'policyrecords':policyrecords})


def approve_request_view(request,pk):
    policyrecords = models.PolicyRecord.objects.get(id=pk)
    policyrecords.status='Approved'
    policyrecords.save()
    return redirect('admin-view-policy-holder')


def disapprove_request_view(request,pk):
    policyrecords = models.PolicyRecord.objects.get(id=pk)
    policyrecords.status='Disapproved'
    policyrecords.save()
    return redirect('admin-view-policy-holder')


def admin_question_view(request):
    questions = models.Question.objects.all()
    return render(request,'insurance/admin_question.html',{'questions':questions})


def update_question_view(request,pk):
    question = models.Question.objects.get(id=pk)
    questionForm=forms.QuestionForm(instance=question)
    
    if request.method=='POST':
        questionForm=forms.QuestionForm(request.POST,instance=question)
        
        if questionForm.is_valid():

            admin_comment = request.POST.get('admin_comment')
            
            
            question = questionForm.save(commit=False)
            question.admin_comment=admin_comment
            question.save()
           
            return redirect('admin-question')
    return render(request,'insurance/update_question.html',{'questionForm':questionForm})


def aboutus_view(request):
    return render(request,'insurance/aboutus.html')


def contactus_view(request):
    sub = forms.ContactusForm()
    if request.method == 'POST':
        sub = forms.ContactusForm(request.POST)
        if sub.is_valid():
            email = sub.cleaned_data['Email']
            name=sub.cleaned_data['Name']
            message = sub.cleaned_data['Message']
            send_mail(str(name)+' || '+str(email),message,settings.EMAIL_HOST_USER, settings.EMAIL_RECEIVING_USER, fail_silently = False)
            return render(request, 'insurance/contactussuccess.html')
    return render(request, 'insurance/contactus.html', {'form':sub})


@login_required(login_url='adminlogin')
def claim_dashboard_view(request):
    dict={
        'total_claims':models.Claim.objects.all().count(),
        'approved_claims':models.Claim.objects.all().filter(status='Approved').count(),
        'disapproved_claims':models.Claim.objects.all().filter(status='Disapproved').count(),
        'pending_claims':models.Claim.objects.all().filter(status='Pending').count(),
    }
    return render(request, 'insurance/claim_dashboard.html', context=dict)


def total_claims(request):
    all_claims = models.Claim.objects.all()
    return render(request,'insurance/admin_total_claims.html',{'all_claims':all_claims})

def approve_claim_request_view(request,pk):
    claimrecord = models.Claim.objects.get(id=pk)
    claimrecord.status='Approved'
    claimrecord.save()
    user = claimrecord.customer.user
    email_subject = "Your Policy Claim Notification"
    email_body_data = {
        "user" : user,
        "message" : "Your Claim has been approved !!!"
    }
    send_notification_email(email_subject, email_body_data)
    return redirect('admin-total_claim')


def disapprove_claim_request_view(request,pk):
    claimrecord = models.Claim.objects.get(id=pk)
    claimrecord.status='Disapproved'
    claimrecord.save()
    user = claimrecord.customer.user
    email_subject = "Your Policy Claim Notification"
    email_body_data = {
        "user" : user,
        "message" : "Your Claim has been disapproved !!!"
    }
    send_notification_email(email_subject, email_body_data)
    return redirect('admin-total_claim')

def admin_view_approved_claim(request):
    claimrecords = models.Claim.objects.all().filter(status='Approved')
    return render(request,'insurance/admin_claim_status.html',{'claimrecords':claimrecords})


def admin_view_disapproved_claim(request):
    claimrecords = models.Claim.objects.all().filter(status='Disapproved')
    return render(request,'insurance/admin_claim_status.html',{'claimrecords':claimrecords})


def admin_view_pending_claims(request):
    claimrecords = models.Claim.objects.all().filter(status='Pending')
    return render(request,'insurance/admin_total_claims.html',{'all_claims':claimrecords})



def send_notification_email(email_subject, email_body_data):
    user = email_body_data.get("user")
    email_body = render_to_string('insurance/email_template.html', email_body_data)
    from_email = settings.EMAIL_HOST_USER
    to_email = [user.email]
    email = EmailMessage(email_subject, email_body, from_email, to_email)
    email.content_subtype = 'html'
    success_count = email.send()
    if success_count == 1:
        print('Email sent successfully')
    else:
        print('Email was not sent')


# def send_notification_email(user):
#     subject = 'Insurance Notification'
#     message = render_to_string('insurance/email_template.html', {'user': user})
#     from_email = settings.EMAIL_HOST_USER
#     recipient_list = [user.email]
#     success_count = send_mail(subject, message, from_email, recipient_list)
#     if success_count == 1:
#         print('Email sent successfully')
#     else:
#         print('Email was not sent')


@shared_task
def auto_renew_policies():
    for policy in models.PolicyRecord.objects.all():

        # calculate new end date and save
        policy_tenure = policy.Policy.tenure
        delta = policy.endDate - timezone.now().date()
        days_between = delta.days
        if policy.endDate < timezone.now().date():
            if policy.auto_renew:
                policy.endDate = timezone.now().date() + relativedelta(months=policy_tenure)
            else:
                policy.status = "Expired"
            policy.save()
        elif days_between < 10:
            base_url = "http://127.0.0.1:8000"
            email_subject = "Policy Auto Renewal Notification"
            email_body_data = {
                "user": policy.customer.user,
                "message": "Your Insurance policy will expire soon !!!. Please click on below link to auto renew your policy.",
                "notification_title": "Policy Auto Renewal Link !!!",
                "customer_id": policy.customer.id,
                "policy_id": policy.Policy.id,
                "base_url": base_url
            }
            send_notification_email(email_subject, email_body_data)

