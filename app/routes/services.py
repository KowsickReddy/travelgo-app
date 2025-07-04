from flask import Blueprint, render_template, request
from ..models import Service

services_bp = Blueprint('services', __name__)

@services_bp.route('/services')
def services():
    # Example: fetch categories or services from DB if needed
    categories = [
        {'key': 'hotel', 'name': 'Hotels'},
        {'key': 'bus', 'name': 'Buses'},
        {'key': 'train', 'name': 'Trains'},
        {'key': 'air', 'name': 'Flights'},
        {'key': 'cab', 'name': 'Cabs'}
    ]
    return render_template('services.html', categories=categories)

@services_bp.route('/services/category')
def service_category():
    category = request.args.get('category')
    # Collect travel details from query string
    travel_details = {
        'from': request.args.get('from'),
        'to': request.args.get('to'),
        'date': request.args.get('date'),
        'adults': request.args.get('adults'),
        'children': request.args.get('children'),
        'class': request.args.get('class'),
        'rooms': request.args.get('rooms'),
        'nights': request.args.get('nights'),
    }
    # Fetch services for the selected category (mock or DB)
    services = Service.query.filter_by(category=category).all() if category else []
    template_map = {
        'train': 'train.html',
        'bus': 'bus.html',
        'hotel': 'hotel.html',
        'air': 'air.html',
        'cab': 'cab.html',
    }
    template = template_map.get(category, 'services.html')
    return render_template(template, services=services, travel_details=travel_details, category=category)
