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
TestProduct API Service Test Suite
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from urllib.parse import quote_plus
from wsgi import app
from service.common import status
from service.models import db, Product
from .factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)

BASE_URL = "/api/products"


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProduct(TestCase):
    """REST API Server Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ############################################################
    # Utility function to bulk create products
    ############################################################
    def _create_products(self, count: int = 1) -> list:
        """Factory method to create products in bulk"""
        products = []
        for i in range(count):
            test_product = ProductFactory()
            test_product.available = i % 2 == 0
            response = self.client.post(BASE_URL, json=test_product.serialize())
            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
                "Could not create test product",
            )
            new_product = response.get_json()
            test_product.id = new_product["id"]
            products.append(test_product)
        return products

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """It should call the home page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    # ----------------------------------------------------------
    # TEST LIST
    # ----------------------------------------------------------
    def test_get_list(self):
        """It should Get a list of Products"""
        self._create_products(5)
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 5)

        # Verify that each product in the list has the new fields
        for product in data:
            self.assertIn("name", product)
            self.assertIn("description", product)
            self.assertIn("price", product)
            self.assertIn("available", product)

    # ----------------------------------------------------------
    # TEST Health
    # ----------------------------------------------------------

    def test_health(self):
        """It should get the health endpoint"""
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["status"], "OK")

    # ----------------------------------------------------------
    # TEST QUERY
    # ----------------------------------------------------------

    def test_query_by_name(self):
        """It should Query Products by name"""
        products = self._create_products(5)
        test_name = products[0].name
        name_count = len([product for product in products if product.name == test_name])
        response = self.client.get(
            BASE_URL, query_string=f"name={quote_plus(test_name)}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), name_count)
        # check the data just to be sure
        for product in data:
            self.assertEqual(product["name"], test_name)

    def test_query_product_list_by_description(self):
        """It should Query Products by Description"""
        products = self._create_products(10)
        test_description = products[0].description
        description_products = [
            product for product in products if product.description == test_description
        ]
        response = self.client.get(
            BASE_URL, query_string=f"description={quote_plus(test_description)}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), len(description_products))
        # check the data just to be sure
        for product in data:
            self.assertEqual(product["description"], test_description)

    def test_query_by_availability(self):
        """It should Query Products by availability"""
        products = self._create_products(10)
        available_products = [
            product for product in products if product.available is True
        ]
        unavailable_products = [
            product for product in products if product.available is False
        ]
        available_count = len(available_products)
        unavailable_count = len(unavailable_products)
        logging.debug("Available Products [%d] %s", available_count, available_products)
        logging.debug(
            "Unavailable Products [%d] %s", unavailable_count, unavailable_products
        )

        # test for available
        response = self.client.get(BASE_URL, query_string="available=true")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), available_count)
        # check the data just to be sure
        for product in data:
            self.assertEqual(product["available"], True)

        # test for unavailable
        response = self.client.get(BASE_URL, query_string="available=false")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), unavailable_count)
        # check the data just to be sure
        for product in data:
            self.assertEqual(product["available"], False)

    def test_query_by_price(self):
        """It should Query Products by price"""
        products = self._create_products(10)
        price = products[0].price
        price_count = len([p for p in products if p.price == price])
        response = self.client.get(BASE_URL, query_string=f"price={price}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), price_count)
        for product in data:
            self.assertEqual(product["price"], price)

    # ----------------------------------------------------------
    # TEST CREATE
    # ----------------------------------------------------------
    def test_create_product(self):
        """It should Create a new Product"""
        test_product = ProductFactory()
        logging.debug("Test product: %s", test_product.serialize())
        response = self.client.post(BASE_URL, json=test_product.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_product = response.get_json()
        self.assertEqual(new_product["name"], test_product.name)
        self.assertEqual(new_product["description"], test_product.description)
        self.assertAlmostEqual(
            float(new_product["price"]), float(test_product.price), places=2
        )
        self.assertEqual(new_product["available"], test_product.available)

    # ----------------------------------------------------------
    # TEST UPDATE
    # ----------------------------------------------------------
    def test_update_product(self):
        """It should Update an existing Product"""
        # create a product to update
        test_product = ProductFactory()
        response = self.client.post(BASE_URL, json=test_product.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # update the product
        new_product = response.get_json()
        logging.debug(new_product)
        new_product["name"] = "toothbrush"
        new_product["description"] = "unknown"
        new_product["price"] = 19.99
        new_product["available"] = False

        response = self.client.put(f"{BASE_URL}/{new_product['id']}", json=new_product)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_product = response.get_json()
        self.assertEqual(updated_product["name"], "toothbrush")
        self.assertEqual(updated_product["description"], "unknown")
        self.assertAlmostEqual(float(updated_product["price"]), 19.99, places=2)
        self.assertEqual(updated_product["available"], False)

    # ----------------------------------------------------------
    # TEST DELETE
    # ----------------------------------------------------------
    def test_delete_product(self):
        """It should Delete a Product"""
        test_product = self._create_products(1)[0]
        response = self.client.delete(f"{BASE_URL}/{test_product.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)
        # make sure they are deleted
        response = self.client.get(f"{BASE_URL}/{test_product.id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_non_existing_product(self):
        """It should Delete a Product even if it doesn't exist"""
        response = self.client.delete(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)

    # ----------------------------------------------------------
    # TEST READ
    # ----------------------------------------------------------
    def test_get_product(self):
        """It should Get a single Product"""
        # get the id of a product
        test_product = self._create_products(1)[0]
        response = self.client.get(f"{BASE_URL}/{test_product.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["name"], test_product.name)

        # New assertions for added fields
        self.assertEqual(data["description"], test_product.description)
        self.assertAlmostEqual(
            float(data["price"]), float(test_product.price), places=2
        )
        self.assertEqual(data["available"], test_product.available)

    def test_get_product_not_found(self):
        """It should not Get a Product thats not found"""
        response = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        logging.debug("Response data = %s", data)
        self.assertIn("was not found", data["message"])

    def test_purchase_not_found(self):
        """It should not Purchase a Product that is not found"""
        response = self.client.put(f"{BASE_URL}/0/purchase")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        logging.debug("Response data = %s", data)
        self.assertIn("was not found", data["message"])


######################################################################
#  T E S T   S A D   P A T H S
######################################################################
class TestSadPaths(TestCase):
    """Test REST Exception Handling"""

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()

    def test_method_not_allowed(self):
        """It should not allow update without a product id"""
        response = self.client.put(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_create_product_no_data(self):
        """It should not Create a Product with missing data"""
        response = self.client.post(BASE_URL, json={})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_product_no_content_type(self):
        """It should not Create a Product with no content type"""
        response = self.client.post(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_product_wrong_content_type(self):
        """It should not Create a Product with the wrong content type"""
        response = self.client.post(BASE_URL, data="hello", content_type="text/html")
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_product_bad_available(self):
        """It should not Create a Product with bad available data"""
        test_product = ProductFactory()
        logging.debug(test_product)
        # change available to a string
        test_data = test_product.serialize()
        test_data["available"] = "yes"
        response = self.client.post(BASE_URL, json=test_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
