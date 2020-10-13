from odoo import fields, models

import logging
_logger = logging.getLogger(__name__)


class ProductWatchProducts(models.Model):
    _name = "product.watch_products"
    _inherit = "mail.thread"
    _description = "watch products"
    _order = 'name'

    name = fields.Char(
        string='Name',
        required=True,
    )
    team_id = fields.Many2one(
        'crm_team',
        string='Team',
    )

    report_id = fields.Many2one(
        'ir.actions.report',
        string='Report',
        required=True,
    )

    active = fields.Boolean(
        string='Active',
        default=True,
    )
    last_print = fields.Datetime(
        string='Last print',
        default=fields.Datetime.now()
    )
    product_ids = fields.Many2many(
        'product.template',
        string='Product',
    )

    def watch_products_all_label(self):
        self.ensure_one()

        self.last_print = fields.Datetime.now()
        if len(self.product_ids):
            self.message_post(
                body='Se genero un pdf con todos los articulos de la lista y se actualizo la fecha de impresion')
            return self.report_id.report_action(self.product_ids)

    def watch_products_label(self):
        # product_watch_products_obj = self.pool.get('product.watch.products')
        self.ensure_one()
        product_ids = self.env['product.template']
        changes = []

        for item in self.product_ids:
            # price_history_ids=price_history_obj.search(cr,uid,[('datetime','>=',cur_obj.last_print),('product_template_id','=',item.product_tmpl_id.id)])
            # obtengo el ultimo cambio anterior a la impresion
            price_history_id = self.env['product.sale.price.history'].search([
                ('datetime', '<=', self.last_print),
                ('product_tmpl_id', '=', item.id)],
                order='datetime desc , id  desc', limit=1)
            if len(price_history_id):
                # no valido cambios de decimales
                if int(price_history_id.list_price) != int(item.list_price):
                    changes.append('%s anterior %s actualizado a %s' % (
                        item.name, price_history_id.list_price, item.list_price))
                    product_ids += item

        if len(product_ids):

            self.last_print = fields.Datetime.now()
            self.message_post(
                body='Se genero un pdf con %s y se actualizo la fecha de impresion' % '|'.join(changes))
            return self.report_id.report_action(product_ids)
        else:
            self.message_post(body='Sin nada que imprimir')