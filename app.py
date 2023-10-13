from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

###########################################
##   FLASK CONFIGS AND INITIALIZATION    ##
###########################################

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = "dfghwenkl4983ufhwjebf8394nvdnv"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///aminta.sqlite3"
db = SQLAlchemy(app)
migrate = Migrate(app, db)



###########################################
##   DATABASE SCHEMA AND MODELS          ##
###########################################

class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity_sold = db.Column(db.Integer, nullable=False)
    sale_date = db.Column(db.DateTime, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    customer_name = db.Column(db.Text)
    payment_method = db.Column(db.Text)
    notes = db.Column(db.Text)

    def __init__(self, product_id, quantity_sold, sale_date, total_price, customer_name=None, payment_method=None, notes=None):
        self.product_id = product_id
        self.quantity_sold = quantity_sold
        self.sale_date = sale_date
        self.total_price = total_price
        self.customer_name = customer_name
        self.payment_method = payment_method
        self.notes = notes

class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity_added = db.Column(db.Integer, nullable=False)
    intake_date = db.Column(db.DateTime, nullable=False)
    supplier_name = db.Column(db.Text)
    purchase_price = db.Column(db.Float, nullable=False)
    notes = db.Column(db.Text)
    expiry_date = db.Column(db.Date)  # New field for expiry date

    # Fields for product hierarchy
    large_packing = db.Column(db.Integer)
    small_packing = db.Column(db.Integer)
    individual_pieces = db.Column(db.Integer)

    def __init__(self, product_id, quantity_added, intake_date, purchase_price, supplier_name=None, notes=None, expiry_date=None, large_packing=None, small_packing=None, individual_pieces=None):
        self.product_id = product_id
        self.quantity_added = quantity_added
        self.intake_date = intake_date
        self.purchase_price = purchase_price
        self.supplier_name = supplier_name
        self.notes = notes
        self.expiry_date = expiry_date
        self.large_packing = large_packing
        self.small_packing = small_packing
        self.individual_pieces = individual_pieces


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.Text)
    unit_price = db.Column(db.Float, nullable=False)
    units_per_box = db.Column(db.Integer)  # If products are sold in boxes, add this field.

    def __init__(self, product_name, unit_price, description=None, category=None, units_per_box=None):
        self.product_name = product_name
        self.unit_price = unit_price
        self.description = description
        self.category = category
        self.units_per_box = units_per_box


####################
#   PRODUCT CRUD   #
####################

#Create a product
@app.route('/api/products', methods=['POST'])
def create_product():
    data = request.json
    product = Product(**data)
    db.session.add(product)
    db.session.commit()
    return jsonify(message='Product created successfully')


#
@app.route()


@app.route('/api/hello')
def hello():
    return jsonify(message = 'hellow Word')


if __name__ == '__main__':
    app.run(debug=True)