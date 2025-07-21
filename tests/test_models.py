######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
Test cases for Product Model
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from unittest.mock import patch
from wsgi import app
from service.models import Product, DataValidationError, db
from .factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  Product   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProduct(TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_product(self):
        """It should create a Product"""
        test_product = ProductFactory()
        test_product.create()
        self.assertIsNotNone(test_product.id)
        data = Product.find(test_product.id)
        self.assertEqual(data.name, test_product.name)
        self.assertEqual(data.description, test_product.description)
        self.assertEqual(float(data.price), test_product.price)
        self.assertEqual(data.available, test_product.available)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = Product(
            name="toothbrush", description="toothbrush", available=True, price=10.12
        )
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)

    def test_read_a_product(self):
        """It should Read a Product"""
        product = ProductFactory()
        logging.debug(product)
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        # Fetch it back
        found_product = Product.find(product.id)
        self.assertEqual(found_product.id, product.id)
        self.assertEqual(found_product.name, product.name)
        self.assertEqual(found_product.description, product.description)

    def test_update_a_product(self):
        """It should Update a Product"""
        product = ProductFactory()
        logging.debug(product)
        product.id = None
        product.create()
        logging.debug(product)
        self.assertIsNotNone(product.id)
        # Change it an save it
        product.description = "toothbrush"
        original_id = product.id
        product.update()
        self.assertEqual(product.id, original_id)
        self.assertEqual(product.description, "toothbrush")
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        products = Product.all()
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].id, original_id)
        self.assertEqual(products[0].description, "toothbrush")

    def test_update_no_id(self):
        """It should not Update a Product with no id"""
        product = ProductFactory()
        logging.debug(product)
        product.id = None
        self.assertRaises(DataValidationError, product.update)

    def test_delete_a_product(self):
        """It should Delete a Product"""
        product = ProductFactory()
        product.create()
        self.assertEqual(len(Product.all()), 1)
        # delete the product and make sure it isn't in the database
        product.delete()
        self.assertEqual(len(Product.all()), 0)

    def test_list_all_products(self):
        """It should List all Products in the database"""
        products = Product.all()
        self.assertEqual(products, [])
        # Create 5 Products
        for _ in range(5):
            product = ProductFactory()
            product.create()
        # See if we get back 5 products
        products = Product.all()
        self.assertEqual(len(products), 5)

    def test_update_product_with_negative_price(self):
        """It should not update a Product with a negative price"""
        product = ProductFactory()
        product.create()
        logging.debug(product)
        product.price = -10
        self.assertRaises(DataValidationError, product.update)

    def test_serialize_a_product(self):
        """It should serialize a Product"""
        product = ProductFactory()
        data = product.serialize()
        self.assertNotEqual(data, None)
        self.assertIn("id", data)
        self.assertEqual(data["id"], product.id)
        self.assertIn("name", data)
        self.assertEqual(data["name"], product.name)
        self.assertIn("description", data)
        self.assertEqual(data["description"], product.description)
        self.assertIn("available", data)
        self.assertEqual(data["available"], product.available)
        self.assertIn("price", data)
        self.assertEqual(data["price"], product.price)

    def test_deserialize_a_product(self):
        """It should de-serialize a Product"""
        data = ProductFactory().serialize()
        product = Product()
        product.deserialize(data)
        self.assertNotEqual(product, None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, data["name"])
        self.assertEqual(product.description, data["description"])
        self.assertEqual(product.available, data["available"])
        self.assertEqual(product.price, data["price"])

    def test_deserialize_missing_data(self):
        """It should not deserialize a Product with missing data"""
        data = {"id": 1, "name": "Kitty", "description": "cat"}
        product = Product()
        self.assertRaises(DataValidationError, product.deserialize, data)

    def test_deserialize_bad_data(self):
        """It should not deserialize bad data"""
        data = "this is not a dictionary"
        product = Product()
        self.assertRaises(DataValidationError, product.deserialize, data)

    def test_deserialize_bad_available(self):
        """It should not deserialize a bad available attribute"""
        test_product = ProductFactory()
        data = test_product.serialize()
        data["available"] = "true"
        product = Product()
        self.assertRaises(DataValidationError, product.deserialize, data)

    def test_find_by_args(self):
        """It should find Products by multiple arguments using find_by_args"""
        # Create several products
        p1 = Product(name="Widget", description="A widget", available=True, price=9.99)
        p2 = Product(
            name="Gadget", description="A gadget", available=False, price=19.99
        )
        p3 = Product(name="Widget", description="A widget", available=True, price=9.99)
        for p in [p1, p2, p3]:
            p.create()
        # Find by name
        results = Product.find_by_args({"name": "Widget"})
        self.assertEqual(len(results), 2)
        for product in results:
            self.assertEqual(product.name, "Widget")
        # Find by name and price
        results = Product.find_by_args({"name": "Widget", "price": 9.99})
        self.assertEqual(len(results), 2)
        for product in results:
            self.assertEqual(product.name, "Widget")
            self.assertEqual(product.price, 9.99)
        # Find by name, price, and available
        results = Product.find_by_args(
            {"name": "Widget", "price": 9.99, "available": True}
        )
        self.assertEqual(len(results), 2)
        for product in results:
            self.assertEqual(product.name, "Widget")
            self.assertEqual(product.price, 9.99)
            self.assertTrue(product.available)
        # Find by description (should match both Widgets)
        results = Product.find_by_args({"description": "A widget"})
        self.assertEqual(len(results), 2)
        for product in results:
            self.assertEqual(product.description, "A widget")
        # Find by available (should match only one Gadget)
        results = Product.find_by_args({"available": False})
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Gadget")
        # Find by price (should match both Widgets)
        results = Product.find_by_args({"price": 9.99})
        self.assertEqual(len(results), 2)
        for product in results:
            self.assertEqual(product.price, 9.99)

    def test_from_args(self):
        """It should create a Product from a dictionary using from_args"""
        args = {
            "name": "TestProduct",
            "description": "A test product",
            "available": True,
            "price": 42.0,
        }
        products = Product.from_args(args)
        self.assertEqual(len(products), 1)
        product = products[0]
        self.assertEqual(product.name, "TestProduct")
        self.assertEqual(product.description, "A test product")
        self.assertTrue(product.available)
        self.assertEqual(product.price, 42.0)
        # Ensure it was actually created in the DB
        found = Product.find(product.id)
        self.assertIsNotNone(found)
        self.assertEqual(found.name, "TestProduct")
        self.assertEqual(found.description, "A test product")
        self.assertTrue(found.available)
        self.assertEqual(found.price, 42.0)


