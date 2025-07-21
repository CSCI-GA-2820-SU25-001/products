"""
Models for Product

All of the models are stored in this module
"""

import logging
from flask_sqlalchemy import SQLAlchemy


logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


class DataValidationError(Exception):
    """Used for an data validation errors when deserializing"""


class Product(db.Model):
    """
    Class that represents a Product
    """

    ##################################################
    # Table Schema
    ##################################################
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(63), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    price = db.Column(db.Float, nullable=True)
    available = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f"<Product {self.name} id=[{self.id}]>"

    def create(self):
        """
        Creates a Product to the database
        """
        logger.info("Creating %s", self.name)
        self.id = None  # pylint: disable=invalid-name
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error creating record: %s", self)
            raise DataValidationError(e) from e

    def update(self):
        """Updates a Product to the database"""
        logger.info("Saving %s", self.name)
        print(self.price, "I am here!!!!")
        if not self.id:
            raise DataValidationError("Update called with empty ID field")
        if self.price is None or float(self.price) < float(0.00):
            raise DataValidationError("Price must be a positive number")
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error updating record: %s", self)
            raise DataValidationError(e) from e

    def delete(self):
        """Removes a Product from the data store"""
        logger.info("Deleting %s", self.name)
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error deleting record: %s", self)
            raise DataValidationError(e) from e

    def serialize(self):
        """Serializes a Product into a dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "available": self.available,
        }

    def deserialize(self, data: dict):
        """
        Deserializes a Product from a dictionary
        Args:
            data (dict): A dictionary containing the Product data
        """
        try:
            self.name = data["name"]
            self.description = data["description"]
            if isinstance(data["available"], bool):
                self.available = data["available"]
            else:
                raise DataValidationError(
                    "Invalid type for boolean [available]: "
                    + str(type(data["available"]))
                )
            self.price = data["price"]  # create enum from string
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid product: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid product: body of request contained bad or no data "
                + str(error)
            ) from error
        return self

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def all(cls):
        """Returns all of the Products in the database"""
        logger.info("Processing all Products")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """Finds a Product by it's ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.session.get(cls, by_id)

    @classmethod
    def find_by_name(cls, name):
        """Returns all Products with the given name

        Args:
            name (string): the name of the Products you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name).all()

    @classmethod
    def find_by_description(cls, description: str) -> list:
        """Returns all of the Products in a description

        :param description: the description of the Products you want to match
        :type description: str

        :return: a collection of Products in that description
        :rtype: list

        """
        logger.info("Processing description query for %s ...", description)
        return cls.query.filter(cls.description == description).all()

    @classmethod
    def find_by_availability(cls, available: bool = True) -> list:
        """Returns all Products by their availability

        :param available: True for products that are available
        :type available: str

        :return: a collection of Products that are available
        :rtype: list

        """
        if not isinstance(available, bool):
            raise TypeError("Invalid availability, must be of type boolean")
        logger.info("Processing available query for %s ...", available)
        return cls.query.filter(cls.available == available)

    @classmethod
    def find_by_price(cls, price: float) -> list:
        """Returns all Products by their Price

        :param price: values are float
        :type available: enum

        :return: a collection of Products that are available
        :rtype: list

        """
        logger.info("Processing price query for %s ...", price)
        return cls.query.filter(cls.price == price)

    @classmethod
    def from_args(cls, args) -> list:
        """Creates a list of Products from the given arguments

        :param args: the arguments containing Product data
        :type args: dict

        :return: a list of Products created from the arguments
        :rtype: list

        """
        logger.info("Creating Products from args: %s", args)
        products = []
        try:
            product = cls()
            product.deserialize(args)
            product.create()
            products.append(product)
        except Exception as e:
            logger.error("Error creating product from args: %s", e)
            raise DataValidationError(e) from e
        return products

    @classmethod
    def find_by_args(cls, args) -> list:
        """Finds Products based on the given arguments

        :param args: the arguments to filter Products by
        :type args: dict

        :return: a list of Products that match the given arguments
        :rtype: list

        """
        logger.info("Finding Products by args: %s", args)
        query = cls.query
        if args.get("name"):
            query = query.filter(cls.name == args["name"])
        if args.get("description"):
            query = query.filter(cls.description == args["description"])
        if args.get("available") is not None:
            query = query.filter(cls.available == args["available"])
        if args.get("price") is not None:
            query = query.filter(cls.price == args["price"])
        return query.all()
