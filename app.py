from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime

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


# Get a list of all products
@app.route('/api/products', methods=['GET'])
def get_all_products():
    products = Product.query.all()
    product_list = [{'id': product.id, 'product_name': product.product_name, 'description': product.description,
                    'category': product.category, 'unit_price': product.unit_price, 'units_per_box': product.units_per_box}
                   for product in products]
    return jsonify(products=product_list)


#Get details of a specific product
@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get(product_id)
    if product:
        return jsonify(product={
            'id' : product.id,
             'product_name': product.product_name,
            'description': product.description,
            'category': product.category,
            'unit_price': product.unit_price,
            'units_per_box': product.units_per_box
        })
    else:
        return jsonify(message = "Product not found"), 404


#Update product details
@app.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    data = request.json
    product = Product.query.get(product_id)
    if not product:
        return jsonify(message='Product not found'), 404
    
    for key, value in data.items():
        setattr(product, key, value)

    db.session.commit()
    return jsonify(message='Product updated successfully')


# DELETE a product entry
@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify(message='Product not found'), 404

    db.session.delete(product)
    db.session.commit()

    return jsonify(message='Product deleted successfully') 


#####################################
#       STOCK CRUD ROUTES           #
#####################################

#create a new stock entry
@app.route('/api/stocks' , methods=['POST'])
def create_stock():
    data = request.json
    #converting date string to datetime format
    data['intake_date'] = datetime.strptime(data['intake_date'], "%Y-%m-%dT%H:%M:%S")
    data['expiry_date'] = datetime.strptime(data['expiry_date'], "%Y-%m-%d")

    stock = Stock(**data)
    db.session.add(stock)
    db.session.commit()
    return jsonify(message = 'Stock entry successfully created')


#get a list of all stock entries
@app.route('/api/stocks', methods=['GET'])
def get_all_Stocks():
    stocks = Stock.query.all()
    stock_list = [{id: stock.id, 'product_id':  stock.product_id, 'quantity_added': stock.quantity_added,
                  'intake_date': stock.intake_date, 'supplier_name': stock.supplier_name,
                  'purchase_price': stock.purchase_price, 'expiry_date': stock.expiry_date,
                  'large_packing': stock.large_packing, 'small_packing': stock.small_packing,
                  'individual_pieces': stock.individual_pieces}
                 for stock in stocks]
    return jsonify(stocks=stock_list)


#get detials of a specific stock entry
@app.route('/api/stocks/<int:stock_id>', methods=['GET'])
def get_stock(stock_id):
    stock = Stock.query.get(stock_id)
    if stock:
        return jsonify(stock={
            'id': stock.id,
            'product_id': stock.product_id,
            'quantity_added': stock.quantity_added,
            'intake_date': stock.intake_date,
            'supplier_name': stock.supplier_name,
            'purchase_price': stock.purchase_price,
            'expiry_date': stock.expiry_date,
            'large_packing': stock.large_packing,
            'small_packing': stock.small_packing,
            'individual_pieces': stock.individual_pieces
        })
    else:
        return jsonify(message = 'Stock entry not found'), 404
    

# Update stock entry details
@app.route('/api/stocks/<int:stock_id>', methods=['PUT'])
def update_Stock(stock_id):
    data = request.json
    stock = Stock.query.get(stock_id)
    if not stock:
        return jsonify(message='Stock entry not found'), 404
    
     # Parse the date and time strings to datetime objects
    if 'intake_date' in data:
        data['intake_date'] = datetime.strptime(data['intake_date'], "%Y-%m-%dT%H:%M:%S")
    if 'expiry_date' in data:
        data['expiry_date'] = datetime.strptime(data['expiry_date'], "%Y-%m-%d")


    for key, value in data.items():
        setattr(stock, key, value)

    db.session.commit()
    return jsonify(message='Stock entry updated successfully')

#DELETE a stock entry
@app.route('/api/stocks/<int:stock_id>', methods=['DELETE'])
def delete_stock(stock_id):
    stock = Stock.query.get(stock_id)
    if not stock:
        return jsonify(message='Stock entry not found') , 404

    db.session.delete(stock)
    db.session.commit()
    return jsonify(message='Stock entry deleted successfully')


##########################################
#               SALE CRUD OPERATIONS     #
##########################################

#Create a new sale entry
@app.route('/api/sales', methods=['POST'])
def create_sale():
    data = request.json

    data['sale_date'] = datetime.strptime(data['sale_date'], "%Y-%m-%dT%H:%M:%S")

    sale = Sale(**data)
    db.session.add(sale)
    db.session.commit()

    return jsonify(message='Sale entry created successfully')

#get a list of all sales entries
@app.route('/api/sales/', methods=['GET'])
def get_all_sales():
    sales = Sale.query.all()
    sale_list = [{'id': sale.id, 'product_id': sale.product_id, 'quantity_sold': sale.quantity_sold,
                  'sale_date': sale.sale_date, 'total_price': sale.total_price, 'customer_name': sale.customer_name,
                  'payment_method': sale.payment_method, 'notes': sale.notes}
                for sale in sales]
    return jsonify(sales=sale_list)

# Get detials of a specific sale entry
@app.route('/api/sales/<int:sale_id>', methods=['GET'])
def get_sale(sale_id):
    sale = Sale.query.get(sale_id)
    if sale:
        return jsonify(sale={
            'id': sale.id,
            'product_id': sale.product_id,
            'quantity_sold': sale.quantity_sold,
            'sale_date': sale.sale_date,
            'total_price': sale.total_price,
            'customer_name': sale.customer_name,
            'payment_method': sale.payment_method,
            'notes': sale.notes
        })
    else:
        return jsonify(message='Sale entry not found'), 404
    

#update sale entry details
@app.route("/api/sales/<int:sale_id>", methods=['PUT'])
def update_sale(sale_id):
    data = request.json
    sale = Sale.query.get(sale_id)
    if not sale:
        return jsonify(message="sale entry not found"), 404
    
    if 'sale_date' in data:
        data['sale_date'] = datetime.strptime(data['sale_date'], "%Y-%m-%dT%H:%M:%S")
    
    for key, value in data.items():
        setattr(sale, key, value)

    db.session.commit()
    return jsonify(message='sale entry updates successfully')


#Delete a sale entry
@app.route('/api/sale/<int:sale_id>', methods=['DELETE'])
def delete_sale(sale_id):
    sale = Sale.query.get(sale_id)
    if not sale:
        return jsonify(message='Sale entry not found'), 404
    
    db.session.delete(sale)
    db.session.commit()
    return jsonify(message='Sale entry deleted successfully')


@app.route('/api/hello')
def hello():
    return jsonify(message = 'hellow Word')

 
if __name__ == '__main__':
    app.run(debug=True)