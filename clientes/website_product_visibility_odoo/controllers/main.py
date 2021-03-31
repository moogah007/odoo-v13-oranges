import logging
from odoo import http, _, SUPERUSER_ID
from odoo.http import request
from werkzeug.exceptions import NotFound
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.website_sale.controllers.main import WebsiteSale,TableCompute
# from odoo.addons.website_sale.controllers.main.WebsiteSale import sitemap_shop
from odoo.addons.website.controllers.main import QueryURL
_logger = logging.getLogger(__name__)


class WebsiteSaleProduct(WebsiteSale):

    @http.route([
        '''/shop''',
        '''/shop/page/<int:page>''',
        '''/shop/category/<model("product.public.category"):category>''',
        '''/shop/category/<model("product.public.category"):category>/page/<int:page>'''
    ], type='http', auth="public", website=True, sitemap=WebsiteSale.sitemap_shop)
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        add_qty = int(post.get('add_qty', 1))
        Category = request.env['product.public.category']
        if category:
            category = Category.search([('id', '=', int(category))], limit=1)
            if not category or not category.can_access_from_current_website():
                raise NotFound()
        else:
            category = Category

        if ppg:
            try:
                ppg = int(ppg)
                post['ppg'] = ppg
            except ValueError:
                ppg = False
        if not ppg:
            ppg = request.env['website'].get_current_website().shop_ppg or 20

        ppr = request.env['website'].get_current_website().shop_ppr or 4

        if category:
            category = request.env['product.public.category'].with_user(SUPERUSER_ID).search([('id', '=', int(category))], limit=1)
            if not category:
                raise NotFound()

        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [[int(x) for x in v.split("-")] for v in attrib_list if v]
        attributes_ids = {v[0] for v in attrib_values}
        attrib_set = {v[1] for v in attrib_values}

        domain = self._get_search_domain(search, category, attrib_values)

        keep = QueryURL('/shop', category=category and int(category), search=search, attrib=attrib_list, order=post.get('order'))

        pricelist_context, pricelist = self._get_pricelist_context()

        request.context = dict(request.context, pricelist=pricelist.id, partner=request.env.user.partner_id)

        #######################################
        if request.env.user.partner_id:
            visible_product_ids = []
            public_prod_categ = request.env['ir.config_parameter'].with_user(SUPERUSER_ID).get_param('website_product_visibility_odoo.visible_public_prod_categ_too')
            if request.env.user.partner_id.visible_product_ids:
                visible_product_ids += request.env.user.partner_id.visible_product_ids.ids
            if request.env.user.partner_id.visible_category_ids:
                visible_product_ids += request.env['product.template'].with_user(SUPERUSER_ID).search([('categ_id', 'in', request.env.user.partner_id.visible_category_ids.ids)]).ids
            if public_prod_categ:
                public_partner = request.env.ref('base.public_partner').with_user(SUPERUSER_ID)
                if public_partner.visible_product_ids:
                    visible_product_ids += public_partner.visible_product_ids.ids
                if public_partner.visible_category_ids:
                    visible_product_ids += request.env['product.template'].with_user(SUPERUSER_ID).search([('categ_id', 'in', public_partner.visible_category_ids.ids)]).ids
            visible_product_ids = list(set(visible_product_ids))
            if (request.env.user.has_group('base.group_public') or request.env.user.has_group('base.group_portal')) and \
                    visible_product_ids:
                visible_product_ids = request.env['product.template'].sudo().browse(visible_product_ids).filtered(lambda p: p.website_published).ids
            domain += [('id', 'in', visible_product_ids)]
        #######################################

        url = "/shop"
        if search:
            post["search"] = search
        if attrib_list:
            post['attrib'] = attrib_list

        Product = request.env['product.template'].with_context(bin_size=True).with_user(SUPERUSER_ID)

        search_product = Product.search(domain)
        website_domain = request.website.website_domain()
        categs_domain = [('parent_id', '=', False)] + website_domain
        if search:
            search_categories = Category.search([('product_tmpl_ids', 'in', search_product.ids)] + website_domain).parents_and_self
            categs_domain.append(('id', 'in', search_categories.ids))
        else:
            search_categories = Category
        categs = Category.search(categs_domain)

        if category:
            url = "/shop/category/%s" % slug(category)

        product_count = len(search_product)
        pager = request.website.pager(url=url, total=product_count, page=page, step=ppg, scope=7, url_args=post)
        products = Product.search(domain, limit=ppg, offset=pager['offset'], order=self._get_search_order(post))

        ProductAttribute = request.env['product.attribute'].with_user(SUPERUSER_ID)
        if products:
            # get all products without limit
            attributes = ProductAttribute.search([('product_tmpl_ids', 'in', search_product.ids)])
        else:
            attributes = ProductAttribute.browse(attributes_ids)

        layout_mode = request.session.get('website_sale_shop_layout_mode')
        if not layout_mode:
            if request.website.viewref('website_sale.products_list_view').active:
                layout_mode = 'list'
            else:
                layout_mode = 'grid'

        values = {
            'search': search,
            'category': category,
            'attrib_values': attrib_values,
            'attrib_set': attrib_set,
            'pager': pager,
            'pricelist': pricelist,
            'add_qty': add_qty,
            'products': products,
            'search_count': product_count,  # common for all searchbox
            'bins': TableCompute().process(products, ppg, ppr),
            'ppg': ppg,
            'ppr': ppr,
            'categories': categs,
            'attributes': attributes,
            'keep': keep,
            'search_categories_ids': search_categories.ids,
            'layout_mode': layout_mode,
        }
        if category:
            values['main_object'] = category
        return request.render("website_sale.products", values)
