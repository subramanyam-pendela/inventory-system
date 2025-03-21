from django.shortcuts import render,redirect,HttpResponse,get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from userapp.models import *
from adminapp.models import *
from django.contrib import messages
import random
from django.core.files.storage import FileSystemStorage
from django.views.decorators.http import require_POST
from django.contrib.auth import logout
from userapp.models import *
from .decorators import session_required
from django.http import HttpResponseForbidden

def user_logout(request):
    logout(request)
    messages.info(request,"Logout Successfully ")
    return redirect('user_login')

def generate_otp(length=4):
    otp = ''.join(random.choices('0123456789', k=length))
    return otp



def index(request):
    events = Event.objects.all()
    context = {'events': events}
    return render(request, "user/index.html", context)


def about(request):
    return render(request, "user/about.html")


def video(request,craft_id):
    craft = get_object_or_404(Craft, pk=craft_id)
    return render(request, 'user/video.html', {'craft': craft})







def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('name')
        password = request.POST.get('password')
        if username == "admin"  and password == "admin":
            messages.success(request, 'Login Successfully.')
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Invalid username or password. Please try again.')
    return render(request, "user/admin-login.html")

def contact(request):
    return render(request, "user/contact.html")



import os
import uuid
import re
import pytesseract
import cv2
from datetime import datetime
from django.conf import settings
from django.core.mail import send_mail
from django.contrib import messages
from django.db import transaction
from django.shortcuts import render, redirect
from .models import User, AadhaarDetail



from django.core.files.storage import FileSystemStorage
import cv2
import os

from django.conf import settings
import os

def process_fingerprint_image(fingerprint_image):
    """
    Processes and saves the fingerprint image using correct paths relative to MEDIA_ROOT.
    """
    # Save original fingerprint to 'fingerprints' directory under MEDIA_ROOT
    fingerprints_dir = os.path.join(settings.MEDIA_ROOT, 'fingerprints')
    fs = FileSystemStorage(location=fingerprints_dir)
    filename = fs.save(fingerprint_image.name, fingerprint_image)
    
    # Read the saved image
    original_path = fs.path(filename)
    img = cv2.imread(original_path, cv2.IMREAD_GRAYSCALE)
    
    # Apply thresholding
    _, img_threshold = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
    
    # Save processed image to 'processed_fingerprints' under MEDIA_ROOT
    processed_dir = os.path.join(settings.MEDIA_ROOT, 'processed_fingerprints')
    os.makedirs(processed_dir, exist_ok=True)
    
    processed_filename = f'processed_{filename}'
    processed_path = os.path.join(processed_dir, processed_filename)
    cv2.imwrite(processed_path, img_threshold)
    
    # Return relative path from MEDIA_ROOT
    return os.path.join('processed_fingerprints', processed_filename)



# Configure Tesseract path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def send_otp_email(user_email, otp):
    """Send OTP to the user's email."""
    print(f"Sending OTP email to {user_email} with OTP {otp}")
    subject = 'Your OTP for Registration'
    message = f'Your OTP is {otp}. Valid for 10 minutes.'
    from_email = settings.DEFAULT_FROM_EMAIL
    send_mail(subject, message, from_email, [user_email])

def preprocess_image(image_path):
    """Enhanced image preprocessing for better OCR accuracy."""
    print(f"Preprocessing image at {image_path}")
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Apply adaptive thresholding
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                  cv2.THRESH_BINARY, 11, 2)
    # Remove noise
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    print("Image preprocessing completed.")
    return cleaned

def extract_aadhaar_details(image_path):
    """Extract details from Aadhaar card image using OCR."""
    print(f"Extracting Aadhaar details from image at {image_path}")
    processed_img = preprocess_image(image_path)  # Preprocess the image
    
    # Perform OCR using Tesseract
    text = pytesseract.image_to_string(processed_img, lang='eng+hin')
    print(f"OCR text extracted: {text}")  # Print the OCR output
    
    # Now process the extracted text
    return process_extracted_text(text)



