from odoo import http
from odoo.http import request
import logging
import json

_logger = logging.getLogger(__name__)

class ConditionalOrderAPI(http.Controller):
    @http.route('/api/create_sale_order', type='json', auth='public', methods=['POST'])
    def create_sale_order(self):
        try:
            # Parse JSON body
            data = json.loads(request.httprequest.get_data(as_text=True))
            product_id = data.get('product_id')
            quantity = data.get('quantity')
            customer_id = data.get('customer_id')

            if not all([product_id, quantity, customer_id]):
                return {'status': 'error', 'message': 'Missing required parameters'}

            product = request.env['product.product'].sudo().browse(product_id)
            if not product.exists():
                return {'status': 'error', 'message': 'Product not found'}

            partner = request.env['res.partner'].sudo().browse(customer_id)
            if not partner.exists():
                return {'status': 'error', 'message': 'Customer not found'}

            stock_quant = request.env['stock.quant'].sudo().search([
                ('product_id', '=', product_id),
                ('location_id.usage', '=', 'internal')
            ], limit=1)
            available_quantity = stock_quant.quantity - stock_quant.reserved_quantity if stock_quant else 0

            if available_quantity >= quantity:
                sale_order = request.env['sale.order'].sudo().create({
                    'partner_id': customer_id,
                    'order_line': [(0, 0, {
                        'product_id': product_id,
                        'product_uom_qty': quantity,
                    })]
                })
                sale_order.action_confirm()
                _logger.info(f"Sale order {sale_order.name} created for product {product.name}")
                return {'status': 'success', 'sale_order_id': sale_order.id, 'message': 'Sale order created successfully'}
            else:
                purchase_order = request.env['purchase.order'].sudo().create({
                    'partner_id': partner.id,  # Use supplier_id for purchase
                    'order_line': [(0, 0, {
                        'product_id': product_id,
                        'product_qty': quantity,
                    })]
                })
                sale_order = request.env['sale.order'].sudo().create({
                    'partner_id': customer_id,
                    'order_line': [(0, 0, {
                        'product_id': product_id,
                        'product_uom_qty': quantity,
                    })]
                })
                sale_order.action_confirm()
                _logger.info(f"Purchase order {purchase_order.name} and sale order {sale_order.name} created for product {product.name}")
                return {'status': 'success', 'sale_order_id': sale_order.id, 'message': 'Purchase and sale order created successfully'}

        except Exception as e:
            _logger.error(f"Error creating order: {str(e)}")
            return {'status': 'error', 'message': str(e)}
