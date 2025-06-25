Conditional Order API Documentation
Overview
The Conditional Order API automates the creation of sale orders in Odoo 17 based on stock availability. If stock is sufficient, a sale order is created directly. If stock is insufficient, a purchase order is created to replenish stock, and a sale order is linked to it via a procurement group for reservation/forecasting.
Endpoint: /api/create_sale_order
Method

POST

Authentication

Requires Odoo user authentication via API key or session token.
Users must have permissions for sale.order, purchase.order, and product.product.

Request Body

Content-Type: application/json
Format:

{
  "product_id": <integer>,
  "quantity": <float>,
  "customer_id": <integer>
}


Fields:
product_id: ID of the product (required).
quantity: Requested quantity (required, must be > 0).
customer_id: ID of the customer (required).



Response

Success (Stock Available):

{
  "status": "success",
  "sale_order_id": <integer>,
  "message": "Sale order created successfully."
}


Success (Stock Unavailable):

{
  "status": "success",
  "sale_order_id": <integer>,
  "message": "Purchase and sale order created successfully."
}


Error:

{
  "status": "error",
  "message": "<error_message>"
}


Example Errors:
"Product ID X does not exist."
"Customer ID Y does not exist."
"No vendor configured for product Z."
"Quantity must be greater than zero."



Example Request
curl -X POST https://your_domain.com/api/create_sale_order \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_api_token>" \
  -d '{
    "product_id": 1,
    "quantity": 5.0,
    "customer_id": 1
  }'

Example Response

Success:

{
  "status": "success",
  "sale_order_id": 42,
  "message": "Sale order created successfully."
}


Error:

{
  "status": "error",
  "message": "Product ID 9999 does not exist."
}

Setup Instructions

Install the Module:

Place the conditional_order_api directory in Odoo's addons path (e.g., /mnt/extra-addons).
Update the module list in Odoo UI (Apps > Update Apps List).
Install the Conditional Order API module.


Configure Dependencies:

Ensure sale_management, purchase, and stock modules are installed.
Configure products with vendors (seller_ids) for purchase order creation.


Generate API Token:

Create a user with appropriate permissions.
Generate an API key in Settings > Users & Companies > Users > Developer Settings.


Run Unit Tests:

Execute tests via Odoo CLI:docker-compose exec odoo odoo -i conditional_order_api -t conditional_order_api





Testing

Unit tests are located in tests/test_order_api.py.
Tests cover:
Sale order creation with sufficient stock.
Purchase and sale order creation with insufficient stock.
Error handling for invalid inputs.


Run tests to validate functionality before deployment.

Notes

The API uses procurement groups to reserve/forecast stock, ensuring proper stock allocation.
Logs are generated for all actions (e.g., stock checks, order creation) under the conditional_order_api logger.
Secure the endpoint with HTTPS and restricted IP access in production.
Monitor Odoo logs for errors: docker-compose logs odoo | grep conditional_order_api.

Troubleshooting

Authentication Errors: Verify API token and user permissions.
Vendor Missing: Ensure products have configured vendors in seller_ids.
Stock Issues: Check product stock in Inventory > Products.
Logs: Enable debug logging (--log-level=debug) for detailed traces.

