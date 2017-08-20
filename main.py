import sqlite3
from flask import (
    Flask,
    jsonify,
    abort,
    render_template
)



db = sqlite3.connect(':memory:')
cursor = db.cursor()


def setup_tables(cursor=None):
    if not cursor:
        cursor = db.cursor()

    cursor.execute('''
    CREATE TABLE receipts(id INTEGER PRIMARY KEY AUTOINCREMENT, total_due FLOAT,
                       tax_due FLOAT, total_purchased FLOAT)
        ''')
    cursor.execute('''
    CREATE TABLE receipt_items(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT,
                       price FLOAT, qty INTEGER, receipt_id INTEGER,
                       FOREIGN KEY(receipt_id) REFERENCES receipts(id))
        ''')
    db.commit()


def drop_tables(cursor=None):
    if not cursor:
        cursor = db.cursor()
    cursor.execute('''DROP TABLE receipts''')
    cursor.execute('''DROP TABLE receipt_items''')
    db.commit()


def calculate_total_purchase(items): ####


    return sum(item['price'] * item['qty']
               for item in items)


def calculate_tax(total, sales_tax): ##

    """
    >>> calculate_tax(100, {'city': .2,'state': .7})
    90.0
    """

    return sum(total * sales_tax[tax_rule]
               for tax_rule in sales_tax)




def calculate_total_due(total_purchased, tax_due):
    """
    >>> calculate_total_due(13, 15)
    28
    >>> calculate_total_due(3.5, 5.5)
    9.0
    >>> calculate_total_due(3, 5.5)
    8.5
    """
    return total_purchased + tax_due


def save_sale(purchase, total_purchased, tax_due, total_due): ###
    cursor = db.cursor()

    cursor.execute('''INSERT INTO receipts(total_purchased, tax_due, total_due)
                  VALUES(?,?,?)''', (total_purchased, tax_due, total_due))
    receipt_id = cursor.lastrowid
    for item in purchase:
        cursor.execute('''INSERT INTO receipt_items(receipt_id, name, price, qty)
                      VALUES(?,?,?,?)''', (receipt_id,
                                           item['name'],
                                           item['qty'],
                                           item['price']))
    db.commit()

    return receipt_id


def print_receipt(items, total_purchased, tax_due, total_due): ####
    receipt = '<html><body>'
    receipt += '<h2>My Fashion Store</h2>'
    receipt += '<hr>'
    receipt += '<br>'.join(['{:.5}    {}    {}'
                           .format(item['name'],
                                   item['qty'],
                                   item['price']) for item in items])
    receipt += '<hr>'
    receipt += '<p>Total: ${0:.2f}</p>'.format(total_purchased)
    receipt += '<p>Tax: ${0:.2f}</p>'.format(tax_due)
    receipt += '<p><strong>Total Due: ${0:.2f}</strong></p>'.format(total_due)
    receipt += '</body></html>'

    return receipt


def complete_sale(purchase, sales_tax): ####
    total_purchased = calculate_total_purchase(purchase)
    tax_due = calculate_tax(total_purchased, sales_tax)
    total_due = calculate_total_due(total_purchased, tax_due)

    receipt_id = save_sale(purchase, total_purchased, tax_due, total_due)

    return receipt_id


def get_sales(): ###
    receipts = []
    for row in db.execute('SELECT * FROM receipts'):
        items = []
        for row2 in db.execute('SELECT * FROM receipt_items WHERE receipt_id == {}'.format(row[0])):
            items.append({'id': row2[0],
                          'name': row2[1],
                          'qty': row2[2],
                          'price': row2[3]})

        receipts.append({'id': row[0],
                         'total_due': row[1],
                         'tax_due': row[2],
                         'total_purchased': row[3],
                         'items': items})
    return receipts


def get_sale(id=None):
    items = []
    row = db.execute('SELECT * FROM receipts where id=?', id).fetchone()

    if row:
        for row2 in db.execute('SELECT * FROM receipt_items WHERE receipt_id=?', (row[0],)):
            items.append({'id': row2[0],
                          'name': row2[1],
                          'qty': row2[2],
                          'price': row2[3]})

        return {'id': row[0],
                'total_due': row[1],
                'tax_due': row[2],
                'total_purchased': row[3],
                'items': items}
    else:
        raise Exception('Receipt {} could not be found.'.format(id))


def create_app():
    app = Flask(__name__)

    app.config['SERVER_NAME'] = '127.0.0.1:5000'
    # app.config['DEBUG'] = True

    @app.before_first_request
    def setup():
        setup_tables()

    @app.route("/")
    def get_homepage_route(): # added route
        return '<h1>Welcome to My Fashion Shop</h1>'

    @app.route("/get-sales")
    def get_sales_route(): # added route
        receipts = get_sales()
        return jsonify(receipts)

    @app.route("/get-receipt/<id>")
    def get_receipt_printout_route(id): # added route
        print (id)
        print (type(id))
        # id is a required parameter
        if not id:
            abort(400)

        try:
            receipt = get_sale(id)
            return print_receipt(receipt['items'],
                                 receipt['total_purchased'],
                                 receipt['tax_due'],
                                 receipt['total_due'])
        except Exception as e:
            return abort(404, str(e))

    @app.route("/add-sale")
    def add_sale_route():  # added route
        purchase = [
            {'name': 't-shirt',
             'qty': 15,
             'price': 9.99
             },
            {'name': 'jeans',
             'qty': 10,
             'price': 12.50
             }
        ]

        sales_tax = {
            'city': .2,
            'state': .7
        }
        receipt_id = complete_sale(purchase, sales_tax)
        return jsonify({'receiptId': receipt_id})

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('page_not_found.html', error=error), 404

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(port=5000)
