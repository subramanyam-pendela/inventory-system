from django.shortcuts import render,redirect,get_list_or_404,get_object_or_404
from userapp.models import *
from adminapp.models import *
from django.contrib.auth import logout
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.db.models import Sum, Count
from django.utils.timezone import now
from django.http import JsonResponse
from datetime import timedelta
from django.db.models.functions import ExtractHour
from decimal import Decimal
from django.db.models import Sum, Count, F
import datetime





def toggle_sell_permission(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    user.allow_to_sell = not user.allow_to_sell
    user.save()
    new_status = "enabled" if user.allow_to_sell else "disabled"
    messages.success(request, f"Sales permission has been {new_status} for {user.name}.")
    return redirect('all_users')



def admin_logout(request):
    logout(request)
    return redirect('admin_login')





from django.utils import timezone

def change_delivery_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.delivery_status = 'completed'
    order.save()
    user_email = order.user.email
    craft_names = order.crafts.name
    delivery_date = timezone.now()
    subject = 'Order Delivered'
    message = f'Hi,\nYour order for the following items has been delivered:\n\n{craft_names}\n\nDelivery Date: {delivery_date}\n\nThank you for shopping with us!'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [user_email]
    send_mail(subject, message, from_email, recipient_list, fail_silently=False)
    return redirect('pending_orders')




import csv
from django.http import HttpResponse

def generate_reports(request):
    report_type = request.GET.get('report_type')  # 'yearly', 'monthly', 'daily'
    year = request.GET.get('year')
    month = request.GET.get('month')
    date_str = request.GET.get('date')

    # Convert month name to a month number if needed
    month_map = {
        'January': 1, 'February': 2, 'March': 3, 'April': 4,
        'May': 5, 'June': 6, 'July': 7, 'August': 8,
        'September': 9, 'October': 10, 'November': 11, 'December': 12
    }

    # Base queryset
    orders = OrderItem.objects.filter(order__status='accepted')

    if report_type == 'yearly' and year:
        # Filter by year
        orders = orders.filter(order__created_at__year=year)

    elif report_type == 'monthly' and year and month:
        orders = orders.filter(order__created_at__year=year,
                               order__created_at__month=month_map[month])

    elif report_type == 'daily' and date_str:
        # e.g. '2025-03-15'
        date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        orders = orders.filter(order__created_at__date=date_obj)

    # Now 'orders' is filtered based on the user’s selection
    # Let's generate a CSV with each item’s craft, quantity, price, etc.

    response = HttpResponse(content_type='text/csv')
    filename = f'{report_type}_report.csv'
    response['Content-Disposition'] = f'attachment; filename={filename}'

    writer = csv.writer(response)
    writer.writerow(['Order ID', 'Craft Name', 'Quantity', 'Unit Price (₹)', 'Total Price (₹)'])

    for item in orders:
        craft_name = item.craft.name
        quantity = item.quantity
        unit_price = item.craft.price
        total_price = unit_price * quantity
        writer.writerow([item.order.id, craft_name, quantity, unit_price, total_price])

    return response




def admin_dashboard(request):
    today = now().date()

    # 1) Basic stats
    total_users = User.objects.count()
    total_crafts = Craft.objects.count()
    total_feedbacks = Feedback.objects.count()

    # 2) Hourly Revenue from accepted orders (in rupees) -- existing code
    sales_data = (
        OrderItem.objects
        .filter(order__status='accepted', order__created_at__date=today)
        .annotate(hour=ExtractHour('order__created_at'))
        .values('hour')
        .annotate(total_sales=Sum(F('craft__price') * F('quantity')))
        .order_by('hour')
    )

    # Create a dict with all hours 0..23 = 0 -- existing code
    sales_chart_data = {hour: 0 for hour in range(24)}
    for entry in sales_data:
        hour = entry['hour']
        sales_chart_data[hour] = float(entry['total_sales'])  # Convert Decimal to float

    print("Hourly Sales Data:", sales_chart_data)  # Debug output

    # 3) Profit/Loss for the day -- existing code
    total_revenue = sum(sales_chart_data.values())  # Sum of all hours
    print("Total Revenue (₹):", total_revenue)

    total_cost = Decimal(total_revenue) * Decimal('0.6')
    print("Total Cost (₹):", total_cost)

    profit = Decimal(total_revenue) - total_cost
    print("Profit (₹):", profit)

    profit_loss_data = {
        'Profit': float(profit) if profit > 0 else 0,
        'Loss': float(abs(profit)) if profit < 0 else 0,
    }

    # NEW FEATURE: Category-wise revenue (bar chart)
    # 1) Query total revenue for each category from today's accepted orders
    category_revenue_qs = (
        OrderItem.objects
        .filter(order__status='accepted', order__created_at__date=today)
        .values('craft__category')
        .annotate(total_revenue=Sum(F('craft__price') * F('quantity')))
    )
    print("Category Revenue QuerySet:", list(category_revenue_qs))  # Debug output

    # 2) Build a dict with fixed choices, and it will include extra categories from the data.
    # Start with fixed keys:
    fixed_keys = [cat[0] for cat in Craft.CATEGORY_CHOICES]
    category_revenue_dict = {key: 0 for key in fixed_keys}
    # Add extra keys if they appear in the data:
    for row in category_revenue_qs:
        key = row['craft__category']  # e.g. 'Textiles'
        total_rev = row['total_revenue'] or 0
        # If the key is not already in the dict, add it:
        if key in category_revenue_dict:
            category_revenue_dict[key] = float(total_rev)
        else:
            category_revenue_dict[key] = float(total_rev)
    print("Category Revenue Dict:", category_revenue_dict)  # Debug output

    # 3) Create the labels and data.
    # Order: first the fixed keys in order, then any extra keys not in fixed_keys.
    extra_keys = [key for key in category_revenue_dict.keys() if key not in fixed_keys]
    all_keys = fixed_keys + extra_keys  # fixed order then extras
    # For labels, use the human readable value from choices; if not found, use the key itself.
    choice_dict = dict(Craft.CATEGORY_CHOICES)
    category_labels = [choice_dict.get(key, key) for key in all_keys]
    category_revenue_data = [category_revenue_dict.get(key, 0) for key in all_keys]
    print("All Category Labels:", category_labels)           # Debug output
    print("All Category Revenue Data:", category_revenue_data)   # Debug output

    # 4) Pass everything to the template
    context = {
        'total_users': total_users,
        'total_crafts': total_crafts,
        'total_feedbacks': total_feedbacks,
        'sales_chart_data': list(sales_chart_data.values()),  # For line chart
        'profit_loss_data': profit_loss_data,
        'category_labels': category_labels,                   # For bar chart
        'category_revenue_data': category_revenue_data,       # For bar chart
    }
    return render(request, 'admin/index.html', context)


def all_crafts(request):
    approved_crafts = Craft.objects.filter(admin_status='approved').order_by('-id')
    return render(request, "admin/all-crafts.html", {'crafts': approved_crafts})


def pending_crafts(request):
    crafts = Craft.objects.filter(admin_status='pending').order_by('-id')
    return render(request, "admin/pending-crafts.html", {'crafts': crafts})




def delete_craft(request, craft_id):
    # Retrieve the craft or return a 404 if not found
    craft = get_object_or_404(Craft, pk=craft_id)
    craft.delete()
    messages.success(request, "Product deleted successfully!")
    return redirect('pending_crafts')



def accept_craft(request, craft_id):
    craft = get_object_or_404(Craft, pk=craft_id, admin_status='pending')
    craft.admin_status = 'approved'
    craft.save()
    messages.success(request,"Accepted !")
    return redirect('pending_crafts')




def all_orders(request):
    accepted_orders = Order.objects.filter(status='accepted').order_by('-created_at')
    return render(request, "admin/all-orders.html", {'accepted_orders': accepted_orders})



def pending_orders(request):
    orders = Order.objects.filter(delivery_status='pending').order_by('-created_at')
    return render(request, "admin/pending-orders.html", {'orders': orders})



def accept_order(request, order_id):
    order = get_object_or_404(Order, pk=order_id, status='pending')
    order.status = 'accepted'
    order.save()
    messages.success(request,"Order is Accepted !")
    return redirect('pending_orders')




def all_users(request):
    users = User.objects.all()
    return render(request, "admin/all-users.html", {'users': users})


def toggle_user_status(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    user.status = 'pending' if user.status == 'accepted' else 'accepted'
    user.save()
    messages.info(request,"Changed status successfully ")
    return redirect('all_users')
    



def remove_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    user.delete()
    messages.info(request,"Deleted User Successfully ")
    return redirect('all_users')




from django.core.paginator import Paginator

def view_feedbacks(request):
    feedbacks_list = Feedback.objects.select_related('Order', 'user').all()
    paginator = Paginator(feedbacks_list, 5) 
    page_number = request.GET.get('page')
    feedbacks = paginator.get_page(page_number)
    return render(request, "admin/feedbacks.html", {'feedbacks': feedbacks})



def graph(request):
    rating_counts = {
        'rating1': Feedback.objects.filter(rating=1).count(),
        'rating2': Feedback.objects.filter(rating=2).count(),
        'rating3': Feedback.objects.filter(rating=3).count(),
        'rating4': Feedback.objects.filter(rating=4).count(),
        'rating5': Feedback.objects.filter(rating=5).count(),
    }
    return render(request, "admin/graph.html",{'rating_counts':rating_counts})


def add_events(request):
    craft_categories = Craft.CATEGORY_CHOICES
    context = {'craft_categories': craft_categories}
    if request.method == 'POST':
        event_name = request.POST.get('event_name')
        event_date = request.POST.get('event_date')
        event_categories = request.POST.getlist('event_category')
        event_description = request.POST.get('event_description')
        event_poster = request.FILES.get('event_img')
        categories_str = ', '.join(event_categories)
        event = Event.objects.create(
            name=event_name,
            date=event_date,
            categories=categories_str,
            description=event_description,
            poster=event_poster
        )
        messages.success(request,"Event is Added Succesfully ")
        return redirect('add_events')
    return render(request, "admin/add-events.html", context)



def manage_events(request):
    events = Event.objects.all()
    return render(request,"admin/manage-events.html",{'events':events})



def remove_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    event.delete()
    messages.info(request,"Event Removed Succesfully ")
    return redirect('manage_events') 




from decimal import Decimal, InvalidOperation

def update_craft_price_view(request, craft_id):
    craft = get_object_or_404(Craft, pk=craft_id)
    
    if request.method == 'POST':
        new_price = request.POST.get('new_price', '').strip()
        new_quantity = request.POST.get('new_quantity', '').strip()
        
        # Update price if a new value is provided
        if new_price:
            try:
                new_price_decimal = Decimal(new_price)
                craft.price = new_price_decimal
            except (InvalidOperation, TypeError):
                messages.error(request, "Please enter a valid price.")
                return redirect('update_craft_price', craft_id=craft_id)
        
        # Update quantity if a new value is provided
        if new_quantity:
            try:
                new_quantity_int = int(new_quantity)
                if new_quantity_int < 0:
                    raise ValueError("Negative quantity not allowed")
                craft.quantity = new_quantity_int
            except (ValueError, TypeError):
                messages.error(request, "Please enter a valid quantity.")
                return redirect('update_craft_price', craft_id=craft_id)
        
        # Save the craft only if at least one field was updated.
        craft.save()
        messages.success(request, "Craft updated successfully!")
        return redirect('all_crafts')
    
    # Render the form for GET requests with current craft info.
    return render(request, "admin/update_craft_price.html", {"craft": craft})




def sentiment_analysis(request):
    return render(request,"admin/sentiment_analysis.html")