def process_extracted_text(text):
    """Process OCR text to extract Aadhaar details."""
    print("Processing extracted text for Aadhaar details.")
    details = {}

    # Aadhaar number extraction
    aadhaar_match = re.search(r'\b(\d{4}[-\s]?\d{4}[-\s]?\d{4})\b', text)
    if aadhaar_match:
        details['aadhaar_number'] = aadhaar_match.group(1).replace(' ', '').replace('-', '')
        print(f"Aadhaar number extracted: {details['aadhaar_number']}")

    # Name extraction
    name_match = re.search(
        r'(Name|नाम)[:\s-]*\n?([A-Za-z\s]+(?:\n[A-Za-z\s]+)?)\n',
        text, 
        re.IGNORECASE | re.MULTILINE
    )
    if name_match:
        details['name'] = ' '.join(name_match.group(2).split())
        print(f"Name extracted: {details['name']}")

    # Enhanced Date of Birth extraction
    dob_patterns = [
        r'(DOB|Date of Birth|जन्म तिथि)[:\s-]*(\d{2}[\/\-]\d{2}[\/\-]\d{4})',
        r'\b(\d{2}/\d{2}/\d{4})\b',
        r'\b(\d{2}-\d{2}-\d{4})\b',
        r'(Year of Birth|जन्म वर्ष)[:\s-]*(\d{4})'
    ]
    
    for pattern in dob_patterns:
        dob_match = re.search(pattern, text, re.IGNORECASE)
        if dob_match:
            date_str = dob_match.group(2) if len(dob_match.groups()) > 1 else dob_match.group(1)
            try:
                # Handle different date formats
                date_str = date_str.replace('-', '/')
                details['date_of_birth'] = datetime.strptime(date_str, '%d/%m/%Y').date()
                print(f"Date of birth extracted: {details['date_of_birth']}")
                break
            except ValueError:
                try:
                    # Handle year-only format (fallback to 01/01/YYYY)
                    if len(date_str) == 4:
                        details['date_of_birth'] = datetime.strptime(f'01/01/{date_str}', '%d/%m/%Y').date()
                        print(f"Year extracted as Date of birth: {details['date_of_birth']}")
                        break
                except:
                    continue

    # Gender extraction with Hindi support
    gender_match = re.search(
        r'(Gender|लिंग)[:\s-]*([MF]|Male|Female|पुरुष|महिला)',
        text, 
        re.IGNORECASE
    )
    if gender_match:
        gender = gender_match.group(2).upper()
        if gender in ['M', 'पुरुष', 'MALE']:
            details['gender'] = 'Male'
            print("Gender extracted: Male")
        elif gender in ['F', 'महिला', 'FEMALE']:
            details['gender'] = 'Female'
            print("Gender extracted: Female")

    # Address extraction with improved multi-line handling
    address_match = re.search(
        r'(Address|पता)[:\s-]*\n((?:.*\n){2,5}?)(?=\d{6}|DOB|Mobile|Year)',
        text, 
        re.IGNORECASE | re.MULTILINE
    )
    if address_match:
        details['address'] = ' '.join([line.strip() for line in address_match.group(2).split('\n') if line.strip()])
        print(f"Address extracted: {details['address']}")

    print("Aadhaar details processed successfully.")
    return details


def generate_otp():
    """Generate 6-digit OTP."""
    otp = str(uuid.uuid4().int)[:6]
    print(f"Generated OTP: {otp}")
    return otp
















import time
import os

def cleanup_temp_files(*paths):
    """Cleanup temporary files with retry mechanism."""
    print("Cleaning up temporary files.")
    for path in paths:
        if path and os.path.exists(path):
            attempts = 3
            for attempt in range(attempts):
                try:
                    os.remove(path)
                    print(f"Removed file: {path}")
                    break  # Successfully removed the file, no need to retry
                except OSError as e:
                    if e.errno == 32:  # File is being used by another process
                        print(f"File is in use, retrying... Attempt {attempt + 1}")
                        time.sleep(1)  # Retry after 1 second
                    else:
                        raise  # If it's a different error, raise the exception


