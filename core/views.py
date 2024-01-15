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
from django.core.files.storage import FileSystemStorage
from pipedrive.client import Client

from .utils import *

client = Client(domain=config('PIPEDRIVE_DOMAIN'))
client.set_api_token(config('PIPEDRIVE_API_TOKEN'))

if settings.DEBUG:
    host='http://127.0.0.1:8000' #localhost
else:
    host='http://tegnology.pythonanywhere.com'

home_items = [('Dashboard','','activity'),
              ('Deals','/deals','briefcase'),
              ('Orders','/orders','inbox'),
              ('Inventory','/inventory','package'),
              ('Customers','/customers','users'),
              ('User Profile','/profile','user'),
              ('Info','https://arc.net/e/5CBAEFB9-943B-4F3B-8A55-5C5E5FECF1AA','info')]
page_items = [(x[0],os.path.join('../',x[1]), x[2]) for x in home_items[:-1]] + [home_items[-1]]
file_objs = {'quotation':{'status':1,'obj':Quotation,'form':QuotationForm},
            'purchase_order':{'status':2,'obj':PurchaseOrder,'form':PurchaseOrderForm},
             'order_confirmation':{'status':3,'obj':OrderConfirmation,'form':OrderConfirmationForm},
            'invoice':{'status':4,'obj':Invoice,'form':InvoiceForm},
            'delivery_notice':{'status':5,'obj':DeliveryNotice,'form':DeliveryForm}}

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
        d_amt = sum([d.quantity for d in qd])
        delivered.append(d_amt)
        qp = Purchase.objects.filter(status__gt=1,status__lt=len(Order.Status)-1,product=p)
        p_amt = sum([p.quantity for p in qp])
        pending.append(p_amt)
        qi = Entry.objects.filter(product=p)
        instock.append(sum([i.quantity for i in qi])-p_amt-d_amt)
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
    sync_pipedrive_latest()
    pk = request.GET.get('id')
    sortby=request.GET.get('sort')
    filterby = request.GET.get('filter')
    #deal with form submissions
    if request.method=='POST':
        order=get_object_or_404(Order, pipedrive_id=int(request.POST['pk']))
        if request.POST['form_id']=="edit_order_status":
            form = OrderStatusForm(request.POST, instance=order)
            if form.is_valid():
                order.prev_status=order.status
                order.prev_status_date=order.status_date
                form.save()
    #apply sort and filter
    queryargs = {'status__gte':1} #get all closed deals
    if filterby=='pending':
        queryargs['status__lt']=len(Order.Status)-1
    elif filterby=='completed':
        queryargs['status__gte']=len(Order.Status)-1
    if sortby=='status-asc':
        queryset=Order.objects.filter(**queryargs).order_by('status')
    elif sortby=='status-desc':
        queryset=Order.objects.filter(**queryargs).order_by('-status')
    elif sortby=='updated-asc':
        queryset=Order.objects.filter(**queryargs).order_by('status_date')
    elif sortby=='updated-desc':
        queryset=Order.objects.filter(**queryargs).order_by('-status_date')   
    else:
        queryset=Order.objects.filter(**queryargs)
    visible_keys=['customer','last_updated']
    invisible_keys= []
    data = []
    for item in queryset:
        if pk is not None:
            if item.pipedrive_id==int(pk):
                selected=True
            else:
                selected=False
        else:
            selected=False
        buf=[(selected,item.pipedrive_id,f"/orders/{item.pipedrive_id}",item.name),item.get_status()]
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
        progress= int(((selected_order.status-1)/(len(Order.Status)-1))*100)
        print(progress)
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
    print(files)
    context={'menu_items':page_items,
             'currentpage':'Orders',
             'orders':orders,
             'selected_order':selected_order,
             'purchases':purchases,
             'sort_options':{'status-asc':'status - asc',
                             'status-desc':'status - desc',
                             'updated-asc':'last updated - asc',
                             'updated-desc':'last updated - desc'},
             'filter_options':{'all': 'all orders',
                               'pending': 'pending orders',
                               'completed': 'completed orders'},
             'sortby':sortby,
             'filterby': filterby,
             'files':files}
    return render(request,'orders.html',context)

