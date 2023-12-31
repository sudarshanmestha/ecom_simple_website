from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import pre_save
from django.utils.text import slugify
from django.shortcuts import reverse



User = get_user_model()

#checkout( addresses)
class Address(models.Model):
    ADDRESS_CHOICES = (
        ('B', 'Billing'),
        ('S', 'shipping'),
    )


    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address_line_1 = models.CharField(max_length=150)
    address_line_2 = models.CharField(max_length=150)
    city = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
    default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.address_line_1}, {self.address_line_2}, {self.city}, {self.zip_code}"

    class Meta:
        verbose_name_plural = 'Addresses'   

#colour
class ColourVariation(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name
#size
class SizeVariation(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name


####product list view
class Product(models.Model):
    title = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to='product_images')
    description = models.TextField()
    price = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateField(auto_now=True)
    active = models.BooleanField(default=False)
    available_colours = models.ManyToManyField(ColourVariation)
    available_sizes = models.ManyToManyField(SizeVariation)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("cart:product-detail", kwargs={'slug': self.slug}) 

    def get_price(self):
        return "{:.2f}".format(self.price / 100)


# product detail view  (add the item to cart)  
class OrderItem(models.Model):
    order = models.ForeignKey(
        "Order", related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    colour = models.ForeignKey(ColourVariation, on_delete=models.CASCADE)
    size = models.ForeignKey(SizeVariation, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.quantity} x {self.product.title}"

    def get_raw_total_item_price(self): 
        return self.quantity * self.product.price  

    def get_total_item_price(self): 
        price =self.get_raw_total_item_price()
        return "{:.2f}".format(price / 100)

    def get_raw_subtotal(self):
        total=0
        for order_item in self.items.all():
            total += order_item.get_raw_total_item_price()

        

#Cart view (all the item in our cart)
class Order(models.Model):
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField(blank=True, null=True)
    ordered = models.BooleanField(default=False)

    billing_address = models.ForeignKey(Address, related_name='billing_address', blank=True, null=True, on_delete=models.SET_NULL)
    shipping_address = models.ForeignKey(Address, related_name='shipping_address', blank=True, null=True, on_delete=models.SET_NULL)
    
    
    def __str__(self):
        return self.reference_number
    
    @property
    def reference_number(self):
        return f"ORDER-{self.pk}"

    def get_raw_subtotal(self):
        total=0
        for order_item in self.items.all():
            total += order_item.get_raw_total_item_price()
        return total    
    
    def get_subtotal(self):
        subtotal = self.get_raw_subtotal()
        return "{:.2f}".format(subtotal / 100)
    #total
    def get_raw_total(self):
        subtotal = self.get_raw_subtotal()
        # add tax, add delivery, substract discounts
        # total = substract-discount + tax + delivery
        return subtotal
    
    def get_total(self):
        total = self.get_raw_total()
        return "{:.2f}".format(total / 100)

#payments
class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    payment_method = models.CharField(max_length=20, choices=(('PayPal', 'PayPal'),))
    timestamp = models.DateTimeField(default=False)
    successful = models.FloatField()
    amount = models.FloatField()
    raw_response = models.TextField()

    def __str__(self):
        return self.reference_number
    
    @property
    def reference_number(self):
        return f"PAYMENT-{self.order}-{self.pk}"    


def pre_save_product_reciever(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.title)

pre_save.connect(pre_save_product_reciever, sender=Product)
