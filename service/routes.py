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
YourResourceModel Service

This service implements a REST API that allows you to Create, Read, Update
and Delete YourResourceModel
"""

import secrets
from flask import Blueprint, request
from flask_restx import Api, Resource, fields, reqparse, abort
from service.models import Product, DataValidationError
from service.common import status

# Blueprint + Flask-RESTX API
api_bp = Blueprint("api", __name__)
api = Api(
    api_bp,
    version="1.0.0",
    title="Product Demo REST API Service",
    description="This is a sample Product microservice",
    doc="/apidocs",  # Swagger UI
    prefix="/api"
)

# Authorization config (if needed later)
authorizations = {
    "apikey": {"type": "apiKey", "in": "header", "name": "X-Api-Key"}
}
api.authorizations = authorizations

# Namespace for products
ns = api.namespace("products", description="Product operations")

# Data Model for Swagger
product_model = api.model("Product", {
    "id": fields.Integer(readOnly=True),
    "name": fields.String(required=True, description="Product name"),
    "description": fields.String(required=False),
    "price": fields.Float(required=False),
    "available": fields.Boolean(required=False),
})

# Query parser
product_args = reqparse.RequestParser()
product_args.add_argument("name", type=str)
product_args.add_argument("description", type=str)
product_args.add_argument("available", type=bool)
product_args.add_argument("price", type=float)


@ns.route("/")
class ProductCollection(Resource):
    """Handles collection-level operations for Products"""
    @ns.expect(product_args)
    @ns.marshal_list_with(product_model)
    def get(self):
        """List or filter products"""
        args = product_args.parse_args()
        if args["description"]:
            return Product.find_by_description(args["description"])
        if args["name"]:
            return Product.find_by_name(args["name"])
        if args["available"] is not None:
            available_str = str(request.args.get("available")).lower()
            if available_str == "true":
                return [p.serialize() for p in Product.find_by_availability(True)]
            if available_str == "false":
                return [p.serialize() for p in Product.find_by_availability(False)]
            abort(status.HTTP_400_BAD_REQUEST, "Invalid value for 'available'. Must be 'true' or 'false'.")
        if args["price"]:
            return Product.find_by_price(args["price"])
        return Product.all()

    @ns.expect(product_model)
    @ns.marshal_with(product_model, code=201)
    def post(self):
        """Create a new product"""
        product = Product()
        try:
            product.deserialize(api.payload)
        except (DataValidationError, KeyError, TypeError) as error:
            abort(status.HTTP_400_BAD_REQUEST, str(error))
        product.create()
        return product.serialize(), 201, {"Location": api.url_for(ProductResource, product_id=product.id)}


@ns.route("/<int:product_id>")
@ns.param("product_id", "The product ID")
class ProductResource(Resource):
    """Handles item-level operations for Products"""
    @ns.marshal_with(product_model)
    def get(self, product_id):
        """Get a product by ID"""
        product = Product.find(product_id)
        if not product:
            api.abort(status.HTTP_404_NOT_FOUND, f"Product with id {product_id} was not found")
        return product.serialize()

    @ns.expect(product_model)
    @ns.marshal_with(product_model)
    def put(self, product_id):
        """Update a product by ID"""
        product = Product.find(product_id)
        if not product:
            api.abort(status.HTTP_404_NOT_FOUND, f"Product with id {product_id} not found")
        product.deserialize(api.payload)
        product.update()
        return product.serialize()

    def delete(self, product_id):
        """Delete a product by ID"""
        product = Product.find(product_id)
        if product:
            product.delete()
        return "", status.HTTP_204_NO_CONTENT


# Optional: for testing root URL
@api_bp.route("/")
def index():
    """Base URL for our service"""
    return app.send_static_file("index.html")


######################################################################
# CREATE A NEW PRODUCT
######################################################################
@app.route("/products", methods=["POST"])
def create_products():
    """
    Create a Product
    This endpoint will create a product based the data in the body that is posted
    """
    app.logger.info("Request to Create a product...")
    check_content_type("application/json")

    product = Product()
    # Get the data from the request and deserialize it
    data = request.get_json()
    app.logger.info("Processing: %s", data)
    product.deserialize(data)

    # Save the new product to the database
    product.create()
    app.logger.info("product with new id [%s] saved!", product.id)

    # Return the location of the new product
    location_url = url_for("get_products", product_id=product.id, _external=True)
    return (
        jsonify(product.serialize()),
        status.HTTP_201_CREATED,
        {"Location": location_url},
    )


######################################################################
# UPDATE A PRODUCT
######################################################################
@app.route("/products/<int:product_id>", methods=["PUT"])
def update_products(product_id):
    """
    Update a Product
    This endpoint will update a Product based the body that is posted
    """
    app.logger.info("Request to Update a product with id [%s]", product_id)
    check_content_type("application/json")

    # Attempt to find the Product and abort if not found
    product = Product.find(product_id)
    if not product:
        abort(
            status.HTTP_404_NOT_FOUND, f"Product with id '{product_id}' was not found."
        )

    # Update the Product with the new data
    data = request.get_json()
    app.logger.info("Processing: %s", data)
    product.deserialize(data)

    # Save the updates to the database
    product.update()

    app.logger.info("Product with ID: %d updated.", product.id)
    return jsonify(product.serialize()), status.HTTP_200_OK


######################################################################
# DELETE A PRODUCT
######################################################################
@app.route("/products/<int:product_id>", methods=["DELETE"])
def delete_products(product_id):
    """
    Delete a Product
    This endpoint will delete a Product based the id specified in the path
    """
    app.logger.info("Request to Delete a product with id [%s]", product_id)

    # Delete the Product if it exists
    product = Product.find(product_id)
    if product:
        app.logger.info("Product with ID: %d found.", product.id)
        product.delete()

    app.logger.info("Product with ID: %d delete complete.", product_id)
    return {}, status.HTTP_204_NO_CONTENT


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


######################################################################
# Checks the ContentType of a request
######################################################################
def check_content_type(content_type) -> None:
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {content_type}",
    )


######################################################################
# READ A PRODUCT
######################################################################


@app.route("/products/<int:product_id>", methods=["GET"])
def get_products(product_id):
    """
    Retrieve a single Product

    This endpoint will return a Product based on it's id
    """
    app.logger.info("Request to Retrieve a product with id [%s]", product_id)

    # Attempt to find the Product and abort if not found
    product = Product.find(product_id)
    if not product:
        abort(
            status.HTTP_404_NOT_FOUND, f"Product with id '{product_id}' was not found."
        )

    app.logger.info("Returning product: %s", product.name)
    return jsonify(product.serialize()), status.HTTP_200_OK


######################################################################
# LIST ALL PRODUCTS
######################################################################
@app.route("/products", methods=["GET"])
def list_products():
    """Returns all of the Products"""
    app.logger.info("Request for product list")

    products = []

    # Parse any arguments from the query string
    name = request.args.get("name")
    description = request.args.get("description")
    available = request.args.get("available")
    price = request.args.get("price")

    if description:
        app.logger.info("Find by description: %s", description)
        products = Product.find_by_description(description)
    elif name:
        app.logger.info("Find by name: %s", name)
        products = Product.find_by_name(name)
    elif available:
        app.logger.info("Find by available: %s", available)
        # create bool from string
        available_value = available.lower() in ["true", "yes", "1"]
        products = Product.find_by_availability(available_value)
    elif price:
        app.logger.info("Find by price: %d", price)
        # create enum from string
        products = Product.find_by_price(price)
    else:
        app.logger.info("Find all")
        products = Product.all()

    results = [product.serialize() for product in products]
    app.logger.info("Returning %d products", len(results))
    return jsonify(results), status.HTTP_200_OK


# Utility function if needed elsewhere
def generate_apikey():
    """Generates a secure API key"""
    return secrets.token_hex(16)


@api.route("/products", methods=["PUT"])
class ProductMethodNotAllowed(Resource):
    """Handles invalid PUT requests on the product collection"""
    def put(self):
        """Returns 405 Method Not Allowed for PUT on /products"""
        abort(status.HTTP_405_METHOD_NOT_ALLOWED, "Method not allowed")
