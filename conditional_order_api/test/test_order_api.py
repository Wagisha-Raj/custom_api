from odoo.tests import HttpCase
import json

class TestConditionalOrderAPI(HttpCase):
    def setUp(self):
        super().setUp()
        self.product = self.env['product.product'].create({
            'name': 'Test Product',
            'type': 'product',
            'list_price': 10.0,
            'standard_price': 8.0,
            'uom_id': self.env.ref('uom.product_uom_unit').id,
        })
        self.customer = self.env['res.partner'].create({
            'name': 'Test Customer',
            'customer_rank': 1,
        })
        self.vendor = self.env['res.partner'].create({
            'name': 'Test Vendor',
            'supplier_rank': 1,
        })
        self.env['product.supplierinfo'].create({
            'partner_id': self.vendor.id,
            'product_id': self.product.id,
            'price': 8.0,
        })
        self.env['stock.quant'].create({
            'product_id': self.product.id,
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'quantity': 10.0,
        })

    def test_create_sale_order_sufficient_stock(self):
        payload = {
            'product_id': self.product.id,
            'quantity': 5.0,
            'customer_id': self.customer.id
        }
        response = self.url_open(
            '/api/create_sale_order',
            data=json.dumps(payload),
            headers={'Content-Type': 'application/json'}
        )
        result = response.json()
        self.assertEqual(result['status'], 'success')
        self.assertIn('sale_order_id', result)
        self.assertEqual(result['message'], 'Sale order created successfully')

        # Verify stock
        stock_quant = self.env['stock.quant'].search([
            ('product_id', '=', self.product.id),
            ('location_id.usage', '=', 'internal')
        ])
        available_quantity = sum(quant.quantity - quant.reserved_quantity for quant in stock_quant)
        self.assertEqual(available_quantity, 5.0)
