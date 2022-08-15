from django.shortcuts import render
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.utils.timezone import datetime
from django.views import View
from customer.models import OrderModel

# Create your views here.
class Dashboard(LoginRequiredMixin,UserPassesTestMixin,View):
    def get(self,request,*args, **kwargs):
        today = datetime.today()
        orders = OrderModel.objects.filter(created_on__year=today.year,created_on__month=today.month,created_on__day=today.day)
        total_revenue = 0
        for order in orders:
            total_revenue += order.price
            
        context = {
            'orders' : orders,
            'total_revenue' : total_revenue,
            'total_orders' : len(orders)
        }
        return render (request,'dashboard.html',context)
    # checks if the user has the staff group if it exisys it returns true if not error 403 is returned
    def test_func(self):
        return self.request.user.groups.filter(name ='Staff').exists()