from django.conf import settings
from django.contrib import messages
from django.shortcuts import get_object_or_404, reverse, redirect
from django.views import generic
from .forms import AddToCartForm, AddressForm
from .models import Product, OrderItem, Address
from .utils import get_or_set_order_session
# Create your views here.

class ProductListView(generic.ListView):
    template_name = 'cart/product_list.html'
    queryset = Product.objects.all()


class ProductDetailView(generic.FormView):
    template_name = 'cart/product_detail.html'
    
    form_class = AddToCartForm
    def get_object(self):
        return get_object_or_404(Product, slug=self.kwargs['slug'])

    def get_success_url(self):
        return reverse('cart:summary')  #TODO: CART

    def get_form_kwargs(self):
        kwargs = super(ProductDetailView, self).get_form_kwargs()
        kwargs["product_id"] = self.get_object().id
        return kwargs  

    def form_valid(self, form):
        order= get_or_set_order_session(self.request)
        product = self.get_object()

        item_filter = order.items.filter(
            product=product,
            colour= form.cleaned_data['colour'],
            size= form.cleaned_data['size'],
            )
        if item_filter.exists():
            item = item_filter.first()
            item.quantity = int(form.cleaned_data['quantity'])
            item.save()
        else:
            new_item = form.save(commit=False)
            new_item.product = product
            new_item.order = order
            new_item.save()

        return super(ProductDetailView, self).form_valid(form)
           
    def get_context_data(self, **kwargs):
        context = super(ProductDetailView, self).get_context_data(**kwargs)
        context['product'] = self.get_object()

        return context 


class CartView(generic.TemplateView):
   template_name = "cart/cart.html"
   def get_context_data(self, **kwargs):
        context = super(CartView, self).get_context_data(**kwargs)
        context["order"] = get_or_set_order_session(self.request)

        return context 


class IncreaseQuantityView(generic.View):
    def get(self, request, *args, **kwargs):
        order_item = get_object_or_404(OrderItem, id=kwargs['pk'])
        order_item.quantity += 1
        order_item.save()
        return redirect("cart:summary")



class DecreaseQuantityView(generic.View):
    def get(self, request, *args, **kwargs):
        order_item = get_object_or_404(OrderItem, id=kwargs['pk'])

        if order_item.quantity <=1:
            order_item.delete()
        else:
            order_item.quantity -= 1
            order_item.save()
        return redirect("cart:summary")    


class RemoveFromView(generic.View):
    def get(self, request, *args, **kwargs):
        order_item = get_object_or_404(OrderItem, id=kwargs['pk'])
        order_item.delete()
        
        
        return redirect("cart:summary")


class CheckoutView(generic.FormView):
    template_name = "cart/checkout.html"
    form_class = AddressForm

        
    def form_valid(self, form):
        order = get_or_set_order_session(self.request)
        selected_shipping_address = form.cleaned_data.get(
            'selected_shipping_address')
        selected_billing_address = form.cleaned_data.get(
            'selected_billing_address')
        
        if selected_shipping_address:
            order.shipping_address =selected_shipping_address
        else:
            address = Address.objects.create(
                address_type= 'S',
                user= self.request.user,
                address_line_1=form.cleaned_data['shipping_address_line_1'],
                address_line_2=form.cleaned_data['shipping_address_line_2'],
                zip_code=form.cleaned_data['shipping_zip_code'],
                city=form.cleaned_data['shipping_city'],
            )
            order.shipping_address == address
        

        if selected_billing_address:
            order.billing_address =selected_billing_address
        else:
            address = Address.objects.create(
                address_type= 'B',
                user= self.request.user,
                address_line_1=form.cleaned_data['billing_address_line_1'],
                address_line_2=form.cleaned_data['billing_address_line_2'],
                zip_code=form.cleaned_data['billing_zip_code'],
                city=form.cleaned_data['billing_city'],
            )
            order.billing_address == address
        order.save()


        messages.info(self.request, "You have successfully added addresses.")    
        return super(CheckoutView, self).form_valid(form)
        
    def get_success_url(self):
        return reverse("cart:payment") 

    def get_form_kwargs(self):
        kwargs = super(CheckoutView, self).get_form_kwargs()
        kwargs["user_id"] = self.request.user.id
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(CheckoutView, self).get_context_data(**kwargs)
        context["order"] = get_or_set_order_session(self.request)

        return context      

class PaymentView(generic.TemplateView):
    template_name = 'cart/payment.html'

    def get_context_data(self, **kwargs):
        context = super(PaymentView, self).get_context_data(**kwargs)
        context["PAYPAL_CLIENT_ID"] = settings.PAYPAL_CLIENT_ID

        return context  
        