@transaction.atomic
def user_register(request):
    """Registration view with comprehensive validation."""
    print("User registration started.")
    if request.method == 'POST':
        aadhar_path = None
        try:
            # Extract form data with safety checks
            form_data = {
                'name': request.POST.get('name', '').strip(),
                'user_name': request.POST.get('username', '').strip(),
                'email': request.POST.get('email', '').lower().strip(),
                'phone': request.POST.get('phone', '').strip(),
                'password': request.POST.get('password', '').strip(),
                'address': request.POST.get('address', '').strip(),
                'profile_picture': request.FILES.get('profile'),
                'aadhar_card_image': request.FILES.get('aadhar_card'),
                'fingerprint': request.FILES.get('fingerprint')
            }

            print(f"Form data received: {form_data}")

            # Validate required fields
            if not all([form_data['email'], form_data['password'], form_data['aadhar_card_image'], form_data['fingerprint']]):
                messages.error(request, 'Missing required fields: Email, Password, or Aadhaar Card')
                print("Missing required fields")
                return redirect('user_register')

            # Validate email format
            if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w{2,4}$', form_data['email']):
                messages.error(request, 'Invalid email format')
                print("Invalid email format")
                return redirect('user_register')

            # Check existing user by email
            if User.objects.filter(email=form_data['email']).exists():
                messages.error(request, 'Email already registered')
                print("Email already registered")
                return redirect('user_register')

            # Process Aadhaar card
            temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')
            os.makedirs(temp_dir, exist_ok=True)
            aadhar_path = os.path.join(temp_dir, f"aadhar_{uuid.uuid4().hex}.png")
            
            print(f"Saving Aadhaar image to: {aadhar_path}")
            with open(aadhar_path, 'wb+') as f:
                for chunk in form_data['aadhar_card_image'].chunks():
                    f.write(chunk)

                # Attempt to extract Aadhaar details
                aadhaar_details = extract_aadhaar_details(aadhar_path)
                print(f"Aadhaar details extracted: {aadhaar_details}")

                # Check if Aadhaar number is valid
                if 'aadhaar_number' not in aadhaar_details or not aadhaar_details['aadhaar_number']:
                    # Immediately inform the user and stop the registration
                    messages.error(request, 'Please provide a clear Aadhaar image with a valid Aadhaar number.')
                    print("Aadhaar number extraction failed")
                    return redirect('user_register')  # Do not continue with the registration

                # Check if Aadhaar number already exists in the AadhaarDetail model
                if AadhaarDetail.objects.filter(aadhaar_number=aadhaar_details['aadhaar_number']).exists():
                    messages.error(request, 'This Aadhaar number is already registered by another user. Please use a different Aadhaar card.')
                    print("Aadhaar number already in use")
                    return redirect('user_register')  # Do not continue with the registration


            if form_data.get('fingerprint'):
                processed_fingerprint_path = process_fingerprint_image(form_data['fingerprint'])
                print(f"Processed fingerprint image saved to: {processed_fingerprint_path}")
            else:
                print("No fingerprint uploaded")


            # Create user and store Aadhaar image
            user = User.objects.create(
                name=form_data['name'],
                user_name=form_data['user_name'],
                email=form_data['email'],
                phone=form_data['phone'],
                password=form_data['password'],  # Should be hashed in production
                address=form_data['address'],
                profile_picture=form_data['profile_picture'],
                aadhar_card_image=form_data['aadhar_card_image'],  # Save the Aadhaar image
                otp=generate_otp(),
                user_fingerprint=processed_fingerprint_path
            )

            print(f"User created with ID: {user.id}")

            # Save Aadhaar details in the AadhaarDetail model
            AadhaarDetail.objects.create(
                user=user,
                aadhaar_number=aadhaar_details['aadhaar_number'],
                name=aadhaar_details.get('name', None),
                date_of_birth=aadhaar_details.get('date_of_birth', None),
                gender=aadhaar_details.get('gender', None),
                address=aadhaar_details.get('address', None)
            )

            # Send OTP
            send_otp_email(user.email, user.otp)

            # No file cleanup or deletion here as per your requirement

            request.session['otp_user_id'] = user.pk
            print("Redirecting to OTP verification")
            return redirect('user_otp')

        except ValueError as ve:
            messages.error(request, f'Aadhaar validation error: {str(ve)}')
            print(f"Aadhaar validation error: {str(ve)}")
            return redirect('user_register')
        except Exception as e:
            messages.error(request, f'Registration failed: {str(e)}')
            print(f"Registration failed: {str(e)}")
            return redirect('user_register')

    return render(request, 'user/user-register.html')





