import os
import re
from datetime import datetime, timedelta
from decimal import Decimal
from werkzeug.utils import secure_filename

def allowed_file(filename, allowed_extensions={'png', 'jpg', 'jpeg', 'gif'}):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def generate_unique_filename(filename):
    """Generate unique filename with timestamp"""
    name, ext = os.path.splitext(secure_filename(filename))
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{name}_{timestamp}{ext}"

def validate_price(price):
    """Validate price value"""
    try:
        price_decimal = Decimal(str(price))
        return price_decimal >= 0 and price_decimal <= 9999.99
    except:
        return False

def format_currency(amount):
    """Format amount as currency"""
    return f"${float(amount):.2f}"

def calculate_discount_percentage(original_price, sale_price):
    """Calculate discount percentage"""
    if not original_price or original_price <= 0:
        return 0
    
    discount = ((original_price - sale_price) / original_price) * 100
    return round(discount, 0)

def generate_slug(text):
    """Generate URL-friendly slug from text"""
    # Convert to lowercase and replace spaces with hyphens
    slug = re.sub(r'[^\w\s-]', '', text.lower())
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug.strip('-')

def paginate_query(query, page=1, per_page=10):
    """Helper function for pagination"""
    try:
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return {
            'items': pagination.items,
            'pagination': {
                'page': page,
                'pages': pagination.pages,
                'per_page': per_page,
                'total': pagination.total,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        }
    except Exception:
        return {
            'items': [],
            'pagination': {
                'page': 1,
                'pages': 0,
                'per_page': per_page,
                'total': 0,
                'has_next': False,
                'has_prev': False
            }
        }

def format_date(date_obj, format_str='%Y-%m-%d'):
    """Format date object to string"""
    if not date_obj:
        return None
    return date_obj.strftime(format_str)

def parse_date(date_str, format_str='%Y-%m-%d'):
    """Parse date string to date object"""
    try:
        return datetime.strptime(date_str, format_str).date()
    except:
        return None

def calculate_shipping_cost(subtotal, free_shipping_threshold=50.00, standard_rate=5.99):
    """Calculate shipping cost based on subtotal"""
    if subtotal >= free_shipping_threshold:
        return 0.00
    return standard_rate

def calculate_tax(subtotal, tax_rate=0.10):
    """Calculate tax amount"""
    return subtotal * Decimal(str(tax_rate))

def validate_phone_number(phone):
    """Basic phone number validation"""
    if not phone:
        return True  # Phone is optional
    
    # Remove all non-digits
    digits_only = re.sub(r'\D', '', phone)
    
    # Check if it's a valid length (10-15 digits)
    return 10 <= len(digits_only) <= 15

def sanitize_search_term(term):
    """Sanitize search term for database queries"""
    if not term:
        return ''
    
    # Remove special characters that could cause issues
    sanitized = re.sub(r'[<>"\';\\]', '', term.strip())
    return sanitized[:100]  # Limit length

def get_file_size(file_path):
    """Get file size in bytes"""
    try:
        return os.path.getsize(file_path)
    except:
        return 0

def format_file_size(size_bytes):
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"

def is_valid_email_domain(email):
    """Basic email domain validation"""
    try:
        domain = email.split('@')[1].lower()
        # Add your domain blacklist/whitelist logic here
        blocked_domains = ['temp-mail.org', '10minutemail.com']
        return domain not in blocked_domains
    except:
        return False

def get_order_status_color(status):
    """Get color class for order status"""
    status_colors = {
        'pending': 'yellow',
        'confirmed': 'blue', 
        'processing': 'purple',
        'shipped': 'indigo',
        'delivered': 'green',
        'cancelled': 'red'
    }
    return status_colors.get(status, 'gray')

def calculate_estimated_delivery(order_date, shipping_method='standard'):
    """Calculate estimated delivery date"""
    if shipping_method == 'express':
        days = 2
    elif shipping_method == 'priority':
        days = 1
    else:  # standard
        days = 5
    
    estimated = order_date + timedelta(days=days)
    return estimated

def generate_order_tracking_number():
    """Generate tracking number for orders"""
    import random
    import string
    
    prefix = "TRK"
    timestamp = datetime.now().strftime("%y%m%d")
    random_part = ''.join(random.choices(string.digits, k=6))
    return f"{prefix}{timestamp}{random_part}"

class APIResponse:
    """Standardized API response helper"""
    
    @staticmethod
    def success(data=None, message="Success", status_code=200):
        """Create success response"""
        response = {"success": True, "message": message}
        if data is not None:
            if isinstance(data, dict):
                response.update(data)
            else:
                response["data"] = data
        return response, status_code
    
    @staticmethod
    def error(message="An error occurred", details=None, status_code=400):
        """Create error response"""
        response = {"success": False, "error": message}
        if details:
            response["details"] = details
        return response, status_code
    
    @staticmethod
    def validation_error(errors, message="Validation failed"):
        """Create validation error response"""
        return {
            "success": False,
            "error": message,
            "validation_errors": errors
        }, 422

def mask_email(email):
    """Mask email for privacy (e.g., j***@example.com)"""
    try:
        username, domain = email.split('@')
        if len(username) <= 2:
            masked_username = username[0] + '*'
        else:
            masked_username = username[0] + '*' * (len(username) - 2) + username[-1]
        return f"{masked_username}@{domain}"
    except:
        return email

def mask_phone(phone):
    """Mask phone number for privacy"""
    if not phone:
        return phone
    
    digits = re.sub(r'\D', '', phone)
    if len(digits) >= 10:
        return f"***-***-{digits[-4:]}"
    return phone

def get_client_ip(request):
    """Get client IP address from request"""
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        return request.environ['REMOTE_ADDR']
    else:
        return request.environ['HTTP_X_FORWARDED_FOR']

def log_user_activity(user_id, action, details=None):
    """Log user activity (placeholder for future implementation)"""
    # This could be expanded to log to database or external service
    activity = {
        'user_id': user_id,
        'action': action,
        'details': details,
        'timestamp': datetime.utcnow()
    }
    print(f"User Activity: {activity}")  # For now, just print

def create_breadcrumbs(category_slug=None, book_title=None):
    """Create breadcrumb navigation"""
    breadcrumbs = [{'name': 'Home', 'url': '/'}]
    
    if category_slug:
        breadcrumbs.append({
            'name': category_slug.replace('-', ' ').title(),
            'url': f'/category/{category_slug}'
        })
    
    if book_title:
        breadcrumbs.append({
            'name': book_title[:50] + '...' if len(book_title) > 50 else book_title,
            'url': '#',
            'current': True
        })
    
    return breadcrumbs