######################################################################
#  T E S T   E X C E P T I O N   H A N D L E R S
######################################################################
class TestExceptionHandlers(TestProduct):
    """Product Model Exception Handlers"""

    @patch("service.models.db.session.commit")
    def test_create_exception(self, exception_mock):
        """It should catch a create exception"""
        exception_mock.side_effect = Exception()
        product = ProductFactory()
        self.assertRaises(DataValidationError, product.create)

    @patch("service.models.db.session.commit")
    def test_update_exception(self, exception_mock):
        """It should catch a update exception"""
        exception_mock.side_effect = Exception()
        product = ProductFactory()
        self.assertRaises(DataValidationError, product.update)

    @patch("service.models.db.session.commit")
    def test_delete_exception(self, exception_mock):
        """It should catch a delete exception"""
        exception_mock.side_effect = Exception()
        product = ProductFactory()
        self.assertRaises(DataValidationError, product.delete)


######################################################################
#  Q U E R Y   T E S T   C A S E S
######################################################################
class TestModelQueries(TestProduct):
    """Product Model Query Tests"""

    def test_find_product(self):
        """It should Find a Product by ID"""
        products = ProductFactory.create_batch(5)
        for product in products:
            product.create()
        logging.debug(products)
        # make sure they got saved
        self.assertEqual(len(Product.all()), 5)
        # find the 2nd product in the list
        product = Product.find(products[1].id)
        self.assertIsNot(product, None)
        self.assertEqual(product.id, products[1].id)
        self.assertEqual(product.name, products[1].name)
        self.assertEqual(product.available, products[1].available)
        self.assertEqual(product.price, products[1].price)

    def test_find_by_description(self):
        """It should Find Products by Description"""
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        description = products[0].description
        count = len(
            [product for product in products if product.description == description]
        )
        found = Product.find_by_description(description)
        self.assertEqual(len(found), count)
        for product in found:
            self.assertEqual(product.description, description)

    def test_find_by_availability(self):
        """It should Find Products by Availability"""
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        available = products[0].available
        count = len([product for product in products if product.available == available])
        found = Product.find_by_availability(available)
        self.assertEqual(found.count(), count)
        for product in found:
            self.assertEqual(product.available, available)

    def test_find_by_price(self):
        """It should Find Products by Price"""
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        price = products[0].price
        count = len([product for product in products if product.price == price])
        found = Product.find_by_price(price)
        self.assertEqual(found.count(), count)
        for product in found:
            self.assertEqual(product.price, price)