def otp(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        user_id = request.session.get("otp_user_id")
        user = User.objects.get(pk=user_id)
        print("Entered OTP:", entered_otp)
        if entered_otp:
            if entered_otp == user.otp:
                user.otp_status = "verified"
                user.save()
                messages.success(request, 'OTP validated successfully.')
                user_id = user.pk
                request.session['user_verified_id'] = user_id
                return redirect('user_login')
            else:
                messages.error(request, 'Invalid OTP. Please try again.')
                return redirect('user_otp')
        else:
            messages.error(request, 'Please enter the OTP.')
            return redirect('user_otp')
    return render(request, "user/otp.html")










from django.core.files.storage import default_storage
import cv2

import numpy as np

import cv2
import numpy as np
from django.core.files.storage import default_storage

import numpy as np

def compare_fingerprints(uploaded_fingerprint, stored_fingerprint_path):
    """
    Compares uploaded fingerprint with stored one using OpenCV histograms.
    """
    # Read uploaded fingerprint
    uploaded_content = uploaded_fingerprint.read()
    uploaded_fingerprint.seek(0)
    np_uploaded = np.frombuffer(uploaded_content, np.uint8)
    img1 = cv2.imdecode(np_uploaded, cv2.IMREAD_GRAYSCALE)
    
    # Read stored fingerprint
    stored_file = default_storage.open(stored_fingerprint_path, 'rb')
    stored_content = stored_file.read()
    stored_file.close()
    np_stored = np.frombuffer(stored_content, np.uint8)
    img2 = cv2.imdecode(np_stored, cv2.IMREAD_GRAYSCALE)
    
    # Process images with thresholding
    _, img1_threshold = cv2.threshold(img1, 127, 255, cv2.THRESH_BINARY)
    _, img2_threshold = cv2.threshold(img2, 127, 255, cv2.THRESH_BINARY)
    
    # Compute histograms (256 bins for 8-bit grayscale)
    hist1 = cv2.calcHist([img1_threshold], [0], None, [256], [0, 256])
    hist2 = cv2.calcHist([img2_threshold], [0], None, [256], [0, 256])
    
    # Normalize histograms to CV_32F type
    cv2.normalize(hist1, hist1, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)
    cv2.normalize(hist2, hist2, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)
    
    # Calculate similarity score
    score = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
    return score







def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        fingerprint = request.FILES.get('fingerprint')
        try:
            user = User.objects.get(email=email)
            print(f"User found with email: {email}")
            if user.password == password:
                print("Password matched.")
                if user.status == "accepted":
                    if user.otp_status == "verified":
                        print("User account is approved.")
                        similarity_score = compare_fingerprints(fingerprint, user.user_fingerprint.name)  # Use the filename, not path
                        print(f"Fingerprint similarity score: {similarity_score}")
                        if similarity_score >= 0.9:
                            request.session['user_login_id'] = user.pk
                            print("Session after login:", dict(request.session))
                            messages.success(request, 'Login successful.')
                            return redirect('user_dashboard')
                        else:
                            print("Fingerprint does not match.")
                            messages.error(request, 'Fingerprint does not match. Please try again.')
                            return redirect('user_login')
                    else:
                        print("Otp Validation is not complted.")
                        messages.error(request, 'Otp Validation is not complted.')
                        return redirect('user_login')
                else:
                    print("User account is not yet approved.")
                    messages.error(request, 'Your account is Temporary on hold.')
                    return redirect('user_login')
            else:
                print("Invalid password.")
                messages.error(request, 'Invalid password.')
                return redirect('user_login')
        except User.DoesNotExist:
            print("User does not exist.")
            messages.error(request, 'User does not exist.')
            return redirect('user_login')
    return render(request, "user/user-login.html")




@session_required
def user_dashboard(request):
    
    return render(request,"user/user-dashboard.html")

@session_required
def user_explore(request):
    return render(request,"user/explore.html")





def payment(request):
    return render(request,"user/payment.html")

@session_required

def cartpage(request):
    user_id = request.session.get('user_login_id')
    user = get_object_or_404(User, pk=user_id)
    
    
    try:
        cart = Cart.objects.get(user=user)
        cart_items = cart.items.all()  
        
        
        subtotal = sum(item.craft.price * item.quantity for item in cart_items)
        
        
        context = {
            'cart_items': cart_items,
            'subtotal': subtotal,
        }
    except Cart.DoesNotExist:
        
        context = {
            'cart_items': [],
            'subtotal': 0,
        }

    return render(request, "user/shoping-cart.html", context)


@session_required

def seller_dashboard(request):
    user_id = request.session.get('user_login_id')
    user = User.objects.get(pk=user_id)
    
    if request.method == 'POST':

        if not user.allow_to_sell:
            messages.error(
                request,
                "You are not allowed to sell any product on this platform. Please contact the admin for further assistance."
            )
            return redirect('user_dashboard')
    
        name = request.POST.get('craftname')
        price = request.POST.get('craftprice')
        description = request.POST.get('description')
        category = request.POST.get('craftCategory')
        state = request.POST.get('state')
        city = request.POST.get('city')
        pin_code = request.POST.get('pincode')

        if 'craftimg' in request.FILES:
            craft_image = request.FILES['craftimg']
            
            
            
        else:
            craft_image = None

        if 'craftvideo' in request.FILES:
            craft_video = request.FILES['craftvideo']
        else:
            craft_video = None

        craft = Craft(
            user=user,
            name=name,
            price=price,
            description=description,
            category=category,
            image=craft_image,
            state=state,
            video=craft_video,
            city=city,
            pin_code=pin_code
        )
        craft.save()
        messages.success(request,"Item Added Successfully !")
        return redirect('seller_dashboard')
    else:

        return render(request, "user/user-seller-dashboard.html")
    
@session_required

def category_view(request, category_name):
    crafts_in_category = Craft.objects.filter(category=category_name, admin_status='approved')
    return render(request, 'user/craft-page.html', {
        'crafts': crafts_in_category,
        'category_name': category_name  
    })



from django.http import JsonResponse
def get_craft_details(request, id):
    craft = Craft.objects.get(id=id)
    return JsonResponse({
        'name': craft.name,
        'image_url': craft.image.url if craft.image else '',
        'price': craft.price,
        'description': craft.description,
        'category': craft.category,
        'seller': f"{craft.user.name}, {craft.user.address}",
    })


@session_required

def crafts_by_state_view(request, state_name):
    crafts_in_state = Craft.objects.filter(state=state_name, admin_status='approved')
    return render(request, 'user/state-craft-page.html', {
        'crafts': crafts_in_state,
        'state_name': state_name,
    })

@session_required

def add_to_cart(request, craft_id):
    user_id = request.session.get('user_login_id')
    user = get_object_or_404(User, pk=user_id)
    craft = get_object_or_404(Craft, id=craft_id)
    
    
    if craft.quantity == 0:
        messages.error(request, "This item is currently out of stock.")
        return redirect('cart')  
    
    
    cart, created = Cart.objects.get_or_create(user=user)
    cart_item, item_created = CartItem.objects.get_or_create(craft=craft, cart=cart)
    
    
    if not item_created:
        if cart_item.quantity + 1 > craft.quantity:
            messages.error(request, "Not enough stock available to add another unit.")
            return redirect('cart')
        cart_item.quantity += 1
        cart_item.save()
        messages.info(request, "+1 added to your cart.")
    else:
        messages.success(request, "Added successfully to your cart.")
    
    
    wishlist_item = WishlistItem.objects.filter(user=user, craft=craft)
    if wishlist_item.exists():
        wishlist_item.delete()
    
    return redirect('cart')








    


@session_required

def checkout(request):
    user_id = request.session.get('user_login_id', None)
    if user_id is None:
        messages.error(request, "You must be logged in to checkout.")
        return redirect('user_login')
    
    user = get_object_or_404(User, pk=user_id)
    cart = get_object_or_404(Cart, user=user)
    
    
    order = Order.objects.create(user=user)
    
    for item in cart.items.all():
        craft = item.craft
        
        
        if craft.quantity >= item.quantity:
            
            craft.quantity -= item.quantity
            craft.save()
        else:
            messages.error(request, f"Not enough quantity for {craft.name}.")
            return redirect('cart')
        
        
        OrderItem.objects.create(
            order=order,
            craft=craft,
            quantity=item.quantity
        )
        
        item.delete()
    
    messages.success(request, "Checkout successful! Your order has been placed.")
    return redirect('my_orders')


@session_required

def my_orders(request):
    user_id = request.session.get('user_login_id')
    user = get_object_or_404(User, pk=user_id)
    orders = Order.objects.filter(user=user).order_by('-created_at')
    return render(request, "user/user-my-orders.html", {'orders': orders})

from django.core.paginator import Paginator


@session_required

def my_purchases(request):
    user_id = request.session.get('user_login_id')
    user = get_object_or_404(User, pk=user_id)
    orders = Order.objects.filter(user=user, status="accepted", delivery_status="completed").order_by('-created_at')
    order_summaries = []
    for order in orders:
        items = order.orderitem_set.all()
        item_count = sum(item.quantity for item in items)
        total_price = sum(item.quantity * item.craft.price for item in items)
        
        order_summaries.append({
            'id': order.id,
            'item_count': item_count,
            'total_price': total_price,
            'created_at': order.created_at,
            'status': order.status,
            'payment_status': order.payment_status
        })

    paginator = Paginator(order_summaries, 5) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "user/user-my-purchases.html", {'page_obj': page_obj})





