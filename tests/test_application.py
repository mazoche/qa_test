import sqlite3
import pytest
from flask import url_for

from main import create_app, setup_tables, calculate_total_purchase, drop_tables


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

    assert total == 274.85


def test_total_tax(app, client):
    # Remove pass and add a test for tax calculation
    pass


def save_sale(app, client):
    # Remove pass and add a test for saving a sale
    pass


def test_app(app, client):
    assert client.get(url_for('get_homepage')).status_code == 200
    assert client.get(url_for('get_homepage')).data == '<h1>Welcome to My Fashion Shop</h1>'


def test_add_sale(app, client):
    assert client.get(url_for('add_sale')).status_code == 200
    # Add more tests here


def test_get_receipt(app, client):
    # Remove pass and add a test for getting receipts
    pass


def test_get_sales(app, client):
    # Remove pass and add a test for getting receipts
    pass
