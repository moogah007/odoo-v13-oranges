# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class SaleOrder(models.Model):
	_inherit = 'sale.order'

	is_hide_edit_button = fields.Boolean(compute='_compute_is_hide_button', string='Is Hide Edit Button')

	def _compute_is_hide_button(self):
		for record in self:
			has_group = self.env.user.has_group('sales_team.group_sale_salesman_all_leads') \
			            or self.env.user.has_group('sales_team.group_sale_salesman') \
			            or self.env.user.has_group('sales_team.group_sale_manager')
			admin_group = self.env.user.has_group('ld_sap_integration.ld_sap_integration_admin_group')
			if (record.state in ['sent_to_sap'] or record.sap_code) and \
					has_group and \
					not admin_group and \
					not self.env.is_admin():
				record.is_hide_edit_button = True
			else:
				record.is_hide_edit_button = False


class SaleBlanketOrder(models.Model):
	_inherit = 'sale.blanket.order'

	is_hide_edit_button = fields.Boolean(compute='_compute_is_hide_button', string='Is Hide Edit Button')

	def _compute_is_hide_button(self):
		for record in self:
			admin_group = self.env.user.has_group('ld_sap_integration.ld_sap_integration_admin_group')
			if not admin_group and not self.env.is_admin():
				record.is_hide_edit_button = True
			else:
				record.is_hide_edit_button = False
