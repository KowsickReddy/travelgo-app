from app import create_app, db
from app.models import Service

app = create_app()
app.app_context().push()

# Sample data for each category
services = [
    # Hotels
    Service(name="The Grand Palace", category="hotel", image="hotel1.jpg", price=2499, rating=4.7, description="Luxury stay in the city center."),
    Service(name="Sunrise Inn", category="hotel", image="hotel2.jpg", price=1599, rating=4.3, description="Affordable comfort for families."),
    Service(name="Lakeview Resort", category="hotel", image="hotel3.jpg", price=3299, rating=4.8, description="Resort with lake view and pool."),
    Service(name="Urban Stay", category="hotel", image="hotel4.jpg", price=1899, rating=4.1, description="Modern hotel in business district."),
    Service(name="Heritage Suites", category="hotel", image="hotel5.jpg", price=2799, rating=4.6, description="Experience heritage luxury."),
    Service(name="Budget Lodge", category="hotel", image="hotel6.jpg", price=999, rating=4.0, description="Best value for solo travelers."),
    Service(name="Airport Residency", category="hotel", image="hotel7.jpg", price=2099, rating=4.2, description="Convenient for airport access."),
    Service(name="Mountain Retreat", category="hotel", image="hotel8.jpg", price=3499, rating=4.9, description="Peaceful mountain escape."),
    Service(name="City Lights Hotel", category="hotel", image="hotel9.jpg", price=1999, rating=4.4, description="Stay in the heart of the city."),
    Service(name="Seaside Villa", category="hotel", image="hotel10.jpg", price=3999, rating=4.9, description="Beachfront luxury villa."),
    # Buses
    Service(name="Express Travels", category="bus", image="bus1.jpg", price=899, rating=4.2, description="AC sleeper bus service."),
    Service(name="CityLink", category="bus", image="bus2.jpg", price=499, rating=4.0, description="Affordable city bus."),
    Service(name="Night Rider", category="bus", image="bus3.jpg", price=1099, rating=4.5, description="Overnight intercity bus."),
    Service(name="GreenLine", category="bus", image="bus4.jpg", price=799, rating=4.1, description="Eco-friendly bus fleet."),
    Service(name="Royal Travels", category="bus", image="bus5.jpg", price=1299, rating=4.6, description="Premium bus experience."),
    Service(name="Budget Express", category="bus", image="bus6.jpg", price=399, rating=3.9, description="Best for budget travelers."),
    Service(name="MetroBus", category="bus", image="bus7.jpg", price=599, rating=4.0, description="City to suburb bus."),
    Service(name="Tourist Coach", category="bus", image="bus8.jpg", price=1499, rating=4.7, description="Tourist sightseeing bus."),
    Service(name="Comfort Travels", category="bus", image="bus9.jpg", price=999, rating=4.3, description="Comfortable seating."),
    Service(name="Speedy Wheels", category="bus", image="bus10.jpg", price=899, rating=4.1, description="Fast intercity bus."),
    # Trains
    Service(name="Shatabdi Express", category="train", image="train1.jpg", price=2999, rating=4.8, description="Fastest intercity train."),
    Service(name="Rajdhani", category="train", image="train2.jpg", price=3499, rating=4.7, description="Luxury long-distance train."),
    Service(name="Duronto", category="train", image="train3.jpg", price=2799, rating=4.5, description="Non-stop express train."),
    Service(name="Jan Shatabdi", category="train", image="train4.jpg", price=1599, rating=4.2, description="Affordable express train."),
    Service(name="Garib Rath", category="train", image="train5.jpg", price=999, rating=4.0, description="Budget AC train."),
    Service(name="Intercity", category="train", image="train6.jpg", price=1299, rating=4.1, description="Daily intercity service."),
    Service(name="Superfast", category="train", image="train7.jpg", price=1899, rating=4.3, description="Superfast train service."),
    Service(name="Passenger", category="train", image="train8.jpg", price=499, rating=3.8, description="Local passenger train."),
    Service(name="Tourist Special", category="train", image="train9.jpg", price=2499, rating=4.6, description="Tourist special train."),
    Service(name="Mountain Rail", category="train", image="train10.jpg", price=3999, rating=4.9, description="Scenic mountain railway."),
    # Flights
    Service(name="IndiGo 6E", category="flight", image="flight1.jpg", price=4999, rating=4.5, description="Domestic low-cost airline."),
    Service(name="Air India", category="flight", image="flight2.jpg", price=6999, rating=4.2, description="National carrier."),
    Service(name="Vistara", category="flight", image="flight3.jpg", price=7999, rating=4.7, description="Premium airline experience."),
    Service(name="SpiceJet", category="flight", image="flight4.jpg", price=5999, rating=4.1, description="Affordable flights."),
    Service(name="Go First", category="flight", image="flight5.jpg", price=5499, rating=4.0, description="Budget airline."),
    Service(name="AirAsia India", category="flight", image="flight6.jpg", price=6299, rating=4.3, description="Low-cost carrier."),
    Service(name="Akasa Air", category="flight", image="flight7.jpg", price=5799, rating=4.1, description="Newest airline."),
    Service(name="Alliance Air", category="flight", image="flight8.jpg", price=4999, rating=4.0, description="Regional airline."),
    Service(name="TruJet", category="flight", image="flight9.jpg", price=4899, rating=3.9, description="Regional flights."),
    Service(name="Star Air", category="flight", image="flight10.jpg", price=5199, rating=4.2, description="Regional airline."),
    # Cabs
    Service(name="City Taxi", category="cab", image="cab1.jpg", price=299, rating=4.3, description="City rides at low fares."),
    Service(name="Airport Cab", category="cab", image="cab2.jpg", price=499, rating=4.5, description="Airport pickup/drop."),
    Service(name="Outstation Cab", category="cab", image="cab3.jpg", price=1299, rating=4.6, description="Long distance cabs."),
    Service(name="Luxury Sedan", category="cab", image="cab4.jpg", price=1999, rating=4.8, description="Premium sedan rides."),
    Service(name="Mini Cab", category="cab", image="cab5.jpg", price=199, rating=4.0, description="Mini cabs for short trips."),
    Service(name="SUV Cab", category="cab", image="cab6.jpg", price=799, rating=4.4, description="Spacious SUV rides."),
    Service(name="Tourist Cab", category="cab", image="cab7.jpg", price=1599, rating=4.5, description="Tourist sightseeing cab."),
    Service(name="Women Cab", category="cab", image="cab8.jpg", price=399, rating=4.7, description="Women-driven cabs."),
    Service(name="Pet Taxi", category="cab", image="cab9.jpg", price=599, rating=4.2, description="Cabs for pets."),
    Service(name="Bike Taxi", category="cab", image="cab10.jpg", price=99, rating=3.8, description="Bike taxi for quick rides.")
]

for s in services:
    db.session.add(s)
db.session.commit()
print("Service data seeded.")
