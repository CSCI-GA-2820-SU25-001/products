[![CI Build](https://github.com/nyu-devops/lab-flask-tdd/actions/workflows/ci.yml/badge.svg)](https://github.com/nyu-devops/lab-flask-tdd/actions/workflows/ci.yml)

# Product Service

## Overview

This is a RESTful Product microservice for managing product records in an online store. The service is built using Flask and PostgreSQL, and supports full CRUD operations along with query filtering.

The `/service` folder contains the business logic and service endpoints. The `/tests` folder contains model and route-level unit tests.

---

## Contents

```
├── .flaskenv                  # Flask environment settings
├── dot-env-example            # Template for .env environment config
├── Makefile                   # Common development commands
├── pyproject.toml             # Python dependencies via Poetry

service/                       # Service package
├── __init__.py                # Package initializer
├── config.py                  # Configuration parameters
├── models.py                  # Product data model and DB logic
├── routes.py                  # REST API route handlers
└── common/                    # Common shared utilities
    ├── cli_commands.py        # Flask CLI: init/reset database
    ├── error_handlers.py      # Global error handlers
    ├── log_handlers.py        # Logging setup
    └── status.py              # HTTP status code definitions

tests/                         # Test suite
├── __init__.py
├── factories.py               # Factory for creating test data
├── test_models.py             # Unit tests for models
├── test_routes.py             # Unit tests for API routes
```

---

## API Endpoints

| Method | Endpoint             | Description                     |
|--------|----------------------|---------------------------------|
| GET    | `/`                  | Returns service metadata        |
| POST   | `/products`          | Creates a new product           |
| GET    | `/products`          | Lists all products              |
| GET    | `/products/{id}`     | Gets a product by ID            |
| PUT    | `/products/{id}`     | Updates a product by ID         |
| DELETE | `/products/{id}`     | Deletes a product by ID         |
| GET    | `/products?name=...` | Finds products by name          |
| GET    | `/products?description=...` | Finds products by description |
| GET    | `/products?available=true or false` | Finds products by availability |

**Create a Product**  
```bash
http POST :8080/products name="Toothbrush" description="Soft bristles" price:=9.99 available:=true
```

**List All Products**  
```bash
http GET :8080/products
```

**Read a Product by ID**  
```bash
http GET :8080/products/1
```

**Update a Product by ID**  
```bash
http PUT :8080/products/1 name="Updated Brush" description="Hard bristles" price:=12.99 available:=false
```

**Delete a Product by ID**  
```bash
http DELETE :8080/products/1
```

**Query Products by Name**  
```bash
http GET :8080/products?name=Toothbrush
```

**Query Products by Availability**  
```bash
http GET :8080/products?available=true
```

##  Error Handling

All errors return JSON responses only:

- **404 Not Found** – if the product ID doesn’t exist  
- **400 Bad Request** – for malformed request body  
- **415 Unsupported Media Type** – if `Content-Type` is not `application/json`  
- **405 Method Not Allowed** – e.g., using `PUT /products` without ID

---


## Running the Service

### Prerequisites

- Python 3.9+
- PostgreSQL running locally or via Docker
- Git

---

### Initial Setup

Clone the repository and install dependencies:

```bash
git clone https://github.com/CSCI-GA-2820-SU25-001/products.git

cd products
```

---

### Running Locally

Start the service using:

```bash
make run
```

The service will be available at `http://localhost:8080`.

---

## Testing

Run the full test suite:

```bash
make test
```

Run individual test files:

```bash
pytest tests/test_models.py
pytest tests/test_routes.py
```

Code coverage: **96%**

---

## Development Commands

| Command         | Description                             |
|----------------|-----------------------------------------|
| `make install` | Install all Python dependencies         |
| `make lint`    | Run flake8 for code style checks        |
| `make run`     | Start the Flask service via Honcho      |
| `make test`    | Run all unit tests with coverage        |
| `make secret`  | Generate a new Flask secret key         |
| `make clean`   | Remove build and cache artifacts        |


---

## License

Copyright (c) 2016, 2025 [John Rofrano](https://www.linkedin.com/in/JohnRofrano/). All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE)

This repository is part of the New York University (NYU) masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** created and taught by [John Rofrano](https://cs.nyu.edu/~rofrano/), Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science, and NYU Stern School of Business.