@login_required
def order_detail(request,pk):
    order = get_object_or_404(Order, pipedrive_id=int(pk))
    if request.method=='POST':
        if request.POST['form_id']=="edit_order_meta":
            form = OrderForm(request.POST, instance=order)
            if form.is_valid():
                form.save()
        elif request.POST['form_id']=="edit_order_status":
            form = OrderStatusForm(request.POST, instance=order)
            if form.is_valid():
                order.prev_status=order.status
                order.prev_status_date=order.status_date
                form.save()
        elif request.POST['form_id']=="mark_complete":
            form = OrderCompleteForm(request.POST, instance=order)
            if form.is_valid():
                order.prev_status=order.status
                order.prev_status_date=order.status_date
                order.status = 6
                form.save()
        elif request.POST['form_id']=="undo_mark_complete":
            order.status=order.prev_status
            order.status_date=order.prev_status_date
            order.save()
        else:
            filetype = request.POST['filetype']
            if request.POST['form_id']=="delete_file":
                setattr(order,filetype,None)
                order.save()
            elif request.POST['form_id'] =='set_date':
                file_obj = getattr(order,filetype)
                form = gen_file_dateform(file_objs[filetype]['obj'],data=request.POST,instance=file_obj)
                if form.is_valid():
                    order.prev_status=order.status
                    order.status = file_objs[filetype]['status']
                    order.prev_status_date=order.status_date
                    order.status_date=file_obj.sent_date
                    form.save()
                order.save()
            elif request.POST['form_id'] =='undo_set_date':
                file_obj = getattr(order,filetype)
                file_obj.sent_date=None
                file_obj.save()
                order.status=order.prev_status
                order.status_date=order.prev_status_date
                order.save()
            elif request.POST['form_id']=='upload_file':
                print(request.POST)
                upload = request.FILES['file']
                fs = FileSystemStorage()
                doc_type = upload.name.split('.')[-1]
                filename = filetype+'s'+'/'+filetype+'-'+request.POST['pk']+'.'+doc_type
                if os.path.exists(os.path.join(settings.MEDIA_ROOT,filename)):
                    #overwrite old file if exists
                    os.system(f'rm {os.path.join(settings.MEDIA_ROOT,filename)}')
                file_instance = fs.save(filename, upload)
                uploaded_file_url = fs.url(filename)
                if filetype != 'purchase_order':
                    file_obj = file_objs[filetype]['obj'](filepath=os.path.join(host+settings.MEDIA_URL,filename))
                    file_obj.save()
                    setattr(order,filetype,file_obj)
                    order.save()
                else:
                    po=PurchaseOrder.objects.create(filepath=os.path.join(host+settings.MEDIA_URL,filename))
                    form=PurchaseOrderForm(request.POST,instance=po)
                    print(form)
                    if form.is_valid():
                        print(po)
                        #purchase_order.received_date=datetime.date.today()
                        form.save()
                        print(po.received_date)
                        order.purchase_order=po
                        order.save()
    try:
        progress= int(((order.status)/(len(Order.Status)-1))*100)
        print(progress)
        files= {f:getattr(order,f) for f in file_objs}
        file_forms={f:{'date':gen_file_dateform(file_objs[f]['obj'])} for f in file_objs if f!= 'purchase_order'}
        purchases = Purchase.objects.filter(order=order)
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
        order=None
        progress=0
        files=None
        file_forms=None
        purchases=None
    context={'menu_items':page_items,
             'currentpage':'Orders',
             'selected_order':order,
             'purchases':purchases,
             'progress_percent':progress,
             'files':files,
             'file_form':file_forms,
             'complete_form': OrderCompleteForm(),
             }
    return render(request,'order_detail.html',context)

@login_required
def inventory(request):
    if request.method == "POST":
        print(request.POST)
        if request.POST['form_id']=="add_new_entry":
            form = EntryForm(request.POST)
            if form.is_valid():
                entry= form.save(commit=False)
                entry.save()
                send_mail(f"New inventory added by {request.user.username}", 
                            str(entry), 
                            from_email=settings.EMAIL_HOST_USER, 
                            recipient_list=[settings.ADMIN_EMAIL], 
                            fail_silently=False)
        elif request.POST['form_id']=="add_new_product":
            form=ProductForm(request.POST)
            if form.is_valid():
                product=form.save(commit=False)
                #Add to Pipedrive also and fetch id
                response = client.products.create_product({'name':product.name})
                print(response)
                product.pipedrive_id=response['data']['id']
                product.save()
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
             'entryform':EntryForm(initial={'user':request.user}),
             'productform':ProductForm()}
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
    form=OrderStatusForm(instance=order,initial={'status_date':datetime.date.today()})
    return render(request,'components/edit_obj.html',{'form':form,'pk':pk})

@login_required
def mark_sent(request,pk,filetype):
    order=get_object_or_404(Order, pipedrive_id=int(pk))
    form=gen_file_dateform(file_objs[filetype]['obj'])
    return render(request,'components/edit_obj.html',{'form':form,'pk':pk})

