from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random
app = Flask(__name__)

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False
db = SQLAlchemy(app)


# Cafe TABLE Configuration
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

    def to_dict(self):
        """Returns a python dictionary using by all values in all columns that belong any table"""
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


def str2bool(v):
    """Makes structured string values boolean"""
    return v.lower() in ("1", "true", "yes", "y")


@app.route("/")
def home():
    return render_template("index.html")
    

# HTTP GET - Read Record
@app.route("/random")
def get_random_cafe():
    cafes = db.session.query(Cafe).all()
    random_cafe = random.choice(cafes)
    return jsonify(Cafe=random_cafe.to_dict())


@app.route("/all")
def get_all_cafes():
    cafes = db.session.query(Cafe).all()
    return jsonify(all_cafes=[cafe.to_dict() for cafe in cafes])


@app.route("/search")
def search():
    loc = request.args.get("loc")
    cafes = db.session.query(Cafe).filter(Cafe.location == loc)
    has_cafe = [cafe.to_dict() for cafe in cafes]
    if has_cafe:
        return jsonify(cafe=has_cafe)
    else:
        error_message = {"Not Found": "Sorry, we dont have a cafe at that location"}
        return jsonify(error=error_message), 404


# HTTP POST - Create Record
@app.route("/add", methods=["POST"])
def add():
    new_cafe = Cafe(name=request.form['name'], map_url=request.form['map_url'], img_url=request.form['img_url'],
                    location=request.form['location'],
                    seats=request.form['seats'],
                    has_toilet=str2bool(request.form['has_toilet']),
                    has_wifi=str2bool(request.form['has_wifi']),
                    has_sockets=str2bool(request.form['has_sockets']),
                    can_take_calls=str2bool(request.form['can_take_calls']),
                    coffee_price=request.form['coffee_price']
                    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe"}), 200


# HTTP PUT/PATCH - Update Record
@app.route("/update-price/<cafe_id>", methods=["GET", "PATCH"])
def update(cafe_id):
    new_price = request.args.get("new_price")
    last_record = db.session.query(Cafe).order_by(Cafe.id.desc()).first()
    if last_record.id >= int(cafe_id):
        cafe_to_patch = Cafe.query.filter_by(id=cafe_id).first()
        cafe_to_patch.coffee_price = new_price
        db.session.commit()
        return jsonify(
            response={"success": f"Successfully patched the {cafe_id}. cafe's coffee price as {new_price} "}), 200
    else:
        return jsonify(Error={"Not Found": "Sorry, a cafe with that id was not found in database"}), 404


# HTTP DELETE - Delete Record

@app.route("/report-closed/<cafe_id>", methods=["GET", "DELETE"])
def delete(cafe_id):
    last_record = db.session.query(Cafe).order_by(Cafe.id.desc()).first()
    if last_record.id >= int(cafe_id):
        user_api_key = request.args.get('api-key')
        if user_api_key == "TopSecretApiKey":
            cafe_to_delete = Cafe.query.get(cafe_id)
            db.session.delete(cafe_to_delete)
            db.session.commit()
            return jsonify({"success": f"Successfully deleted a cafe with {cafe_id} id."}), 200
        else:
            return jsonify({"error": "Sorry, that is not allowed. Make sure you have the correct api-key."}), 403
    else:
        return jsonify(Error={"Not Found": "Sorry, a cafe with that id was not found in database"}), 404


if __name__ == '__main__':
    app.run(debug=True)