@session_required

def my_profile(request):
    user_id = request.session.get('user_login_id')
    user = get_object_or_404(User, pk=user_id)
    if request.method == "POST":
        user.name = request.POST.get('full_name')
        user.phone = request.POST.get('phone')
        user.email = request.POST.get('email')
        user.password = request.POST.get('password')
        user.address = request.POST.get('address')
        if 'profile_picture' in request.FILES:
            user.profile_picture = request.FILES['profile_picture']
        user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('my_profile')
    return render(request,"user/user-profile.html", {'user': user})




from django.db.models import Sum, Count, Prefetch


@session_required

def customers_orders(request):
    user_id = request.session.get('user_login_id')
    seller = get_object_or_404(User, pk=user_id)
    seller_crafts = Craft.objects.filter(user=seller)
    order_items_prefetch = Prefetch('orderitem_set', queryset=OrderItem.objects.filter(craft__in=seller_crafts))
    pending_orders = Order.objects.filter(
    orderitem__craft__in=seller_crafts,
    delivery_status='pending'
    ).prefetch_related(order_items_prefetch).distinct().order_by('-created_at')
    orders_with_totals = []
    for order in pending_orders:
        item_count = order.orderitem_set.aggregate(sum=Sum('quantity'))['sum'] or 0
        total_price = sum(item.quantity * item.craft.price for item in order.orderitem_set.all())
        craft_names = ", ".join(order.orderitem_set.values_list('craft__name', flat=True))
        orders_with_totals.append({
            'order': order,
            'item_count': item_count,
            'total_price': total_price,
            'craft_names': craft_names, 
        })
    return render(request, "user/user-seller-customers-orders.html", {'orders_with_totals': orders_with_totals})



