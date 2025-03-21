from django.db import models
from django.conf import settings

# Create your models here.

class User(models.Model):
    name = models.CharField(max_length=200)
    user_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    password = models.CharField(max_length=50)
    address = models.CharField(max_length=100)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    aadhar_card_image = models.ImageField(upload_to='aadhar_cards/', null=True, blank=True) 
    status = models.CharField(max_length=10, default='accepted')
    otp = models.CharField(max_length=6, default='0') 
    otp_status = models.CharField(max_length=15, default='Not Verified')
    # New field to track if the user is allowed to sell products.
    allow_to_sell = models.BooleanField(default=True)  
    user_fingerprint = models.ImageField(upload_to='images/fingerprints', null=True, blank=True)  

    def __str__(self):
        return self.name
    


class AadhaarDetail(models.Model):
    user = models.OneToOneField('User', on_delete=models.CASCADE, related_name='aadhaar_detail')
    aadhaar_number = models.CharField(max_length=12, unique=True, null=True, blank=True)
    name = models.CharField(max_length=200, null=True, blank=True)  # Allow null and blank
    date_of_birth = models.DateField(null=True, blank=True)  # Allow null and blank
    gender = models.CharField(max_length=10, null=True, blank=True)  # Allow null and blank
    address = models.TextField(null=True, blank=True)  # Allow null and blank

    def __str__(self):
        return f"Aadhaar Details for {self.name}"


class Craft(models.Model):
    CATEGORY_CHOICES = [
        ('Electronics', 'Electronics'),
        ('Home Appliances', 'Home Appliances'),
        ('Furniture', 'Furniture'),
        ('Clothing', 'Clothing'),
        ('Footwear', 'Footwear'),
        ('Books', 'Books'),
        ('Toys', 'Toys'),
        ('Automobiles', 'Automobiles'),
        ('Sports Equipment', 'Sports Equipment'),
        ('Others', 'Others'),
    ]

    STATE_CHOICES = [
        ('AP', 'Andhra Pradesh'),
        ('AR', 'Arunachal Pradesh'),
        ('AS', 'Assam'),
        ('BR', 'Bihar'),
        ('CT', 'Chhattisgarh'),
        ('GA', 'Goa'),
        ('GJ', 'Gujarat'),
        ('HR', 'Haryana'),
        ('HP', 'Himachal Pradesh'),
        ('JK', 'Jammu and Kashmir'),
        ('JH', 'Jharkhand'),
        ('KA', 'Karnataka'),
        ('KL', 'Kerala'),
        ('MP', 'Madhya Pradesh'),
        ('MH', 'Maharashtra'),
        ('MN', 'Manipur'),
        ('ML', 'Meghalaya'),
        ('MZ', 'Mizoram'),
        ('NL', 'Nagaland'),
        ('OR', 'Odisha'),
        ('PB', 'Punjab'),
        ('RJ', 'Rajasthan'),
        ('SK', 'Sikkim'),
        ('TN', 'Tamil Nadu'),
        ('TG', 'Telangana'),
        ('TR', 'Tripura'),
        ('UP', 'Uttar Pradesh'),
        ('UT', 'Uttarakhand'),
        ('WB', 'West Bengal'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    # materials_used = models.CharField(max_length=255, blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Pottery')
    image = models.ImageField(upload_to='craft_images/', blank=True, null=True)
    video = models.FileField(upload_to='craft_videos/', blank=True, null=True)
    state = models.CharField(max_length=50, choices=STATE_CHOICES, default='AP') 
    city = models.CharField(max_length=100)
    pin_code = models.CharField(max_length=6)
    admin_status = models.CharField(max_length=10, default='pending')
    date_added = models.DateTimeField(auto_now_add=True, null=True)
    # New Fields
    brand_name = models.CharField(max_length=100, blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.name




class WishlistItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    craft = models.ForeignKey(Craft, on_delete=models.CASCADE) 

    def __str__(self):
        return f"{self.user.username}'s Wishlist: {self.craft.name}"




class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    craft = models.ForeignKey(Craft, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def total_price(self):
        return self.craft.price * self.quantity

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    crafts = models.ManyToManyField(Craft, through='OrderItem')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10,default='pending')
    payment_status = models.CharField(max_length=10,default='Online')
    delivery_status = models.CharField(max_length=10, default='pending')



class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    craft = models.ForeignKey(Craft, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    



from django.db import models

class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    Order = models.ForeignKey(Order, on_delete=models.CASCADE)
    user_name = models.CharField(max_length=255)
    user_email = models.EmailField()
    rating = models.IntegerField()
    additional_comments = models.TextField()
    sentiment = models.CharField(max_length=20, null=True)  # Add this field to store the sentiment
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'feedback'
