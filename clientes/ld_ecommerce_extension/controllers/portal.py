# -*- coding: utf-8 -*-

import json

from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
from odoo.http import request
from odoo import http, _
from odoo.addons.web.controllers.main import ReportController
from odoo.osv.expression import OR
from odoo.addons.website_sale.controllers.main import WebsiteSale

class CustomerPortal(CustomerPortal):

    # @http.route(['/shop/payment2'], type='http', auth="public", website=True, sitemap=False)
    # def payment2(self, **post):
    #     order = request.website.sale_get_order()
    #     order.send_to_sap_web()
    #     return request.redirect("/shop/payment")

    def _prepare_home_portal_values(self):
        values = super(CustomerPortal, self)._prepare_home_portal_values()
        partner = request.env.user.partner_id

        SaleOrder = request.env['sale.order']
        SaleBlanketOrder = request.env['sale.blanket.order']
        orders_vig_count = SaleOrder.search_count([
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('sap_code', '!=', False),('split_state', 'in', ('block', 'approve'))
        ])
        orders_hist_count = SaleOrder.search_count([
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('sap_code', '!=', False),'|', ('split_state', '=', 'dispatch'), ('state', '=', 'cancel')
        ])
        orders_orig_count = SaleOrder.search_count([
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('sap_code', '=', False),('state', 'in', ('draft', 'sale', 'sent_failed', 'sent_to_sap', 'sent'))
        ])

        orders_vig_count_azu = SaleBlanketOrder.search_count([
            ('partner_id', '=', partner.commercial_partner_id.id),
            ('sap_code', '!=', False),('split_state', 'in', ('block', 'approve'))
        ])
        orders_hist_count_azu = SaleBlanketOrder.search_count([
            ('partner_id', '=', partner.commercial_partner_id.id),
            ('sap_code', '!=', False),'|', ('split_state', '=', 'dispatch'), ('state', '=', 'cancel')
        ])
        orders_orig_count_azu = SaleOrder.search_count([
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('sap_code', '=', False),('state', 'in', ('draft', 'sale', 'sent_failed', 'sent_to_sap', 'sent'))
        ])

        sap_code = request.env['sap.vbak.vkorg'].sudo().search([('company_id', '=', request.env.company.id)],limit=1).code
        #print (request.env.company.id)
        values.update({
            'orders_vig_count': orders_vig_count,
            'orders_hist_count': orders_hist_count,
            'orders_orig_count': orders_orig_count,
            'orders_vig_count_azu': orders_vig_count_azu,
            'orders_hist_count_azu': orders_hist_count_azu,
            'orders_orig_count_azu': orders_orig_count_azu,
            'sap_code': sap_code,
        })
        print (values)
        return values

    @http.route(['/my/orders_vig', '/my/orders_vig/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_orders_vig(self, page=1, date_begin=None, date_end=None, search=None, search_in='content', sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        SaleOrder = request.env['sale.order']

        domain = [
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('sap_code', '!=', False), ('split_state', 'in', ('block', 'approve'))
        ]

        searchbar_sortings = {
            'date': {'label': _('Order Date'), 'order': 'date_order desc'},
            'name': {'label': _('Reference'), 'order': 'name'},
            'stage': {'label': _('Stage'), 'order': 'state'},
        }

        searchbar_inputs = {
            'content': {'input': 'content', 'label': _('Buscar en Referencia de Cliente')},
            'name': {'input': 'name', 'label': _('Search in Name')},
        }

        # default sortby order
        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['order']

        archive_groups = self._get_archive_groups('sale.order', domain) if values.get('my_details') else []
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # search
        if search and search_in:
            search_domain = []
            if search_in == 'content':
                search_domain = OR([search_domain, [('client_order_ref', 'ilike', search)]])
            if search_in == 'name':
                search_domain = OR([search_domain, [('name', 'ilike', search)]])
            domain += search_domain

        # search
        if search and search_in:
            search_domain = []
            if search_in == 'content':
                search_domain = OR([search_domain, [('client_order_ref', 'ilike', search)]])
            if search_in == 'name':
                search_domain = OR([search_domain, [('name', 'ilike', search)]])
            domain += search_domain

        # count for pager
        order_count = SaleOrder.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/orders_vig",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=order_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        orders = SaleOrder.search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_orders_history'] = orders.ids[:100]

        values.update({
            'date': date_begin,
            'quotations': orders.sudo(),
            'page_name': 'order',
            'pager': pager,
            'archive_groups': archive_groups,
            'default_url': '/my/orders',
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("ld_ecommerce_extension.portal_my_quotations2", values)

    @http.route(['/my/orders_hist', '/my/orders_hist/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_orders_hist(self, page=1, date_begin=None, date_end=None, search=None, search_in='content', sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        SaleOrder = request.env['sale.order']

        domain = [
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('sap_code', '!=', False),'|', ('split_state', '=', 'dispatch'), ('state', '=', 'cancel')
        ]

        searchbar_sortings = {
            'date': {'label': _('Order Date'), 'order': 'date_order desc'},
            'name': {'label': _('Reference'), 'order': 'name'},
            'stage': {'label': _('Stage'), 'order': 'state'},
        }

        searchbar_inputs = {
            'content': {'input': 'content', 'label': _('Buscar en Referencia de Cliente')},
            'name': {'input': 'name', 'label': _('Search in Name')},
        }

        # default sortby order
        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['order']

        archive_groups = self._get_archive_groups('sale.order', domain) if values.get('my_details') else []
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # search
        if search and search_in:
            search_domain = []
            if search_in == 'content':
                search_domain = OR([search_domain, [('client_order_ref', 'ilike', search)]])
            if search_in == 'name':
                search_domain = OR([search_domain, [('name', 'ilike', search)]])
            domain += search_domain

        # count for pager
        order_count = SaleOrder.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/orders_hist",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=order_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        orders = SaleOrder.search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])
        print (orders)
        request.session['my_orders_history'] = orders.ids[:100]

        values.update({
            'date': date_begin,
            'quotations': orders.sudo(),
            'page_name': 'order',
            'pager': pager,
            'archive_groups': archive_groups,
            'default_url': '/my/orders',
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("ld_ecommerce_extension.portal_my_quotations2", values)

    @http.route(['/my/orders_orig', '/my/orders_orig/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_orders_orig(self, page=1, date_begin=None, date_end=None, search=None, search_in='content', sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        SaleOrder = request.env['sale.order']

        domain = [
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('sap_code', '=', False),('state', 'in', ('draft', 'sale', 'sent_failed', 'sent_to_sap', 'sent'))
        ]

        searchbar_sortings = {
            'date': {'label': _('Order Date'), 'order': 'date_order desc'},
            'name': {'label': _('Reference'), 'order': 'name'},
            'stage': {'label': _('Stage'), 'order': 'state'},
        }

        searchbar_inputs = {
            'content': {'input': 'content', 'label': _('Buscar en Referencia de Cliente')},
            'name': {'input': 'name', 'label': _('Search in Name')},
        }

        # default sortby order
        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['order']

        archive_groups = self._get_archive_groups('sale.order', domain) if values.get('my_details') else []
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # search
        if search and search_in:
            search_domain = []
            if search_in == 'content':
                search_domain = OR([search_domain, [('client_order_ref', 'ilike', search)]])
            if search_in == 'name':
                search_domain = OR([search_domain, [('name', 'ilike', search)]])
            domain += search_domain

        # count for pager
        order_count = SaleOrder.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/orders_orig",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=order_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        orders = SaleOrder.search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])
        print (orders)
        request.session['my_orders_history'] = orders.ids[:100]

        values.update({
            'date': date_begin,
            'quotations': orders.sudo(),
            'page_name': 'order',
            'pager': pager,
            'archive_groups': archive_groups,
            'default_url': '/my/orders',
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("ld_ecommerce_extension.portal_my_quotations3", values)


    @http.route(['/my/orders_vig_azu', '/my/orders_vig_azu/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_orders_vig_azu(self, page=1, date_begin=None, date_end=None, search=None, search_in='content', sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        SaleOrder = request.env['sale.blanket.order']

        domain = [
            ('partner_id', '=', partner.commercial_partner_id.id),
            ('sap_code', '!=', False), ('split_state', 'in', ('block', 'approve'))
        ]

        searchbar_sortings = {
            'date': {'label': _('Order Date'), 'order': 'date_order desc'},
            'name': {'label': _('Reference'), 'order': 'name'},
            'stage': {'label': _('Stage'), 'order': 'state'},
        }

        searchbar_inputs = {
            'content': {'input': 'content', 'label': _('Buscar en Referencia de Cliente')},
            'name': {'input': 'name', 'label': _('Search in Name')},
        }

        # default sortby order
        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['order']

        archive_groups = self._get_archive_groups('sale.blanket.order', domain) if values.get('my_details') else []
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # search
        if search and search_in:
            search_domain = []
            if search_in == 'content':
                search_domain = OR([search_domain, [('client_order_ref', 'ilike', search)]])
            if search_in == 'name':
                search_domain = OR([search_domain, [('name', 'ilike', search)]])
            domain += search_domain

        # count for pager
        order_count = SaleOrder.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/orders_vig_azu",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=order_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        orders = SaleOrder.search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_orders_history'] = orders.ids[:100]

        values.update({
            'date': date_begin,
            'quotations': orders.sudo(),
            'page_name': 'order',
            'pager': pager,
            'archive_groups': archive_groups,
            'default_url': '/my/orders',
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("ld_ecommerce_extension.portal_my_quotations2", values)

    @http.route(['/my/orders_hist_azu', '/my/orders_hist_azu/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_orders_hist_azu(self, page=1, date_begin=None, date_end=None, search=None, search_in='content', sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        SaleOrder = request.env['sale.blanket.order']

        domain = [
            # ('partner_id', '=', partner.commercial_partner_id.id),
            # ('sap_code', '!=', False),'|', ('split_state', '=', 'dispatch'), ('state', '=', 'cancel')
        ]

        searchbar_sortings = {
            'date': {'label': _('Order Date'), 'order': 'date_order desc'},
            'name': {'label': _('Reference'), 'order': 'name'},
            'stage': {'label': _('Stage'), 'order': 'state'},
        }

        searchbar_inputs = {
            'content': {'input': 'content', 'label': _('Buscar en Referencia de Cliente')},
            'name': {'input': 'name', 'label': _('Search in Name')},
        }

        # default sortby order
        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['order']

        archive_groups = self._get_archive_groups('sale.blanket.order', domain) if values.get('my_details') else []
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # search
        if search and search_in:
            search_domain = []
            if search_in == 'content':
                search_domain = OR([search_domain, [('client_order_ref', 'ilike', search)]])
            if search_in == 'name':
                search_domain = OR([search_domain, [('name', 'ilike', search)]])
            domain += search_domain

        # count for pager
        order_count = SaleOrder.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/orders_hist_azu",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=order_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        orders = SaleOrder.search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])
        print (orders)
        request.session['my_orders_history'] = orders.ids[:100]

        values.update({
            'date': date_begin,
            'quotations': orders.sudo(),
            'page_name': 'order',
            'pager': pager,
            'archive_groups': archive_groups,
            'default_url': '/my/orders',
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("ld_ecommerce_extension.portal_my_quotations2", values)

    @http.route(['/my/orders_orig_azu', '/my/orders_orig_azu/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_orders_orig_azu(self, page=1, date_begin=None, date_end=None, search=None, search_in='content', sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        SaleOrder = request.env['sale.order']

        domain = [
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('sap_code', '=', False),('state', 'in', ('draft', 'sale', 'sent_failed', 'sent_to_sap','sent'))
        ]

        searchbar_sortings = {
            'date': {'label': _('Order Date'), 'order': 'date_order desc'},
            'name': {'label': _('Reference'), 'order': 'name'},
            'stage': {'label': _('Stage'), 'order': 'state'},
        }

        searchbar_inputs = {
            'content': {'input': 'content', 'label': _('Buscar en Referencia de Cliente')},
            'name': {'input': 'name', 'label': _('Search in Name')},
        }

        # default sortby order
        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['order']

        archive_groups = self._get_archive_groups('sale.order', domain) if values.get('my_details') else []
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # search
        if search and search_in:
            search_domain = []
            if search_in == 'content':
                search_domain = OR([search_domain, [('client_order_ref', 'ilike', search)]])
            if search_in == 'name':
                search_domain = OR([search_domain, [('name', 'ilike', search)]])
            domain += search_domain

        # count for pager
        order_count = SaleOrder.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/orders_orig_azu",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=order_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        orders = SaleOrder.search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])
        print (orders)
        request.session['my_orders_history'] = orders.ids[:100]

        values.update({
            'date': date_begin,
            'quotations': orders.sudo(),
            'page_name': 'order',
            'pager': pager,
            'archive_groups': archive_groups,
            'default_url': '/my/orders',
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("ld_ecommerce_extension.portal_my_quotations3", values)

    @http.route(['/my/orders/so/<model(sale.order):order>',
                 '/my/orders/sbo/<model(sale.blanket.order):order>'], type='http', auth="user", website=True)
    def portal_order_report_html(self, order, **kw):
        ctx = request.context.copy()
        ctx['is_from_portal'] = True
        report_name = None
        if order._name == 'sale.order':
            report_name = 'portal_sale_webreport.report_portal_saleorder'
        elif order._name == 'sale.blanket.order':
            report_name = 'portal_sale_webreport.report_portal_sale_blanket_order'
        response = ReportController.report_routes(ReportController, report_name,
                                                  docids=str(order.id),
                                                  converter='html',
                                                  context=json.dumps(ctx))
        return response

    @http.route(['/my/orders/lso/<model(sale.order):order>',
                 '/my/orders/lsbo/<model(sale.blanket.order):order>'], type='http', auth="user", website=True)
    def portal_linked_order_report_html(self, order, **kw):
        ctx = request.context.copy()
        ctx['is_from_portal'] = True
        report_name = None
        if order._name == 'sale.order':
            report_name = 'portal_sale_webreport.report_portal_linked_saleorder'
        elif order._name == 'sale.blanket.order':
            report_name = 'portal_sale_webreport.rprt_prtl_lnkd_sale_bankt_ordr'
        response = ReportController.report_routes(ReportController, report_name,
                                                  docids=str(order.id),
                                                  converter='html',
                                                  context=json.dumps(ctx))
        return response