def accept_order(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    user_id = request.session.get('user_login_id')
    if not order.orderitem_set.filter(craft__user_id=user_id).exists():
        return HttpResponseForbidden("You are not authorized to perform this action.")
    order.status = 'accepted'
    order.save()
    messages.success(request,"Order Accepted")
    return redirect('customers_orders') 






from io import TextIOWrapper
import pickle
import joblib
from transformers import AlbertTokenizer
from tensorflow.keras.models import model_from_json
from tensorflow.keras.preprocessing.sequence import pad_sequences
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Feedback, User, Order


print("Loading tokenizer...")
loaded_tokenizer = AlbertTokenizer.from_pretrained('amazone review/albert_tokenizer')


print("Loading label encoder...")
label_encoder = joblib.load('amazone review/label_encoder.joblib')


print("Loading model architecture...")
model_architecture_path = 'amazone review/bylstm_model_architecture.json'
with open(model_architecture_path, 'r') as json_file:
    loaded_model_json = json_file.read()


print("Loading model weights...")
model_weights_path = 'amazone review/bylstm_model_weights.h5'
loaded_model = model_from_json(loaded_model_json)
loaded_model.load_weights(model_weights_path)

max_len = 256


def predict_sentiment(text):
    print(f"Predicting sentiment for text: {text}")

    
    print(f"Tokenizing and padding input text...")
    sequences = [loaded_tokenizer.encode(text, max_length=max_len, truncation=True, padding='max_length')]
    padded_sequences = pad_sequences(sequences, maxlen=max_len, padding='post', truncating='post')

    
    print(f"Making prediction using the model...")
    predictions = loaded_model.predict(padded_sequences)
    print(f"Model prediction output: {predictions}")

    
    predicted_label = label_encoder.inverse_transform(predictions.argmax(axis=1))[0]
    print(f"Predicted sentiment label: {predicted_label}")
    
    
    return predicted_label


def feedback(request, order_id):
    print(f"Received feedback submission for order ID: {order_id}")
    user_id = request.session.get('user_login_id')
    print(f"User ID from session: {user_id}")

    if request.method == 'POST':
        print(f"Processing POST request...")
        
        user = get_object_or_404(User, pk=user_id)
        order = get_object_or_404(Order, pk=order_id)

        print(f"Fetched user: {user.user_name}, order: {order.id}")
        
        
        user_name = request.POST.get('user_name')
        user_email = request.POST.get('user_email')
        rating = request.POST.get('rating')
        additional_comments = request.POST.get('additional_comments')

        print(f"Feedback form data: user_name={user_name}, user_email={user_email}, rating={rating}, additional_comments={additional_comments}")

        
        print(f"Performing sentiment analysis...")
        sentiment = predict_sentiment(additional_comments)  
        print(f"Predicted sentiment: {sentiment}")

        
        
        if sentiment == 1:
            sentiment_label = "neutral"
        elif sentiment == 2:
            sentiment_label = "positive"
        else:
            sentiment_label = "negative"
        
        print(f"Mapped sentiment label: {sentiment_label}")

        
        print(f"Saving feedback to the database...")
        feedback = Feedback.objects.create(
            user=user,
            Order=order,
            user_name=user_name,
            user_email=user_email,
            rating=rating,
            additional_comments=additional_comments,
            sentiment=sentiment_label  
        )
        print(f"Feedback saved: {feedback}")

        
        messages.success(request, "Your feedback has been submitted successfully.")
        print(f"Redirecting to 'my_purchases'...")
        return redirect('my_purchases')

    print("Returning feedback page...")
    return render(request, "user/user-feedback.html")



def add_wishlist(request, craft_id):
    user_id = request.session.get('user_login_id')
    user = get_object_or_404(User, pk=user_id)
    craft = get_object_or_404(Craft, pk=craft_id)
    if WishlistItem.objects.filter(user=user, craft=craft).exists():
        messages.warning(request, f"{craft.name} is already in your wishlist.")
    else:
        WishlistItem.objects.create(user=user, craft=craft)
        messages.success(request, f"{craft.name} has been added to your wishlist.")
    return redirect("wishlist")

def wishlist(request):
    user_id = request.session.get('user_login_id')
    user = get_object_or_404(User, pk=user_id)
    wishlist_items = WishlistItem.objects.filter(user=user)
    return render(request, "user/wishlist.html", {'wishlist_items': wishlist_items})



def telugu(request):
    return render(request,"user/tel.html")

def hindi(request):
    return render(request,"user/hin.html")


def tamil(request):
    return render(request,"user/tam.html")

def kannnada(request):
    return render(request,"user/kan.html")



def remove_from_wishlist(request, item_id):
    item = get_object_or_404(WishlistItem, id=item_id)
    item.delete()
    messages.success(request, "Item removed from your wishlist.")
    return redirect('wishlist')







import re
import requests
from django.conf import settings
from django.shortcuts import render, redirect
from adminapp.models import Conversation
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def user_chatbot(request):
    conversations = Conversation.objects.all().order_by('created_at')
    
    if request.method == 'POST':
        user_message = request.POST.get('message', '').strip()
        if user_message:
            # Call Perplexity API
            headers = {
                "Authorization": f"Bearer {settings.PERPLEXITY_API_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "sonar",
                "messages": [
                  {
                        "role": "system",
                        "content": (
                            "You are a professional salesperson and inventory specialist for technology and electrical products. "
                            "Answer inquiries about products—such as the latest laptops, smartphones, and other electrical gadgets—"
                            "by providing accurate details including pricing and availability. "
                            "Your responses should be precise, professional, and reflect a deep knowledge of inventory details. "
                            "IMPORTANT: Provide all responses in plain text only, with no markdown formatting, no asterisks, no brackets, and no hyperlinks. "
                            "Output must be clear and simple plain text."
                        )
                    },

                    {
                        "role": "user",
                        "content": user_message
                    }
                ]
            }
            
            response = requests.post(
                "https://api.perplexity.ai/chat/completions",
                json=payload,
                headers=headers
            )
            
            bot_response = "Error: Could not get response from AI"
            if response.status_code == 200:
                try:
                    bot_response = response.json()['choices'][0]['message']['content']
                    
                    # Remove markdown bold () and any references (e.g., [1], [2], etc.)
                    bot_response = re.sub(r'\\([^]+)\\*', r'\1', bot_response)  # Remove bold
                    bot_response = re.sub(r'\[\d+\]', '', bot_response)  # Remove reference numbers
                except:
                    pass
                
            Conversation.objects.create(
                user_message=user_message,
                bot_response=bot_response
            )
            
            return redirect('user_chatbot')
    return render(request, "user/user_chatbot.html", {'conversations': conversations})

