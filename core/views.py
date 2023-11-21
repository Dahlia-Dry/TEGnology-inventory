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
import pdfkit
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash

if settings.DEBUG:
    host='http://127.0.0.1:8000' #localhost
else:
    host='http://tegnology.pythonanywhere.com'

home_items = [('Dashboard','','activity'),
              ('Orders','/orders','inbox'),
              ('Inventory','/inventory','package'),
              #('Customers','/customers','users'),
              ('User Profile','/profile','user')]
page_items = [(x[0],os.path.join('../',x[1]), x[2]) for x in home_items]
file_objs = {'invoice':{'obj':Invoice,'form':InvoiceForm,'dateform':InvoiceDateForm},}

@login_required
def dashboard(request):
    products=Product.objects.all()
    delivered = []
    pending = []
    instock=[]
    names = []
    for p in products:
        names.append(p.name)
        qd= Purchase.objects.filter(status__gte=len(Order.Status)-1,product=p)
        delivered.append(sum([d.quantity for d in qd]))
        qp = Purchase.objects.filter(status__lt=len(Order.Status)-1,product=p)
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
def orders(request,pk=None):
    if request.method=='POST':
        print(request.POST)
        if request.POST['form_id']=="edit_order_meta":
            order=get_object_or_404(Order, pipedrive_id=int(request.POST['pk']))
            form = OrderForm(request.POST, instance=order)
            if form.is_valid():
                form.save()
        if request.POST['form_id']=="edit_order_status":
            order=get_object_or_404(Order, pipedrive_id=int(request.POST['pk']))
            form = OrderStatusForm(request.POST, instance=order)
            if form.is_valid():
                order.prev_status_date=order.status_date
                form.save()
        elif request.POST['form_id']=="delete_file":
            filetype = request.POST['filetype']
            order=get_object_or_404(Order, pipedrive_id=int(request.POST['pk']))
            setattr(order,filetype,None)
            order.save()
        elif request.POST['form_id'] =='set_date':
            filetype = request.POST['filetype']
            order=get_object_or_404(Order, pipedrive_id=int(request.POST['pk']))
            file_obj = getattr(order,filetype)
            form = file_objs[filetype]['dateform'](request.POST,instance=file_obj)
            if form.is_valid():
                form.save()
            if order.status < order.Status.INVOICE_SENT.value:
                order.status=order.Status.INVOICE_SENT.value
                order.prev_status_date=order.status_date
                order.status_date=file_obj.sent_date
            order.save()
        elif request.POST['form_id'] =='undo_set_date':
            filetype = request.POST['filetype']
            order=get_object_or_404(Order, pipedrive_id=int(request.POST['pk']))
            file_obj = getattr(order,filetype)
            file_obj.sent_date=None
            file_obj.save()
            if order.status == order.Status.INVOICE_SENT.value:
                order.status=order.status-1
                order.status_date = order.prev_status_date
            order.save()
    queryset = Order.objects.all()
    visible_keys=['customer','last_updated']
    invisible_keys= []
    data = []
    print('PK',pk)
    for item in queryset:
        if pk is not None:
            if item.pipedrive_id==int(pk):
                selected=True
            else:
                selected=False
        else:
            selected=False
        buf=[(selected,item.pipedrive_id,item.get_edit_url(),item.name),item.get_status()]
        for key in visible_keys:
            if key=='last_updated':
                buf.append(item.status_date)
            else:
                buf.append(eval(f'item.{key}'))
        for key in invisible_keys:
            buf.append(eval(f'item.{key}'))
        data.append(buf)
    orders = render_to_string('components/order_table.html',{'visible_keys':visible_keys,
                                                            'invisible_keys':invisible_keys,
                                                             'data':data})
    try:
        selected_order= Order.objects.get(pipedrive_id=int(pk))
        progress= int((selected_order.status/len(Order.Status))*100)
        files= {f:getattr(selected_order,f) for f in file_objs}
        purchases = Purchase.objects.filter(order=selected_order)
        purchase_context={}
        purchase_context['keys'] = ['product','quantity','total']
        purchase_context['data'] = []
        purchase_context['id']='purchasetable'
        for item in purchases:
            buf=[item.id]
            for key in purchase_context['keys']:
                buf.append(eval(f'item.{key}'))
            purchase_context['data'].append(buf)
        purchases=render_to_string('components/purchase_table.html',purchase_context)
    except Exception as e:
        print(e)
        selected_order=None
        progress=0
        files=None
        purchases=None
    context={'menu_items':page_items,
             'currentpage':'Orders',
             'orders':orders,
             'selected_order':selected_order,
             'purchases':purchases,
             'progress_percent':progress,
             'files':files,
             'file_form':{f:file_objs[f]['dateform']() for f in file_objs}}
    return render(request,'orders.html',context)

@login_required
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
        elif request.POST['form_id'] == 'mark_as_delivered':
            pks = request.POST['purchase_pks'].split(',')
            for pk in pks:
                try:
                    instance = Purchase.objects.get(id=pk)
                    instance.status='delivered'
                    instance.save()
                except:
                    pass
    context={'menu_items':page_items,
             'currentpage':'Inventory',
             'entryform':EntryForm(initial={'user':request.user})}
    entries = Entry.objects.all()
    entry_context={}
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
    """
    purchases = Purchase.objects.filter(status='pending')
    purchase_context={}
    purchase_context['keys'] = ['order','status','order_date','product','quantity']
    purchase_context['data'] = []
    purchase_context['id']='purchasetable'
    for item in purchases:
        buf=[item.id]
        for key in purchase_context['keys']:
            buf.append(eval(f'item.{key}'))
        purchase_context['data'].append(buf)
    purchases=render_to_string('components/purchase_table.html',purchase_context)
    context['purchases']= purchases

    deliveries = Purchase.objects.filter(status='delivered')
    delivery_context={}
    delivery_context['keys'] = ['order','status','order_date','product','quantity']
    delivery_context['data'] = []
    delivery_context['id']='deliverytable'
    for item in deliveries:
        buf=[item.id]
        for key in delivery_context['keys']:
            buf.append(eval(f'item.{key}'))
        delivery_context['data'].append(buf)
    deliveries=render_to_string('components/purchase_table.html',delivery_context)
    context['deliveries']= deliveries"""
    return render(request,'inventory.html',context)