@login_required
def edit_order_meta(request,pk):
    order=get_object_or_404(Order, pipedrive_id=int(pk))
    form=OrderForm(instance=order)
    return render(request,'components/edit_obj.html',{'form':form,'pk':pk})

@login_required
def view_file(request,pk,filetype):
    order_instance = get_object_or_404(Order,pipedrive_id=int(pk))
    instance= getattr(order_instance,filetype)
    return redirect(instance.filepath)

@login_required
def upload_file(request,pk,filetype):
    if filetype != 'purchase_order':
        return render(request,'components/upload_file.html',{'pk':pk})
    else:
        return render(request,'components/purchase_order_form.html',{'form':PurchaseOrderForm()})

@login_required
def gen_file(request,pk,filetype):
    order_instance = get_object_or_404(Order,pipedrive_id=int(pk))
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
        initial['created_date']=datetime.date.today()
        initial['contact_person'] = order_instance.contact_person
        initial['contact_email']=order_instance.contact_email
        if request.user.is_authenticated:
            print(request.user.email)
            initial['sender_email'] = request.user.email
    form=file_objs[filetype]['form'](initial=initial)
    file_obj = file_objs[filetype]['obj'](filepath=os.path.join(host+settings.MEDIA_URL,filepath))
    for key in initial:
        setattr(file_obj,key,initial[key])
        file_obj.save()
    if request.method=='POST':
        if request.POST['form_id']=='generate_file':
            form = file_objs[filetype]['form'](request.POST,instance=file_obj)
            if form.is_valid():
                form.save()
        elif request.POST['form_id'] =='edit_customer':
            customer=get_object_or_404(Customer, id=int(request.POST['pk']))
            customer_form = CustomerForm(request.POST, instance=customer)
            if customer_form.is_valid():
                customer_form.save()
    print('DATE',file_obj.created_date)
    context['form']=form
    context['customer']=customer=order_instance.customer
    purchases = Purchase.objects.filter(order=order_instance)
    line_items = []
    for p in purchases:
        item = {}
        item['name'] = p.product.name
        item['quantity'] = p.quantity
        item['price_per'] = p.unit_price
        item['price'] = order_instance.currency+f' {(p.quantity*p.unit_price):.2f}'
        line_items.append(item)
    file_context= {'logo_path':os.path.join(settings.STATIC_ROOT,'assets/logo.png'),
                    'line_items':line_items,'total':f'{order_instance.total:.2f}',
                    'vat':f'{order_instance.vat}','vat_amt':f' {order_instance.total*(order_instance.vat/100):.2f}',
                    'total_vat':f' {order_instance.total*(1+order_instance.vat/100):.2f}','currency':order_instance.currency}
    print(file_context)
    file_obj.currency=order_instance.currency
    file_obj.total=order_instance.total
    print('order',order_instance.currency,order_instance.total)
    file_obj.line_items=line_items
    file_obj.save()
    file_context['customer'] = customer
    file_context['tegnology'] = Customer.objects.get(name='TEGnology Aps')
    if filetype == 'quotation':
        file_context['quotation'] =file_obj
        output_text=render_to_string('documents/quotation.html',file_context)
        pdfkit.from_string(output_text,os.path.join(settings.MEDIA_ROOT,filepath),options={"enable-local-file-access": ""})
        if request.method=='POST' and 'save' in request.POST:
            print('saving quotation')
            order_instance.quotation=file_obj
            order_instance.save()
            if order_instance.status == 0:
                return redirect(os.path.join(host,f'/deals/{order_instance.pipedrive_id}'))
            else:
                return redirect(os.path.join(host,f'/orders/{order_instance.pipedrive_id}'))
        context['filepath'] = file_obj.filepath
    elif filetype=='order_confirmation':
        file_context['order_confirmation'] =file_obj
        try:
            file_context['po_number'] = order_instance.purchase_order.po_number
        except:
            file_context['po_number'] = None
        output_text=render_to_string('documents/order_confirmation.html',file_context)
        pdfkit.from_string(output_text,os.path.join(settings.MEDIA_ROOT,filepath),options={"enable-local-file-access": ""})
        if request.method=='POST' and 'save' in request.POST:
            print('saving order confirmation')
            order_instance.order_confirmation=file_obj
            order_instance.save()
            return redirect(os.path.join(host,f'/orders/{order_instance.pipedrive_id}'))
        context['filepath'] = file_obj.filepath
    elif filetype == 'invoice':
        file_context['invoice'] =file_obj
        output_text=render_to_string('documents/invoice.html',file_context)
        pdfkit.from_string(output_text,os.path.join(settings.MEDIA_ROOT,filepath),options={"enable-local-file-access": ""})
        if request.method=='POST' and 'save' in request.POST:
            print('saving invoice')
            order_instance.invoice=file_obj
            order_instance.save()
            return redirect(os.path.join(host,f'/orders/{order_instance.pipedrive_id}'))
        context['filepath'] = file_obj.filepath
    elif filetype=='delivery_notice':
        file_context['delivery_notice'] =file_obj
        output_text=render_to_string('documents/delivery_notice.html',file_context)
        pdfkit.from_string(output_text,os.path.join(settings.MEDIA_ROOT,filepath),options={"enable-local-file-access": ""})
        if request.method=='POST' and 'save' in request.POST:
            print('saving invoice')
            order_instance.invoice=file_obj
            order_instance.save()
            return redirect(os.path.join(host,f'/orders/{order_instance.pipedrive_id}'))
        context['filepath'] = file_obj.filepath
    return render(request,'file_generate.html',context)

