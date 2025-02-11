from flask import Blueprint, request
from flask_restful import Api, Resource, reqparse
from models import db, Product, Service, Booking

# Define Blueprint for Booking
booking_bp = Blueprint('booking', __name__)
api = Api(booking_bp)

# Initialize the request parsers
product_booking_parser = reqparse.RequestParser()
service_booking_parser = reqparse.RequestParser()

# Add arguments for the product booking
product_booking_parser.add_argument('product_id', type=str, required=True, help="Product Name is required")
product_booking_parser.add_argument('name', type=str, required=True)
product_booking_parser.add_argument('phone', type=str, required=True)
product_booking_parser.add_argument('message', type=str, required=False)
product_booking_parser.add_argument('appointment', type=str, required=False)
product_booking_parser.add_argument('status', type=str, choices=['pending', 'confirmed', 'cancelled'], default='pending')
product_booking_parser.add_argument('amount_paid', type=float, required=False)

# Add arguments for the service booking
service_booking_parser.add_argument('service_id', type=str, required=True, help="Service Name is required")
service_booking_parser.add_argument('name', type=str, required=True)
service_booking_parser.add_argument('phone', type=str, required=True)
service_booking_parser.add_argument('message', type=str, required=False)
service_booking_parser.add_argument('appointment', type=str, required=False)
service_booking_parser.add_argument('status', type=str, choices=['pending', 'confirmed', 'cancelled'], default='pending')
service_booking_parser.add_argument('amount_paid', type=float, required=False)

# Resources

# Get Bookings for Products with Product Name
class ProductBookingsResource(Resource):
    def get(self):
        # Step 1: Query Booking records where product_id is not None
        bookings = db.session.query(Booking).filter(Booking.product_id.isnot(None)).all()

        # Step 2: Perform a query to get product names by joining with the Product table
        product_dict = {}
        if bookings:
            # Only query the product table if there are bookings
            product_names = db.session.query(Product.id, Product.name).all()
            product_dict = {product.id: product.name for product in product_names}

        # Step 3: Format the booking data as a list of dictionaries including the product name
        formatted_bookings = []
        for booking in bookings:
            # Check if product_id is an integer or a string (product_id as product name directly)
            if isinstance(booking.product_id, str):
                # If product_id is a string, use it as product_name
                product_name = booking.product_id  # product_id is already the product name
            else:
                # Else, get the product name from the product_dict (using product_id to look it up)
                product_name = product_dict.get(booking.product_id, "Unknown Product")

            # Format the booking data
            formatted_booking = {
                "id": booking.id,
                "product_id": booking.product_id,
                "product_name": product_name,
                "name": booking.name,
                "phone": booking.phone,
                "message": booking.message,
                "timestamp": booking.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                "appointment": booking.appointment,
                "status": booking.status,
                "amount_paid": booking.amount_paid
            }

            formatted_bookings.append(formatted_booking)

        return {"product_bookings": formatted_bookings}, 200
        
    def post(self):
        # Parse the request body
        data = request.get_json()

        # Validate the request data
        args = product_booking_parser.parse_args()

        # Create a new Booking record
        booking = Booking(
            product_id=args['product_id'],
            name=args['name'],
            phone=args['phone'],
            message=args.get('message'),
            appointment=args.get('appointment'),
            status=args['status'],
            amount_paid=args.get('amount_paid')
        )

        # Add the new booking to the database session
        db.session.add(booking)
        db.session.commit()

        # Return the newly created booking as a response
        return {'message': 'Created successfully'} , 200