@login_required
def profile(request):
    profile=get_object_or_404(Profile,user=request.user)
    context={'menu_items':page_items,
             'currentpage':'User Profile'}
    if request.method == "POST":
        if request.POST['form_id']=="change_password":
            form = PasswordChangeForm(request.user, request.POST)
            if form.is_valid():
                user = form.save()
                update_session_auth_hash(request, user)  # Important!
                messages.success(request, 'Your password was successfully updated!')
            else:
                messages.error(request, 'Please correct the error below.')
        elif request.POST['form_id']=="edit_notification_settings":
            form = ProfileForm(request.POST, instance=profile)
            if form.is_valid():
                form.save()
            context['profile'] = form
            context['popup'] = True
            return render(request,'profile.html',context)
    form=ProfileForm(instance=profile)
    context['profile'] = form
    return render(request,'profile.html',context)

@login_required
def change_password(request):
    form = PasswordChangeForm(request.user)
    return render(request,'components/form_bare.html',{'form':form})

@login_required
def edit_entry(request,pk):
    entry=get_object_or_404(Entry, id=int(pk))
    print(entry)
    form=EntryForm(instance=entry)
    return render(request,'components/edit_obj.html',{'form':form,'pk':pk})

@login_required
def edit_customer(request,pk):
    customer=get_object_or_404(Customer, id=int(pk))
    form=CustomerForm(instance=customer)
    return render(request,'components/edit_obj.html',{'form':form,'pk':pk})

@login_required
def edit_order_status(request,pk):
    order=get_object_or_404(Order, pipedrive_id=int(pk))
    form=OrderStatusForm(instance=order)
    return render(request,'components/edit_obj.html',{'form':form,'pk':pk})

@login_required
def edit_order_meta(request,pk):
    order=get_object_or_404(Order, pipedrive_id=int(pk))
    form=OrderForm(instance=order)
    return render(request,'components/edit_obj.html',{'form':form,'pk':pk})

@login_required
def view_file(request,pk,filetype):
    order_instance = get_object_or_404(Order,pipedrive_id=int(pk))
    print(filetype)
    if filetype == 'invoice':
        instance = order_instance.invoice
        print(instance)
    return redirect(instance.filepath)

@login_required
def gen_file(request,pk,filetype):
    order_instance = get_object_or_404(Order,pipedrive_id=int(pk))
    print(filetype)
    context = {'filetype':filetype,
               'menu_items':page_items,
                'currentpage':'Orders',
                'pipedrive_id':pk}
    filepath = f'{filetype}s/{filetype}-{order_instance.pipedrive_id}.pdf'
    initial = {}
    try:  #delete any previously existing instance
        obj = file_objs[filetype]['obj'].objects.get(filepath=os.path.join(host+settings.MEDIA_URL,filepath))
        initial = {key:obj.__dict__[key] for key in obj.__dict__ if key in InvoiceForm.visible_fields}
        obj.delete()
    except:
        initial['created_date']=order_instance.close_date
        initial['contact_person'] = order_instance.contact_person
        initial['contact_email']=order_instance.contact_email
    form=file_objs[filetype]['form'](initial=initial)
    file_obj = file_objs[filetype]['obj'](filepath=os.path.join(host+settings.MEDIA_URL,filepath))
    print(host)
    print(os.path.join(host+settings.MEDIA_URL,filepath))
    if request.method=='POST':
        if request.POST['form_id'] =='generate_file':
            form = file_objs[filetype]['form'](request.POST,instance=file_obj)
            if form.is_valid():
                form.save()
        elif request.POST['form_id'] =='edit_customer':
            customer=get_object_or_404(Customer, id=int(request.POST['pk']))
            customer_form = CustomerForm(request.POST, instance=customer)
            if customer_form.is_valid():
                customer_form.save()
    context['form']=form
    context['customer']=customer=order_instance.customer
    if filetype == 'invoice':
        purchases = Purchase.objects.filter(order=order_instance)
        line_items = []
        for p in purchases:
            item = {}
            item['name'] = p.product.name
            item['quantity'] = p.quantity
            item['price'] = order_instance.currency+f' {(p.quantity*p.unit_price):.2f}'
            line_items.append(item)
        invoice_context={'logo_path':os.path.join(settings.STATIC_ROOT,'assets/logo.png'),
                     'line_items':line_items}
        file_obj.currency=order_instance.currency
        file_obj.total=order_instance.total
        print('order',order_instance.currency,order_instance.total)
        file_obj.line_items=line_items
        file_obj.save()
        invoice_context['customer'] = customer
        invoice_context['tegnology'] = Customer.objects.get(name='TEGnology Aps')
        invoice_context['invoice'] =file_obj
        output_text=render_to_string('documents/invoice.html',invoice_context)
        pdfkit.from_string(output_text,os.path.join(settings.MEDIA_ROOT,filepath),options={"enable-local-file-access": ""})
        #file_obj.save()
        if request.method=='POST' and 'save' in request.POST:
            print('saving invoice')
            order_instance.invoice=file_obj
            order_instance.save()
            return redirect(os.path.join(host,f'/orders/id={order_instance.pipedrive_id}'))
        context['filepath'] = file_obj.filepath
    return render(request,'file_generate.html',context)

