from functools import total_ordering
from multiprocessing import context
from unicodedata import category
from django.shortcuts import render,redirect
from .models import *
from django.views.generic import View
# from django.conf import settings
from django.core.mail import send_mail
import json


# Create your views here.
class Index(View):    
    def get(self, request, *args, **kwargs):
        return render(request, 'index.html')
class About(View):    
    def get(self, request, *args, **kwargs):
        return render(request, 'about.html')
class Order(View):
    def get(self,request,*args, **kwargs):
        appetizers = MenuItem.objects.filter(category__name__contains='Appetizer')
        entres = MenuItem.objects.filter(category__name__contains='Entre')
        desserts = MenuItem.objects.filter(category__name__contains = 'Dessert')
        drinks = MenuItem.objects.filter(category__name__contains = 'Drink')
        
        context = {
            'appetizers': appetizers,
            'entres':entres,
            'desserts': desserts,
            'drinks': drinks, 
        }
        return render(request,'order.html',context)
    
    def post(self, request, *args, **kwargs):
        #get input fields at the bottom of the order template
        name = request.POST.get('name')
        email = request.POST.get('email')
        street = request.POST.get('street')
        city= request.POST.get('city')
        state= request.POST.get('state')
        zip_code=request.POST.get('zip')
        
        #a customer orders items from the Menu which arre placed in an empty list called items
        order_items = {
            'items': []
        }
        items = request.POST.getlist('items[]')
        for item in items:
            #get all the ordered items and place them in the menu_item variable
            menu_item = MenuItem.objects.get(pk__contains=int(item))
            item_data = {
                'id': menu_item.pk,
                'name': menu_item.name,
                'price': menu_item.price,
            }
            #for appending the item in the list
            order_items['items'].append(item_data)
        #  to get each price and id.   
        #to calculate the total price, we need each id to add it as a relationship to our order object that we are about to create.
            price = 0
            item_ids = []
            
        for item in order_items['items']:
            price += item['price']
            item_ids.append(item['id'])
        
        order = OrderModel.objects.create(
            price=price,
            name=name,
            email=email,
            street=street,
            city=city,
            state=state,
            zip_code=zip_code
            )
        #line will go through each item id in the list and add it to the order that we just made
        order.items.add(*item_ids)
        
         # After all the calculations for the units and price are done a confirmation email is sent to the customer
        body = ('Hello, thank you so much for your order, your food is being prepared and it will be delivered soon \n'f'Your total:{price}\n')
        
        send_mail(
            'Thank you for your Order',
            body,
            'june@gmail.com',
            [email],
            fail_silently=False
        )
        
        context = {
            'items': order_items['items'],
            'price': price
        }
        # return render(request, 'order_confirmation.html', context)
        return redirect('order-confirmation',pk=order.pk)
    
class OrderConfirmation(View):
    def get(self,request,pk, *args, **kwargs):
        order = OrderModel.objects.get(pk=pk)#get what the user ordered
        
        context = {
            'pk' : order.pk,
            'items' : order.items,
            'price' : order.price    
        }
    
        return render(request,'order_confirmation.html',context)
    
    def post(self,request,pk,*args, **kwargs):
        data = json.loads(request.body)

        if data['isPaid']:
            order = OrderModel.objects.get(pk=pk)
            order.is_paid = True
            order.save()#save the is_paid object in the db
        
        return redirect('payment-confirmation')
        
class OrderPayConfirmation(View):
    def get(self,request,*args, **kwargs):
        return render(request,'order_pay_confirmation.html')
    
