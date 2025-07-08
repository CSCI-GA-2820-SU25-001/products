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
from flask import Blueprint, request, current_app
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
    prefix="/api",
)

# Authorization config (if needed later)
authorizations = {"apikey": {"type": "apiKey", "in": "header", "name": "X-Api-Key"}}
api.authorizations = authorizations

# Namespace for products
ns = api.namespace("products", description="Product operations")

# Data Model for Swagger
product_model = api.model(
    "Product",
    {
        "id": fields.Integer(readOnly=True),
        "name": fields.String(required=True, description="Product name"),
        "description": fields.String(required=False),
        "price": fields.Float(required=False),
        "available": fields.Boolean(required=False),
    },
)

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
            abort(
                status.HTTP_400_BAD_REQUEST,
                "Invalid value for 'available'. Must be 'true' or 'false'.",
            )
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
        return (
            product.serialize(),
            201,
            {"Location": api.url_for(ProductResource, product_id=product.id)},
        )


@ns.route("/<int:product_id>")
@ns.param("product_id", "The product ID")
class ProductResource(Resource):
    """Handles item-level operations for Products"""

    @ns.marshal_with(product_model)
    def get(self, product_id):
        """Get a product by ID"""
        product = Product.find(product_id)
        if not product:
            api.abort(
                status.HTTP_404_NOT_FOUND, f"Product with id {product_id} was not found"
            )
        return product.serialize()

    @ns.expect(product_model)
    @ns.marshal_with(product_model)
    def put(self, product_id):
        """Update a product by ID"""
        product = Product.find(product_id)
        if not product:
            api.abort(
                status.HTTP_404_NOT_FOUND, f"Product with id {product_id} not found"
            )
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
    """Returns a simple HTML page with link to API docs"""
    return current_app.send_static_file("index.html")


@api.route("/products", methods=["PUT"])
class ProductMethodNotAllowed(Resource):
    """Handles invalid PUT requests on the product collection"""

    def put(self):
        """Returns 405 Method Not Allowed for PUT on /products"""
        abort(status.HTTP_405_METHOD_NOT_ALLOWED, "Method not allowed")


# Utility function if needed elsewhere
def generate_apikey():
    """Generates a secure API key"""
    return secrets.token_hex(16)


@api.errorhandler
def default_error_handler(error):
    """Defines the default errorhandler"""
    message = str(error)
    return {"message": message}, getattr(error, "code", 500)