class ProductBookingDeleteResource(Resource):
    def delete(self, booking_id):
        booking = Booking.query.get(booking_id)
        if not booking:
            return {"message": "Booking not found"}, 404

        db.session.delete(booking)
        db.session.commit()

        return {"message": "Booking deleted successfully"}, 200

    def put(self, booking_id):
       # Get the booking by id
       booking = Booking.query.get_or_404(booking_id)

       # Get the data from the request body
       data = request.get_json()

       # Update the appointment field if provided
       if 'appointment' in data:
            booking.appointment = data['appointment']

       # Update the status field if provided
       if 'status' in data:
            booking.status = data['status']

       # Update the amount_paid field if provided
       if 'amount_paid' in data:
            booking.amount_paid = data['amount_paid']

       # Commit the changes to the database
       db.session.commit()

       return {"message": "Booking updated successfully"}, 200


# Get Bookings for Services with Service Name
class ServiceBookingsResource(Resource):
  def get(self):
    # Step 1: Query Booking records where service_id is not None
    bookings = db.session.query(Booking).filter(Booking.service_id.isnot(None)).all()

    # Step 2: Perform a query to get service names by joining with the Service table
    service_dict = {}
    if bookings:
        # Only query the service table if there are bookings
        service_names = db.session.query(Service.id, Service.name).all()
        service_dict = {service.id: service.name for service in service_names}

    # Step 3: Format the booking data as a list of dictionaries including the service name
    formatted_bookings = []
    for booking in bookings:
        # Check if service_id is an integer or a string (service_id as service name directly)
        if isinstance(booking.service_id, str):
            # If service_id is a string, use it as service_name
            service_name = booking.service_id  # service_id is already the service name
        else:
            # Else, get the service name from the service_dict (using service_id to look it up)
            service_name = service_dict.get(booking.service_id, "Unknown Service")

        # Format the booking data
        formatted_booking = {
            "id": booking.id,
            "service_id": booking.service_id,
            "service_name": service_name,
            "name": booking.name,
            "phone": booking.phone,
            "message": booking.message,
            "timestamp": booking.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            "appointment": booking.appointment,
            "status": booking.status,
            "amount_paid": booking.amount_paid
        }

        formatted_bookings.append(formatted_booking)

    return {"service_bookings": formatted_bookings}, 200
  
  def post (self):
      # Parse the request body
      data = request.get_json()

      # Validate the request data
      args = service_booking_parser.parse_args()

      # Create a new Booking record
      booking = Booking(
          service_id=args['service_id'],
          name=args['name'],
          phone=args['phone'],
          message=args.get('message'),
          appointment=args.get('appointment'),
          status=args['status'],
          amount_paid=args.get('amount_paid')
      )

      # Add the new booking to the database session
      db.session.add(booking)
      db.session.commit()

      # Return the newly created booking as a response
      return {'message': 'Created successfully'}, 200

class ServiceBookingDeleteResource(Resource):
    def delete(self, booking_id):
        # Retrieve the booking by ID
        booking = Booking.query.get(booking_id)
        if not booking:
            return {"message": "Booking not found"}, 404

        # Delete the booking
        db.session.delete(booking)
        db.session.commit()

        return {"message": "Booking deleted successfully"}, 200

    def put(self, booking_id):
       # Get the booking by id
       booking = Booking.query.get_or_404(booking_id)

       # Get the data from the request body
       data = request.get_json()

       # Update the appointment field if provided
       if 'appointment' in data:
            booking.appointment = data['appointment']

       # Update the status field if provided
       if 'status' in data:
            booking.status = data['status']

       # Update the amount_paid field if provided
       if 'amount_paid' in data:
            booking.amount_paid = data['amount_paid']

       # Commit the changes to the database
       db.session.commit()

       return {"message": "Booking updated successfully"}, 200

# Add Resources to the API
api.add_resource(ProductBookingsResource, '/products/bookings', endpoint='product_bookings')
api.add_resource(ServiceBookingsResource, '/services/bookings', endpoint='service_bookings')

# Add delete resource with booking_id to delete specific booking
api.add_resource(ProductBookingDeleteResource, '/products/bookings/<int:booking_id>', endpoint='delete_product_booking')
api.add_resource(ServiceBookingDeleteResource, '/services/bookings/<int:booking_id>', endpoint='delete_service_booking')
