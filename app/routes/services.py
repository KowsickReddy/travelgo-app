from flask import Blueprint, render_template, request
from app.models import Service

services_bp = Blueprint('services', __name__)

@services_bp.route('/services')
def services():
    category = request.args.get('category')
    from_location = request.args.get('from_location', '')
    destination = request.args.get('destination', '')
    date = request.args.get('date', '')
    categories = [
        {'key': 'hotel', 'name': 'Hotels'},
        {'key': 'bus', 'name': 'Buses'},
        {'key': 'train', 'name': 'Trains'},
        {'key': 'air', 'name': 'Flights'},
        {'key': 'cab', 'name': 'Cabs'}
    ]
    if category:
        # Fetch services from DB for the selected category
        options = Service.query.filter_by(category=category).all()
        template_map = {
            'train': 'train.html',
            'bus': 'bus.html',
            'hotel': 'hotel.html',
            'air': 'air.html',
            'cab': 'cab.html',
        }
        template = template_map.get(category, 'services.html')
        return render_template(
            template,
            options=options,
            category=category,
            from_location=from_location,
            destination=destination,
            date=date
        )
    # If no category, show the categories selection page
    return render_template(
        'services.html',
        categories=categories,
        from_location=from_location,
        destination=destination,
        date=date
    )