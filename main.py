from flask import Flask, jsonify, render_template,request  
from flask_sqlalchemy import SQLAlchemy  
import random  

app = Flask(__name__)  

# Connect to Database  
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'  
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  
db = SQLAlchemy()  
db.init_app(app)  


# Cafe TABLE Configuration class + methods  
class Cafe(db.Model):  
    id = db.Column(db.Integer, primary_key=True)  
    name = db.Column(db.String(250), unique=True, nullable=False)  
    map_url = db.Column(db.String(500), nullable=False)  
    img_url = db.Column(db.String(500), nullable=False)  
    location = db.Column(db.String(250), nullable=False)  
    seats = db.Column(db.String(250), nullable=False)  
    has_toilet = db.Column(db.Boolean, nullable=False)  
    has_wifi = db.Column(db.Boolean, nullable=False)  
    has_sockets = db.Column(db.Boolean, nullable=False)  
    can_take_calls = db.Column(db.Boolean, nullable=False)  
    coffee_price = db.Column(db.String(250), nullable=True)  

# perform the serialization process for the database
    def to_dict(self):  
        # method 1
        # dictionary = {}
        # for column in self.__table__.columns:
        #     dictionary[column.name] = getattr(self, column.name)
        #     return dictionary
        # method 2 (dictionary comprehension )
        return { column.name : getattr(self, column.name) for column in self.__table__.columns}

with app.app_context():
    db.create_all()

@app.route('/insert-sample-data')
def insert_sample_data():
    sample_cafes = [
    ]
    # Insert sample cafes into the database
    with app.app_context():
        for cafe in sample_cafes:
            # Check if a cafe with the same name already exists
            existing_cafe = Cafe.query.filter_by(name=cafe.name).first()
            if not existing_cafe:
                db.session.add(cafe)
        db.session.commit()

    return jsonify({"message": "Sample data inserted successfully!"})

@app.route("/")  
def home():
    cafe = Cafe.query.all()  
    return render_template("index.html", cafes=cafe)  

@app.route("/random")
def get_random_cafe():
    cafes = db.session.query(Cafe).all()
    random_cafe = random.choice(cafes)  
    return jsonify(cafes=random_cafe.to_dict())

@app.route("/all_cafes")
def all_cafes():
    cafes = db.session.query(Cafe).all()  
    return jsonify(cafes=[cafe.to_dict() for cafe in cafes])

@app.route('/search')
def search():
    location = request.args.get('location')
    if not location:  
        return jsonify({'error':
                        {"Not Found": "we don't have cafe at that location"}}), 400 
    
    cafes = db.session.query(Cafe).filter_by(location=location).all()
    if cafes:
        return jsonify(cafes=[cafe.to_dict() for cafe in cafes])
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."})
    

@app.route('/add_cafe', methods=['POST'])
def add():
    try:
        # Validate and ensure the form fields are not None
        name = request.form.get("name")
        map_url = request.form.get("map_url")
        img_url = request.form.get("img_url")
        location = request.form.get("location")
        seats = request.form.get("seats")  # Raw form data before conversion
        coffee_price = request.form.get("coffee_price")

        # Check if any field is None or missing
        if not name or not map_url or not img_url or not location or seats is None or coffee_price is None:
            return jsonify(error="Missing required form fields."), 400
        # Convert to appropriate types
        new_cafe = Cafe(
            name=name,
            map_url=map_url,
            img_url=img_url,
            location=location,
            has_sockets=bool(request.form.get("has_sockets")),
            has_toilet=bool(request.form.get("has_toilet")),
            has_wifi=bool(request.form.get("has_wifi")),
            can_take_calls=bool(request.form.get("can_take_calls")),
            seats=int(seats),  # Convert to int
            coffee_price=float(coffee_price)
        )
        # Add to the database
        db.session.add(new_cafe)
        db.session.commit()

        return jsonify(response={"success": "Successfully added the new cafe."})

    except ValueError as e:
        db.session.rollback()  # Rollback session in case of error
        return jsonify(error=f"ValueError: {str(e)}"), 400  # Catch conversion issues specifically

    except Exception as e:
        db.session.rollback()
        return jsonify(error=f"General error: {str(e)}"), 500

@app.route('/update-price/<int:cafe_id>', methods=['PATCH'])
def update_cafe_price(cafe_id):
    new_price = request.args.get("new_price")
    if new_price is None:
        return jsonify({"error": "Missing required parameter: new_price."}), 400
    try:
        new_price = float(new_price)  # Convert to float and catch ValueError
    except ValueError:
        return jsonify({"error": "Invalid price format."}), 400
    cafe = db.session.query(Cafe).get(cafe_id)
    if cafe:
        cafe.coffee_price = new_price
        db.session.commit()
        return jsonify({"success": "Successfully updated the cafe price.", "new_price": cafe.coffee_price}), 200
    else:
        return jsonify({"msg": "Cafe not found."}), 404
    
@app.route('/delete/<int:cafe_id>', methods=['DELETE'])
def delete_cafe(cafe_id):
    api_key = request.args.get('api-key')
    # Check if the API key is valid
    if api_key != 'topsecretkey':
        return jsonify(error={"message": "Forbidden: Invalid API key."}), 403
    # Query the cafe by ID
    cafe = db.session.query(Cafe).get(cafe_id)
    if cafe:
        db.session.delete(cafe)
        db.session.commit()
        return jsonify(success={"message": "Successfully deleted the cafe."}), 200
    else:
        return jsonify(error={"message": "Not Found: Cafe with that ID not found."}), 404

if __name__ == '__main__':  
    app.run(debug=True)