@login_required
def deals(request):
    sync_pipedrive_latest()
    pk = request.GET.get('id')
    sortby=request.GET.get('sort')
    filterby = request.GET.get('filter')
    #deal with form submissions
    if request.method=='POST':
        pass
    #apply sort and filter
    queryargs = {'status':0} #get all open deals
    queryset=Order.objects.filter(**queryargs)
    visible_keys=['customer','last_updated']
    invisible_keys= []
    data = []
    for item in queryset:
        if pk is not None:
            if item.pipedrive_id==int(pk):
                selected=True
            else:
                selected=False
        else:
            selected=False
        buf=[(selected,item.pipedrive_id,f"/deals/{item.pipedrive_id}",item.name),item.get_status()]
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
    print(files)
    context={'menu_items':page_items,
             'currentpage':'Deals',
             'deals':orders,
             'selected_order':selected_order,
             'purchases':purchases}
    return render(request,'deals.html',context)

@login_required
def deal_detail(request,pk):
    order = get_object_or_404(Order, pipedrive_id=int(pk))
    if request.method=='POST':
        if request.POST['form_id']=="edit_order_meta":
            form = OrderForm(request.POST, instance=order)
            if form.is_valid():
                form.save()
        else:
            filetype = request.POST['filetype']
            if request.POST['form_id']=="delete_file":
                setattr(order,filetype,None)
                order.save()
            elif request.POST['form_id'] =='set_date':
                file_obj = getattr(order,filetype)
                form = gen_file_dateform(file_objs[filetype]['obj'],data=request.POST,instance=file_obj)
                if form.is_valid():
                    order.prev_status=order.status
                    order.status = file_objs[filetype]['status']
                    order.prev_status_date=order.status_date
                    order.status_date=file_obj.sent_date
                    form.save()
                order.save()
                return redirect(os.path.join(host,f'/orders/{order.pipedrive_id}'))
            elif request.POST['form_id']=='upload_file':
                print(request.POST)
                upload = request.FILES['file']
                fs = FileSystemStorage()
                doc_type = upload.name.split('.')[-1]
                filename = filetype+'s'+'/'+filetype+'-'+request.POST['pk']+'.'+doc_type
                if os.path.exists(os.path.join(settings.MEDIA_ROOT,filename)):
                    #overwrite old file if exists
                    os.system(f'rm {os.path.join(settings.MEDIA_ROOT,filename)}')
                file_instance = fs.save(filename, upload)
                uploaded_file_url = fs.url(filename)
                file_obj = file_objs[filetype]['obj'](filepath=os.path.join(host+settings.MEDIA_URL,filename))
                file_obj.save()
                setattr(order,filetype,file_obj)
                order.save()
    try:
        purchases = Purchase.objects.filter(order=order)
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
        file_forms={'quotation':{'date':gen_file_dateform(file_objs['quotation']['obj'])}}
    except Exception as e:
        print(e)
        order=None
        purchases=None
        file_forms = None
    context={'menu_items':page_items,
             'currentpage':'Deals',
             'selected_order':order,
             'purchases':purchases,
             'filetype':'quotation',
             'file_obj':order.quotation,
             'file_form':file_forms}
    return render(request,'deal_detail.html',context)

def customers(request):
    context={'menu_items':page_items,
             'currentpage':'Customers'}
    customers = Customer.objects.all()
    customer_context={}
    customer_context['keys'] = []
    customer_context['data'] = []
    for item in customers:
        #buf=[item.get_edit_url()]
        buf=[item.id]
        for key in customer_context['keys']:
            buf.append(eval(f'item.{key}'))
        buf.append(item.id)
        customer_context['data'].append(buf)
    customers=render_to_string('components/customer_table.html',customer_context)
    context['customers']= customers
    return render(request,'customers.html',context)