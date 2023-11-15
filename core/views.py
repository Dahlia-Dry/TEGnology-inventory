from django.shortcuts import render, redirect
from .models import *
from django.template.loader import render_to_string
from django.conf import settings
import plotly.graph_objects as go
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from .forms import *
import os
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail

if settings.DEBUG:
    host='http://127.0.0.1:8000' #localhost
else:
    host=''

home_items = [('Dashboard','','activity'),
              ('Orders','/orders','inbox'),
              ('Inventory','/inventory','package'),
              ('Customers','/customers','users'),
              ('User Profile','/profile','user')]
page_items = [(x[0],os.path.join('../',x[1]), x[2]) for x in home_items]

@login_required
def dashboard(request):
    products=Product.objects.all()
    delivered = []
    pending = []
    instock=[]
    names = []
    for p in products:
        names.append(p.name)
        qd = Purchase.objects.filter(status='delivered',product=p)
        delivered.append(sum([d.quantity for d in qd]))
        qp = Purchase.objects.filter(status='pending',product=p)
        pending.append(sum([p.quantity for p in qp]))
        qi = Entry.objects.filter(product=p)
        instock.append(sum([i.quantity for i in qi]))
    inventory=go.Figure(data=[
        go.Bar(name='In Stock',x=names,y=instock,marker_color='#bc2a1a'),
        go.Bar(name='Pending', x=names, y=pending,marker_color='#abdae1'),
        go.Bar(name='Delivered', x=names, y=delivered,marker_color='#1d3d3d'),
    ])
    context={'menu_items':home_items,
             'currentpage':'Dashboard',
             'inventorychart':inventory.to_html()}
    return render(request,'dashboard.html',context)

@login_required
def orders(request):
    queryset = Order.objects.all()
    keys=['name','pipedrive_id','last_updated','close_date']
    data = []
    for item in queryset:
        buf=[(item.pipedrive_id,item.get_edit_url(),item.name)]
        for key in keys[1:]:
            buf.append(eval(f'item.{key}'))
        data.append(buf)
        print(buf)
    orders = render_to_string('components/order_table.html',{'keys':keys,'data':data})
    context={'menu_items':page_items,
             'currentpage':'Orders',
             'orders':orders}
    return render(request,'orders.html',context)

def inventory(request):
    if request.method == "POST":
        print(request.POST)
        if request.POST['form_id']=="add_new_entry":
            form = EntryForm(request.POST)
            if form.is_valid():
                entry= form.save(commit=False)
                entry.save()
                send_mail("New inventory added", 
                            "new inventory :0", 
                            from_email=settings.EMAIL_HOST_USER, 
                            recipient_list=[settings.ADMIN_EMAIL], 
                            fail_silently=False)
        elif request.POST['form_id'] == "delete_entries":
            pks = request.POST['entry_pks'].split(',')
            for pk in pks:
                try:
                    instance = Entry.objects.get(id=pk)
                    instance.delete()
                except:
                    pass
        elif request.POST['form_id'] =='edit_entries':
            print(request.POST)
            entry=get_object_or_404(Entry, id=int(request.POST['pk']))
            form = EntryForm(request.POST, instance=entry)
            if form.is_valid():
                form.save() 
    context={'menu_items':page_items,
             'currentpage':'Inventory',
             'entryform':EntryForm()}
    entries = Entry.objects.all()
    #context['add_entry_link'] = host+'/admin/core/entry/add/'
    entry_context={}
    entry_context['id']='entrytable'
    entry_context['keys'] = ['product','date','quantity','user']
    entry_context['data'] = []
    for item in entries:
        #buf=[item.get_edit_url()]
        buf=[item.id]
        for key in entry_context['keys']:
            buf.append(eval(f'item.{key}'))
        buf.append(item.id)
        entry_context['data'].append(buf)
    entries=render_to_string('components/entry_table.html',entry_context)
    context['entries']= entries

    purchases = Purchase.objects.filter(status='pending')
    context['add_purchase_link'] = host+'/admin/core/purchase/add/'
    purchase_context={}
    purchase_context['id']='purchasetable'
    purchase_context['keys'] = ['order','status','order_date','product','quantity']
    context['entry_keys'] = entry_context['keys']
    purchase_context['data'] = []
    for item in purchases:
        buf=[item.get_edit_url(),f"""<td><a href= "{item.order.get_edit_url()}" title="Edit in Pipedrive">{item.order.name}</a></td>"""]
        for key in purchase_context['keys'][1:]:
            buf.append(eval(f'item.{key}'))
        purchase_context['data'].append(buf)
    purchases=render_to_string('components/purchase_table.html',purchase_context)
    context['purchases']= purchases

    deliveries = Purchase.objects.filter(status='delivered')
    delivery_context={}
    delivery_context['id']='deliverytable'
    delivery_context['keys'] = ['order','status','order_date','product','quantity']
    delivery_context['data'] = []
    for item in deliveries:
        buf=[item.get_edit_url(),f"""<td><a href= "{item.order.get_edit_url()}" title="Edit in Pipedrive">{item.order.name}</a></td>"""]
        for key in delivery_context['keys'][1:]:
            buf.append(eval(f'item.{key}'))
        delivery_context['data'].append(buf)
    deliveries=render_to_string('components/purchase_table.html',delivery_context)
    context['deliveries']= deliveries
    return render(request,'inventory.html',context)

def edit_entry(request,pk):
    entry=get_object_or_404(Entry, id=int(pk))
    print(entry)
    form=EntryForm(instance=entry)
    return render(request,'components/edit_entry.html',{'form':form,'pk':pk})

def profile(request):
    profile=get_object_or_404(Profile,user=request.user)
    context={'menu_items':page_items,
             'currentpage':'User Profile'}
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
        context['profile'] = form
        context['popup'] = True
        return render(request,'profile.html',context)
    else:
        form=ProfileForm(instance=profile)
        context['profile'] = form
        return render(request,'profile.html',context)