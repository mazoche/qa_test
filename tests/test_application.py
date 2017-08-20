import sqlite3
import pytest
import json

from flask import url_for

from main import (
    create_app,
    setup_tables,
    calculate_total_purchase,
    drop_tables,
    complete_sale,
    get_sale,
    print_receipt
)

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
db = sqlite3.connect(':memory:')
cursor = db.cursor()


@pytest.fixture(scope='session')
def app(request):
    # Create the basic table structure
    setup_tables(cursor)

    # This function can be used to pre-load data into the database or other
    # common test setup tasks

    def teardown():
        drop_tables(cursor)

    request.addfinalizer(teardown)

    app = create_app()
    app_context = app.app_context()
    app_context.push()
    app.testing = True
    return app


@pytest.yield_fixture
def client(app):
    """A Flask test client. An instance of :class:`flask.testing.TestClient`
    by default.
    """
    with app.test_client() as client:
        yield client


# Basic calculation test
def test_total_purchase(app, client):

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

    total = calculate_total_purchase(purchase)

    assert total == 274.85, "Computing total purchase failed"


def test_total_tax(app, client):  # no need of this one it is a docktest now
    # Remove pass and add a test for tax calculation
    pass


def test_save_sale(app, client):
    # Remove pass and add a test for saving a sale

    # init part
    purchase = [  # NOQA
            {'name': 't-shirt',
             'qty': 15,
             'price': 9.99
             },
            {'name': 'jeans',
             'qty': 10,
             'price': 12.50
             }
        ]


def test_app(app, client):
    assert client.get(url_for('get_homepage_route')).status_code == 200
    assert client.get(url_for('get_homepage_route')).data == b'<h1>Welcome to My Fashion Shop</h1>'


def test_add_sale(app, client):
    # Add more tests here

    response = client.get(url_for('add_sale_route'))
    assert response.status_code == 200
    assert json.loads(response.data) == {'receiptId': 1}
    assert complete_sale(purchase, sales_tax) == 2


def test_error_handler(app, client):
    response1 = client.get("/fakeurl")
    assert response1.status_code == 404, "Page not found handler missing"
    response = client.get(url_for('get_receipt_printout_route', id=False))
    assert response.status_code == 404, "Bad request handler missing"


def test_get_receipt(app, client):

    response_receipt = client.get(url_for('get_receipt_printout_route', id=1))
    receipt = get_sale("1")
    show = print_receipt(
        receipt['items'],
        receipt['total_purchased'],
        receipt['tax_due'],
        receipt['total_due']
    )

    assert response_receipt.status_code == 200
    assert response_receipt.data == bytearray(show, encoding="utf-8")
    assert response_receipt.data == b'<html><body><h2>My Fashion Store</h2><hr>t-shi    15.0    9.99' \
                                    b'<br>jeans    10.0    12.5<hr><p>Total: $274.85</p>' \
                                    b'<p>Tax: $247.37</p><p><strong>Total Due: $522.22</strong></p></body></html>'


def test_get_sales(app, client):
    response_sales = client.get(url_for('get_sales_route'))

    if not cursor.rowcount == 0:

        show = [
            {
                "id": 1,
                "items": [
                  {
                    "id": 1,
                    "name": "t-shirt",
                    "price": 9.99,
                    "qty": 15.0
                  },
                  {
                    "id": 2,
                    "name": "jeans",
                    "price": 12.5,
                    "qty": 10.0
                  }
                ],
                "tax_due": 247.365,
                "total_due": 522.215,
                "total_purchased": 274.85
            },
            {
                "id": 2,
                "items": [
                  {
                    "id": 3,
                    "name": "t-shirt",
                    "price": 9.99,
                    "qty": 15.0
                  },
                  {
                    "id": 4,
                    "name": "jeans",
                    "price": 12.5,
                    "qty": 10.0
                  }
                ],
                "tax_due": 247.365,
                "total_due": 522.215,
                "total_purchased": 274.85
            }
        ]

    assert response_sales.status_code == 200
    assert json.loads(response_sales.data) == show


def test_exeption(app, client):
    with pytest.raises(Exception) as excinfo:
        get_sale("9")
    assert str(excinfo.value) == 'Receipt {} could not be found.'.format(9)


def test_multi_digit_sale(app, client):
    for i in range(9):
        response = client.get(url_for('add_sale_route'))
        assert response.status_code == 200
    assert get_sale("9"), "single digit sale not working"
    assert get_sale("10"), "multi digit sale not working"
