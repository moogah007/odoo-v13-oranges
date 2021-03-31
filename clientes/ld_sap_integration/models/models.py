# -*- coding: utf-8 -*-
from odoo import http, models, fields, api, _
from datetime import datetime, timedelta
import calendar
from odoo.exceptions import RedirectWarning, UserError,ValidationError
import requests, json
import base64
from odoo.tools.safe_eval import safe_eval

import logging
_logger = logging.getLogger(__name__)

class SapKna1(models.Model):
    _name = 'sap.kna1'
    _description = 'sap.kna1'

    KUNNR = fields.Char(size=10,string="KUNNR",index=True,translate=True)
    BRSCH = fields.Char(size=4,string="BRSCH",translate=True)
    LAND1 = fields.Char(size=3,string="LAND1",translate=True)
    NAME1 = fields.Char(size=35,string="NAME1",translate=True)
    ORT01 = fields.Char(size=35,string="ORT01",translate=True)
    PSTLZ = fields.Char(size=10,string="PSTLZ",translate=True)
    REGIO = fields.Char(size=3,string="REGIO",translate=True)
    STCD1 = fields.Char(size=16,string="STCD1",translate=True)
    STRAS = fields.Char(size=35,string="STRAS",translate=True)
    TELF1 = fields.Char(size=16,string="TELF1",translate=True)
    TELF2 = fields.Char(size=16,string="TELF2",translate=True)
    STCDT = fields.Char(size=2,string="STCDT",translate=True)
    sap_knvv_ids = fields.One2many('sap.knvv','sap_kna1_id',string="Sales Area",index=True,ondelete='cascade',translate=True)
    sap_knb1_ids = fields.One2many('sap.knb1','sap_kna1_id',string="Society",index=True,ondelete='cascade',translate=True)
    AUFSD = fields.Char(size=2,string="AUFSD",translate=True)
    KURST = fields.Char(size=2,string="KURST",translate=True)
    process_date = fields.Datetime(string="Process Date",translate=True,index=True)
    cust2partnerf = fields.Boolean(string="processed",index=True,translate=True)

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, rec.KUNNR))
        return result

    def cust2partner(self):
        customers = self.env['sap.kna1'].search([('cust2partnerf', '=', False)],limit=1000)
        #customers.write({'cust2partnerf': True, 'process_date': datetime.now()})
        for customer in customers:
            values = dict()
            country = self.env['res.country'].search([('code', '=', customer.LAND1)])
            state = self.env['res.country.state'].search([
                ('sap_code', '=', customer.KUNNR),
            ])
            if not customer.STCD1:
                self.env['sap.sinc.errors'].create({
                    'model_name': 'sap.kna1',
                    'id_model': customer.id,
                    'error_str': "campo STCD1 No Definido, id: " + str(customer.id),
                    'date_mark': datetime.now(),
                })
            else:
                orglist = list()
                for sales_area in customer.sap_knvv_ids:
                    if sales_area.VKORG and (sales_area.VKORG + sales_area.SPART) not in orglist:
                        print (customer.id)
                        print(sales_area.id)
                        parent = self.env['res.partner']
                        orglist.append(sales_area.VKORG + sales_area.SPART)
                        comp = self.env['sap.vbak.vkorg'].search([('code', '=', sales_area.VKORG)])

                        parent = self.env['res.partner'].search([
                            ('sap_code', '=', customer.KUNNR),
                            ('type', '=', 'contact'),
                        ])
                        self.env['res.partner'].search([
                            ('parent_id', '=', parent.id),
                            ('type', '=', 'delivery'),
                        ]).write({'active': False})

                        if not comp.company_id:
                            self.env['sap.sinc.errors'].create({
                                'model_name': 'sap.vbak.vkorg',
                                'id_model': comp.id,
                                'error_str': "campo company_id No Definido, id: " + str(comp.id),
                                'date_mark': datetime.now(),
                            })
                        else:
                            attribs = customer.sap_knvv_ids.filtered(lambda a: a.VKORG == sales_area.VKORG)
                            pcateg2 = self.env['product.category']
                            for attib in attribs:
                                pcateg2 |= self.env['sap.vbak.spart'].search([('code', '=', attib.SPART)]).category_id

                            user = self.env['res.users']
                            for interlocutor in sales_area.sap_knvp_ids:
                                if interlocutor.PARVW == 'VE':
                                    user = self.env['res.users'].search([('sap_code', '=', interlocutor.KUNN2)],limit=1)

                            vals = dict()
                            vals.update({
                                'vat': customer.STCD1,
                                'name': customer.NAME1,
                                'company_type': 'company',
                                'street': customer.STRAS,
                                'phone': customer.TELF1,
                                'country_id': country.id,
                                'type': 'contact',
                                'is_company': True,
                                'sap_code': customer.KUNNR,
                                'zip': customer.PSTLZ,
                                'city': customer.ORT01,
                                'email': False,
                                'state_id': state.id,
                                'mobile': customer.TELF2,
                                'industry_id': self.env['sap.brsch'].search([('code', '=', customer.BRSCH)]).id,
                                # 'l10n_latam_identification_type_id': self.env.ref('l10n_ar.it_cuit'),
                                'customer_rank': '1',
                                'active': True,
                                'lang': 'es_AR',
                            })
                            vals.update({'company_id': comp.company_id.id})
                            vals.update({'visible_category_ids': [(6, 0, list(pcateg2._ids))]})

                            vals.update({'user_id': user.id})

                            parent = self.env['res.partner'].search([
                                ('sap_code', '=', customer.KUNNR),
                                ('type', '=', 'contact'),
                                ('company_id', '=', comp.company_id.id)
                            ])
                            if not parent:
                                parent = self.env['res.partner'].create(vals)
                                parent.message_follower_ids.unlink()
                            else:
                                vals.update({'message_follower_ids': False})
                                parent.message_follower_ids.unlink()
                                parent.write(vals)

                            vals.update({'message_follower_ids': False})

                            #self.env['res.partner'].search([
                            #    ('company_id', '=', comp.company_id.id),
                            #    ('parent_id', '=', parent.id),
                            #    ('type', '=', 'delivery'),
                            #]).write({'active': False})

                            wefoundf = False
                            for interlocutor2 in sales_area.sap_knvp_ids:
                                print ("-----------------")
                                print (interlocutor2.id)
                                print (interlocutor2.PARVW)
                                if interlocutor2.PARVW == 'WE':
                                    wefoundf = True
                                    comp = self.env['sap.vbak.vkorg'].search([('code', '=', sales_area.VKORG)])

                                    del_add_kna1 = self.env['sap.kna1'].search([('KUNNR', '=', interlocutor2.KUNN2)],limit=1)
                                    print (del_add_kna1)
                                    vat = ""
                                    if del_add_kna1.STCD1:
                                        vat  = "AR" + del_add_kna1.STCD1
                                    if del_add_kna1:
                                        vals2 = dict()
                                        vals2 = {
                                            'company_type': 'person',
                                            'type': 'delivery',
                                            'lang': 'es_AR',
                                            'country_id': self.env['res.country'].search([('code', '=', 'AR')]).id,
                                            'parent_id': parent.id,
                                            'is_company': True,
                                            'vat': vat,
                                            'name': del_add_kna1.NAME1,
                                            'street': del_add_kna1.STRAS,
                                            'phone': del_add_kna1.TELF1,
                                            'sap_code': del_add_kna1.KUNNR,
                                            'zip': del_add_kna1.PSTLZ,
                                            'city': del_add_kna1.ORT01,
                                            'email': False,
                                            'state_id': state.id,
                                            'mobile': del_add_kna1.TELF2,
                                            'industry_id': self.env['sap.brsch'].search([('code', '=', customer.BRSCH)]).id,
                                            'company_id': comp.company_id.id,
                                            'active': True,
                                            'lang': 'es_AR',
                                        }
                                        del_partner = self.env['res.partner'].search([
                                            ('sap_code', '=', vals2['sap_code']),
                                            ('type', '=', 'delivery'),
                                            ('company_id', '=', comp.company_id.id),
                                        ])
                                        print (del_partner)
                                        if not del_partner:
                                            del_partner = self.env['res.partner'].create(vals2)
                                            print (del_partner)
                                            del_partner.message_follower_ids.unlink()
                                            vals2.update({'message_follower_ids': False})
                                        else:
                                            del_partner.message_follower_ids.unlink()
                                            del_partner.write(vals2)
                                        vals2.update({'message_follower_ids': False})

                                        customer.write({'cust2partnerf': True, 'process_date': datetime.now()})
                                    else:
                                        self.env['sap.sinc.errors'].create({
                                            'model_name': 'sap.knvp',
                                            'id_model': interlocutor2.id,
                                            'error_str': "ninguna direccion de entrega encontrada para: " + interlocutor2.KUNN2 + ", " + str(interlocutor2.id),
                                            'date_mark': datetime.now(),
                                        })
                            if not wefoundf:
                                self.env['sap.sinc.errors'].create({
                                    'model_name': 'sap.kna1',
                                    'id_model': sales_area.id,
                                    'error_str': "campo PARVW (WE No Definido), id: " + str(sales_area.id),
                                    'date_mark': datetime.now(),
                                })
                    else:
                        if not sales_area.VKORG:
                            self.env['sap.sinc.errors'].create({
                                'model_name': 'sap.kna1',
                                'id_model': customer.id,
                                'error_str': "campo VKORG No Definido, id: " + str(customer.id),
                                'date_mark': datetime.now(),
                            })
            #self.env.cr.commit()


class SapKnvv(models.Model):
    _name = 'sap.knvv'
    _description = 'sap.knvv Sales Area'

    sap_kna1_id = fields.Many2one('sap.kna1',index=True,ondelete='cascade',translate=True)
    KUNNR = fields.Char(size=10,string="KUNNR",index=True,translate=True)
    VKORG = fields.Char(size=4,string="VKORG",translate=True)
    VTWEG = fields.Char(size=2,string="VTWEG",translate=True)
    SPART = fields.Char(size=2,string="SPART",translate=True)
    WAERS = fields.Char(size=5,string="WAERS",translate=True)
    ZTERM = fields.Char(size=4,string="ZTERM",translate=True)
    sap_knvp_ids = fields.One2many('sap.knvp','sap_knvv_id',string="Interlocutor Functions",index=True,ondelete='cascade',translate=True)
    KURST = fields.Char(size=2,string="KURST",translate=True)
    process_date = fields.Datetime(string="Process Date",translate=True)


    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, rec.KUNNR))
        return result

class SapKnvp(models.Model):
    _name = 'sap.knvp'
    _description = 'sap.knvp'

    sap_knvv_id = fields.Many2one('sap.knvv',index=True,ondelete='cascade',translate=True)
    KUNNR = fields.Char(size=10,string="KUNNR",index=True,translate=True)
    VKORG = fields.Char(size=4,string="VKORG",translate=True)
    VTWEG = fields.Char(size=2,string="VTWEG",translate=True)
    SPART = fields.Char(size=2,string="SPART",translate=True)
    PARVW = fields.Char(size=2,string="PARVW",translate=True)
    KUNN2 = fields.Char(size=10,string="KUNN2",translate=True)
    partner_id = fields.Many2one('res.partner',string="Parrtner",translate=True)
    process_date = fields.Datetime(string="Process Date",translate=True)


    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, rec.KUNNR))
        return result

class SapKnb1(models.Model):
    _name = 'sap.knb1'
    _description = 'sap.knb1 Society'

    sap_kna1_id = fields.Many2one('sap.kna1',index=True,ondelete='cascade',translate=True)
    KUNNR = fields.Char(size=10,string="KUNNR",index=True,translate=True)
    BUKRS = fields.Char(size=4,string="BUKRS",translate=True)
    BUSAB = fields.Char(size=2,string="BUSAB",translate=True)
    INTAD = fields.Char(size=130,string="INTAD",translate=True)

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, rec.KUNNR))
        return result

class SapSales(models.Model):
    _name = 'sap.sales'
    _description = 'sap.sales'

    VBAK_AUART = fields.Char(size=6, string="VBAK_AUART",translate=True)
    VBAK_VBELN = fields.Char(size=10, string="VBAK_VBELN",translate=True)
    VBAK_ZTERM = fields.Char(size=6, string="VBAK_ZTERM",translate=True)
    VBAK_ANGDT = fields.Char(size=10, string="VBAK_ANGDT",translate=True)
    VBAK_BNDDT = fields.Char(size=10, string="VBAK_BNDDT",translate=True)
    VBAK_VKORG = fields.Char(size=4, strng="VBAK_VKORG",translate=True)
    VBAK_VTWEG = fields.Char(size=2, string="VBAK_VTWEG",translate=True)
    VBAK_SPART = fields.Char(size=2, string="VBAK_SPART",translate=True)
    VBUK_CMPSB = fields.Char(size=50, string="VBUK_CMPSB",translate=True)
    VBUK_CMPSF = fields.Char(size=50, string="VBUK_CMPSF",translate=True)
    VBUK_CMPSG = fields.Char(size=50, string="VBUK_CMPSG",translate=True)
    VBUK_CMGST = fields.Char(size=50, string="VBUK_CMGST",translate=True)
    VBAK_UPDKZ = fields.Char(size=1, string="VBAK_UPDKZ",translate=True)
    sap_sales_interlocutor_ids = fields.One2many('sap.sales.interlocutor','sap_sales_id',index=True,ondelete='cascade',translate=True)
    sap_sales_position_ids = fields.One2many('sap.sales.position','sap_sales_id',index=True,ondelete='cascade',translate=True)
    JEST_STAT = fields.Char(size=50,string="Price Block",translate=True)
    RETURN = fields.Char(size=30,string="RETURN",translate=True)
    BLOCKED = fields.Selection([('S','Si'),('N','No')],string="Blocked",translate=True)
    sincedf = fields.Boolean(string="Sincronized")
    VBKD_BSTKD_OC = fields.Char(size=20, string="VBKD_BSTKD_OC",translate=True)

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, rec.VBAK_VKORG))
        return result

    def cron_create_new_sales(self):
        domain = [('sincedf', '=', False)]
        sap_sales = self.env['sap.sales'].search(domain)
        print (sap_sales)
        for sale in sap_sales:
            doset = True
            print ("sale ID ", sale.id)
            if not sale.VBAK_UPDKZ:
                self.env['sap.sinc.errors'].create({
                    'model_name': 'sap.sales',
                    'id_model': sale.id,
                    'error_str': "campo VBAK_UPDKZ No Definido debe tener U,I,D id: " + str(sale.id),
                    'date_mark': datetime.now(),
                })
                doset = False
            vals = dict()
            company = self.env['sap.vbak.vkorg'].search([('code', '=', sale.VBAK_VKORG)]).company_id
            print (company)
            auart = self.env['sap.vbak.auart'].search([('code', '=', sale.VBAK_AUART)])
            if not auart.type:
                self.env['sap.sinc.errors'].create({
                    'model_name': 'sap.sales',
                    'id_model': sale.id,
                    'error_str': "SAP SALES: auart sin TYPE, id: " + str(auart.id),
                    'date_mark': datetime.now(),
                })
                doset = False

            vtweg =  self.env['sap.vbak.vtweg'].search([('code', '=', sale.VBAK_VTWEG)])
            spart =  self.env['sap.vbak.spart'].search([('code', '=', sale.VBAK_SPART)])
            interlocutorp = self.env['sap.sales.interlocutor'].search([
                ('sap_sales_id', '=', sale.id),
                ('VBPA_PARVW', '=', 'SO')
            ])
            if len(interlocutorp)>1:
                self.env['sap.sinc.errors'].create({
                    'model_name': 'sap.sales',
                    'id_model': sale.id,
                    'error_str': "SAP SALES: mas de 1 interlocutor encontrado, id: " + str(sale.id),
                    'date_mark': datetime.now(),
                })
                doset = False
                #_logger.error("SAP SALES: mas de 1 interlocutor encontrado, id: " + sale.id)
            print (interlocutorp)
            partnerp = self.env['res.partner'].search([
                ('sap_code', '=', interlocutorp.VBPA_KUNNR),
                ('company_id', '=', company.id),
                ('type', '=', 'contact')
            ])
            if not partnerp:
                self.env['sap.sinc.errors'].create({
                    'model_name': 'sap.sales',
                    'id_model': sale.id,
                    'error_str': "SAP SALES: partner NO encontrado, id: " + str(sale.id),
                    'date_mark': datetime.now(),
                })

            if len(partnerp)>1:
                self.env['sap.sinc.errors'].create({
                    'model_name': 'sap.sales',
                    'id_model': sale.id,
                    'error_str': "SAP SALES: mas de 1 partner encontrado, id: " + str(sale.id),
                    'date_mark': datetime.now(),
                })
                doset = False
                #_logger.error("SAP SALES: mas de 1 partner encontrado, id: " + str(sale.id))

            print (partnerp)
            interlocutori = self.env['sap.sales.interlocutor'].search([
                ('sap_sales_id', '=', sale.id),
                ('VBPA_PARVW', '=', 'RF')
            ])
            if len(interlocutori)>1:
                self.env['sap.sinc.errors'].create({
                    'model_name': 'sap.sales',
                    'id_model': sale.id,
                    'error_str': "SAP SALES: mas de 1 interlocutor encontrado, id: " + str(sale.id),
                    'date_mark': datetime.now(),
                })
                doset = False
                #_logger.error("SAP SALES: mas de 1 interlocutor encontrado, id: " + sale.id)

            partneri = self.env['res.partner'].search([
                ('sap_code', '=', interlocutori.VBPA_KUNNR),
                ('company_id', '=', company.id),
                ('type', '=', 'contact')
            ])
            if not partneri:
                self.env['sap.sinc.errors'].create({
                    'model_name': 'sap.sales',
                    'id_model': sale.id,
                    'error_str': "SAP SALES: partner Invoice NO encontrado, id: " + str(sale.id),
                    'date_mark': datetime.now(),
                })
                doset = False
            if len(partneri)>1:
                self.env['sap.sinc.errors'].create({
                    'model_name': 'sap.sales',
                    'id_model': sale.id,
                    'error_str': "SAP SALES: mas de 1 partner encontrado, id: " + str(sale.id),
                    'date_mark': datetime.now(),
                })
                doset = False
                #_logger.error("SAP SALES: mas de 1 partner encontrado, id: " + sale.id)

            interlocutors = self.env['sap.sales.interlocutor'].search([
                ('sap_sales_id', '=', sale.id),
                ('VBPA_PARVW', '=', 'EM')
            ])
            if len(interlocutors)>1:
                self.env['sap.sinc.errors'].create({
                    'model_name': 'sap.sales',
                    'id_model': sale.id,
                    'error_str': "SAP SALES: mas de 1 interlocutor encontrado, id: " + str(sale.id),
                    'date_mark': datetime.now(),
                })
                doset = False
                #_logger.error("SAP SALES: mas de 1 interlocutor encontrado, id: " + sale.id)

            partners = self.env['res.partner'].search([
                ('sap_code', '=', interlocutors.VBPA_KUNNR),
                ('company_id', '=', company.id),
                ('type', '=', 'delivery')
            ])
            werk = self.env['sap.werk']
            if not partners:
                werk = self.env['sap.werk'].search([('code', '=', interlocutors.VBPA_KUNNR)])
            if len(partners)>1:
                self.env['sap.sinc.errors'].create({
                    'model_name': 'sap.sales',
                    'id_model': sale.id,
                    'error_str': "SAP SALES: mas de 1 partner encontrado, id: " + str(sale.id),
                    'date_mark': datetime.now(),
                })
                doset = False
                #_logger.error("SAP SALES: mas de 1 partner encontrado, id: " + sale.id)
            if not partners:
                partners = partnerp
            # if not partners:
            #     self.env['sap.sinc.errors'].create({
            #         'model_name': 'sap.sales',
            #         'id_model': sale.id,
            #         'error_str': "SAP SALES: partner Shipping NO encontrado, id: " + str(sale.id),
            #         'date_mark': datetime.now(),
            #     })
            #     sale.write({'sincedf': False})

            split_state = 'approve'
            if sale.BLOCKED == 'S':
                split_state = 'block'
            if partnerp and partners and partneri and auart.type:
                new_date = False
                if sale.VBAK_BNDDT != '00.00.0000' and sale.VBAK_BNDDT:
                    the_date = sale.VBAK_BNDDT.replace('.', '')
                    new_date = the_date[4:8] + '-' + the_date[2:4] + '-' + the_date[0:2]

                if auart.type == 'sale':
                    ord = self.env['sale.order']
                else:
                    ord = self.env['sale.blanket.order']
                if sale.sap_sales_position_ids:
                    if auart.type == 'sale':
                        ord = self.env['sale.order'].search([('name', '=', sale.sap_sales_position_ids[0].VBKD_BSTKD)])
                    else:
                        ord = self.env['sale.blanket.order'].search([('name', '=', sale.sap_sales_position_ids[0].VBKD_BSTKD)])

                query = """SELECT id from stock_warehouse where company_id = %d LIMIT %d""" % (company.id,1)
                print (query)
                self.env.cr.execute(query)
                wh = self.env.cr.fetchall()


                #wh = self.env['stock.warehouse'].search([('company_id', '=', company.id)],limit=1)
                print (wh)
                if not wh:
                    self.env['sap.sinc.errors'].create({
                        'model_name': 'sap.sales',
                        'id_model': sale.id,
                        'error_str': "SAP SALES: no hay warehouse definido para la empresa: " + str(company.id),
                        'date_mark': datetime.now(),
                    })
                    doset = False
                else:
                    print ("seteando True snced")
                    sale.write({'sincedf': True})
                    vals.update({
                        'sap_code': sale.VBAK_VBELN,
                        'company_id': company.id,
                        'partner_id': partnerp.id,
                        'partner_invoice_id': partneri.id,
                        'partner_shipping_id': partners.id,
                        'split_state': split_state,
                        'sap_document_type_id': auart.id,
                        'vbak_vkorg_id': company.id,
                        'vbak_vtweg_id': vtweg.id,
                        'vbak_spart_id': spart.id,
                        'validity_date': new_date,
                        'payment_term_id': self.env['account.payment.term'].search([('sap_code', '=', sale.VBAK_ZTERM)],limit=1).id,
                        'pricelist_id': 1,
                        'VBKD_BSTKD': ord.id,
                        'vbap_werks': werk.id,
                        'client_order_ref': sale.VBKD_BSTKD_OC,
                    })
                    if werk:
                        vals.update({'pickup': True})
                    if not sale.VBAK_UPDKZ:
                        pass
                    else:
                        print (sale.VBAK_UPDKZ)
                        try:
                            if sale.VBAK_UPDKZ == 'I':
                                print (vals)
                                print (auart.type)
                                if auart.type == 'sale':
                                    vals.update({'warehouse_id': wh[0][0]})
                                    ord = self.env['sale.order'].sudo().create(vals)
                                else:
                                    vals.update({'date_order': datetime.now()})
                                    ord = self.env['sale.blanket.order'].sudo().create(vals)
                                print (ord)
                            if sale.VBAK_UPDKZ == 'U':
                                if auart.type == 'sale':
                                    ord = self.env['sale.order'].search([('sap_code', '=', sale.VBAK_VBELN)],limit=1)
                                    ord.write(vals)
                                else:
                                    ord = self.env['sale.blanket.order'].search([('sap_code', '=', sale.VBAK_VBELN)],limit=1)
                                    ord.write(vals)
                            if sale.VBAK_UPDKZ == 'D':
                                ord = self.env['sale.order']
                                if auart.type == 'sale':
                                    self.env['sale.order'].search([('sap_code', '=', vals['sap_code'])]).sudo().unlink()
                                else:
                                    self.env['sale.order'].search([('sap_code', '=', vals['sap_code'])]).sudo().unlink()
                        except Exception as e:
                            self.env['sap.sinc.errors'].create({
                                'model_name': 'sap.material',
                                'id_model': sale.id,
                                'error_str': "Error: " + str(e),
                                'date_mark': datetime.now(),
                            })
                            doset = False

                    print (ord)
                    if sale.VBAK_UPDKZ and ord:
                        for line in sale.sap_sales_position_ids:
                            line_vals = dict()
                            prod = self.env['product.product'].search([
                                ('sap_code', '=', line.VBAP_MATNR),
                                ('company_id', '=', company.id)
                            ],limit=1)
                            if not prod:
                                self.env['sap.sinc.errors'].create({
                                    'model_name': 'sap.sales',
                                    'id_model': sale.id,
                                    'error_str': "ERROR SAP: NO existe producto para el sap code " + str(line.VBAP_MATNR),
                                    'date_mark': datetime.now(),
                                })
                                doset = False
                            else:
                                prod_uom = self.env['uom.uom'].search([('sap_code', '=', line.VBAP_VRKME)],limit=1)
                                print (prod_uom)
                                if not prod_uom:
                                    self.env['sap.sinc.errors'].create({
                                        'model_name': 'sap.sales',
                                        'id_model': sale.id,
                                        'error_str': "ERROR SAP: el " + str(line.VBAP_VRKME) + " no tiene uom_uom",
                                        'date_mark': datetime.now(),
                                    })
                                    doset = False
                                    #_logger.error("ERROR SAP: el " + str(line.VBAP_VRKME) + " no tiene uom_uom")
                                else:
                                    line_vals.update({
                                        'sequence': line.VBAP_POSNR,
                                        'product_id': prod.id,
                                        'name': prod.name,
                                        'product_uom_qty': line.VBAP_KWMENG,
                                        'product_uom': prod_uom.id,
                                        'price_unit': line.KONV_KBETR,
                                        'KONV_WAERS': self.env['sap.waers'].search([('code', '=', line.KONV_WAERS)]).id,
                                        'vbap_werks': self.env['sap.werk'].search([('code', '=', line.VBAP_WERKS)]).id,
                                        'order_id': ord.id,
                                    })
                                    print ("grabando linea")
                                    if not line.VBAP_UPDKZ:
                                        pass
                                    else:
                                        try:
                                            if line.VBAP_UPDKZ == 'I':
                                                if auart.type == 'sale':
                                                    lineord = self.env['sale.order.line'].sudo().create(line_vals)
                                                else:
                                                    lineord = self.env['sale.blanket.order.line'].sudo().create(line_vals)
                                            if line.VBAP_UPDKZ == 'U':
                                                if auart.type == 'sale':
                                                    self.env['sale.order.line'].search([
                                                        ('sequence', '=', line_vals['sequence']),
                                                        ('order_id', '=', line_vals['order_id'])]).sudo().write(line_vals)
                                                else:
                                                    self.env['sale.blanket.order.line'].search([
                                                        ('sequence', '=', line_vals['sequence']),
                                                        ('order_id', '=', line_vals['order_id'])]).sudo().write(line_vals)
                                            if line.VBAP_UPDKZ == 'D':
                                                if auart.type == 'sale':
                                                    self.env['sale.order.line'].search([
                                                        ('sequence', '=', line_vals['sequence']),
                                                        ('order_id', '=', line_vals['order_id'])]).sudo().unlink()
                                                else:
                                                    self.env['sale.blanket.order.line'].search([
                                                        ('sequence', '=', line_vals['sequence']),
                                                        ('order_id', '=', line_vals['order_id'])]).sudo().unlink()

                                        except Exception as e:
                                            self.env['sap.sinc.errors'].create({
                                                'model_name': 'sap.material',
                                                'id_model': sale.id,
                                                'error_str': "Error: " + str(e),
                                                'date_mark': datetime.now(),
                                            })
                                            doset = False
            if doset:
                sale.sincedf = True
            print ("sale ID, sinced", sale.id, sale.sincedf)


class SapSalesInterlocutor(models.Model):
    _name = 'sap.sales.interlocutor'
    _description = 'sap.sales.interlocutor'

    VBPA_PARVW = fields.Char(size=10, string="VBPA_PARVW",translate=True)
    VBPA_KUNNR = fields.Char(size=18, string="VBPA_KUNNR",translate=True)
    sap_sales_id = fields.Many2one('sap.sales',index=True,ondelete='cascade',translate=True)

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, rec.VBPA_KUNNR))
        return result


class SapSalesPosition(models.Model):
    _name = 'sap.sales.position'
    _description = 'sap.sales.position'

    VBAP_POSNR = fields.Char(size=6, string="VBAP_POSNR",translate=True)
    VBAP_MATNR = fields.Char(size=18, string="VBAP_MATNR",translate=True)
    KONV_KBETR = fields.Char(size=30, string="KONV_KBETR",translate=True)
    KONV_WAERS = fields.Char(size=6, string="KONV_WAERS",translate=True)
    VBAP_KWMENG = fields.Char(size=30, string="VBAP_KWMENG",translate=True)
    VBAP_VRKME = fields.Char(size=6, string="VBAP_VRKME",translate=True)
    VBAP_ABGRU = fields.Char(size=10, sting="VBAP_ABGRU",translate=True)
    VBAP_WERKS = fields.Char(size=6, string="VBAP_WERKS",translate=True)
    JEST_STAT = fields.Char(size=20, string="JEST_STAT",translate=True)
    VBAP_UPDKZ = fields.Char(size=2, string="VBAP_UPDKZ",translate=True)
    VBAP_VGBEL = fields.Char(size=10, string="VBAP_VGBEL",translate=True)
    VBAP_VGPOS = fields.Char(size=8, string="VBAP_VGPOS",translate=True)
    sap_sales_id = fields.Many2one('sap.sales',index=True,ondelete='cascade',translate=True)
    VBEP_EDATU = fields.Char(size=10, string="VBEP_EDATU",translate=True)
    VBKD_BSTKD = fields.Char(size=10, string="VBKD_BSTKD",translate=True)

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, rec.VBAP_POSNR))
        return result

class SapVbakVtweg(models.Model):
    _name = 'sap.vbak.vtweg'
    _description = 'sap.vbak.vtweg'

    code = fields.Char(size=4,string="Code",translate=True)
    name = fields.Char(size=50,string="Name",translate=True)

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, rec.name[0:20]))
        return result

class SapVbakSpart(models.Model):
    _name = 'sap.vbak.spart'
    _description = 'sap.vbak.spart'

    code = fields.Char(size=4,string="Code",translate=True)
    name = fields.Char(size=50,string="Name",translate=True)
    category_id = fields.Many2one('product.category',string="Product Category",translate=True)

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, rec.name[0:20]))
        return result

class SapVbakVkorg(models.Model):
    _name = 'sap.vbak.vkorg'
    _description = 'sap.vbak.vkorg'

    code = fields.Char(size=4,string="Code",translate=True)
    name = fields.Char(size=50,string="Name",translate=True)
    company_id = fields.Many2one('res.company',string="Company",translate=True)
    direct_to_sap = fields.Boolean(string="Send to sap automatically",translate=True)
    no_attribs = fields.Boolean(string="NO WEB Attributes",translate=True)

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, rec.name[0:20]))
        return result

class SapVbakVkorg2(models.Model):
    _name = 'sap.rej.reason'
    _description = 'sap.rej.reason'

    code = fields.Char(size=4,string="Code",translate=True)
    name = fields.Char(size=50,string="Name",translate=True)

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, rec.name[0:20]))
        return result

class Kschl(models.Model):
    _name = "kschl"
    _description = 'kschl'

    name = fields.Char(size=30,string="Name",translate=True)
    discount = fields.Integer(string="Discount",translate=True)

class SapMaterial(models.Model):
    _name = 'sap.material'
    _description = 'sap.material'

    MATNR = fields.Char(size=18,string="Número de material",translate=True)
    MAKTX = fields.Char(size=40,string="Texto breve de material",translate=True)
    SPART = fields.Char(size=2,string="Sector",translate=True)
    value_ids = fields.One2many('value.line','sap_material_id',string="Codigo de atributo",translate=True)
    material_line_ids = fields.One2many('sap.material.line','sap_material_id',string="Material Lines",translate=True)
    PRDHA = fields.Char(string="Jerarquia",translate=True)
    sinced = fields.Boolean(string="sinced",index=True)

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, rec.MATNR))
        return result

    def cron_create_new_products(self):
        materials = self.env['sap.material'].search([('sinced', '=', False)])
        #print (materials)
        materials.write({'sinced': True})
        for material in materials:
            #print (material)
            pcateg2 = self.env['product.public.category']
            for attib in material.value_ids:
                pcateg = self.env['product.public.category'].search([('sap_code', '=', attib.CHARC_TXT)])
                pcateg2 |= pcateg

            for line in material.material_line_ids:
                print (line)
                print (line.VKORG)
                vkorg = self.env['sap.vbak.vkorg'].search([('code', '=', line.VKORG)])
                print (vkorg)
                print (vkorg.company_id)
                company = vkorg.company_id
                web = self.env['website'].search([('company_id', '=', company.id)],limit=1)
                save = True
                if not company:
                    save = False
                    self.env['sap.sinc.errors'].create({
                        'model_name': 'sap.material',
                        'id_model': material.id,
                        'error_str': "NO se encuentra compania en el settingg sap.vbak.vkorg ID " + str(vkorg.id),
                        'date_mark': datetime.now(),
                    })
                    #_logger.info("NO se encuentra compania en el settingg sap.vbak.vkorg ID " +
                   #              str(vkorg.id))
                uom_id = self.env['uom.uom'].search([('sap_code', '=', line.VRKME)],limit=1).id
                if not uom_id:
                    save = False
                    self.env['sap.sinc.errors'].create({
                        'model_name': 'sap.material',
                        'id_model': material.id,
                        'error_str': "NO se encuentra uom_id codigo " + line.VRKME,
                        'date_mark': datetime.now(),
                    })
                    #_logger.info("NO se encuentra uom_id codigo " + line.VRKME)
                vals = dict() #self.env['product.product'].default_get({})
                if not material.SPART:
                    save = False
                    self.env['sap.sinc.errors'].create({
                        'model_name': 'sap.material',
                        'id_model': material.id,
                        'error_str': "NO se encuentra SPART en el material",
                        'date_mark': datetime.now(),
                    })
                categ = self.env['sap.vbak.spart'].search([('code', '=', material.SPART)]).category_id.id
                if not categ:
                    save = False
                    self.env['sap.sinc.errors'].create({
                        'model_name': 'sap.material',
                        'id_model': material.id,
                        'error_str': "NO se encuentra categ en el seteo sap.vbak.spart codigo " + str(material.SPART),
                        'date_mark': datetime.now(),
                    })
                    #_logger.info("NO se encuentra categ en el seteo sap.vbak.spart codigo " + material.SPART)
                if save and line.VTWEG != '20':
                    name = str(material.MAKTX)
                    if line.TDLINE and line.TDSPRAS == 'S':
                        name = str(line.TDLINE)
                    print (name, line.TDLINE, line.TDSPRAS, material.MAKTX)
                    vals.update({
                        'sap_code': material.MATNR,
                        'name': name,
                        'display_name': name,
                        'categ_id': categ,
                        'company_id': company.id,
                        'uom_id': uom_id,
                        'uom_po_id': uom_id,
                        'dist_channel': line.VTWEG,
                        #'attribute_line_ids': temp,
                        'responsible_id': False,
                        #'public_categ_ids': [(6,0,list(pcateg2._ids))],
                        'website_id': web.id,
                        #'default_code': material.MATNR,
                    })
                    if vkorg.no_attribs == False:
                        vals.update({'public_categ_ids': [(6,0,list(pcateg2._ids))]})
                    try:
                        orig_prod = self.env['product.product'].search([
                            ('sap_code', '=', material.MATNR),
                            ('company_id', '=', company.id)
                        ])
                        if not orig_prod:
                            prod = self.env['product.product'].create(vals)
                            line.write({'product_id': prod.id})
                        else:
                            orig_prod.write(vals)
                            orig_prod.product_tmpl_id.write(vals)
                            line.write({'product_id': orig_prod.id})
                        print (orig_prod)
                    except Exception as e:
                        self.env['sap.sinc.errors'].create({
                            'model_name': 'sap.material',
                            'id_model': material.id,
                            'error_str': "Error: " +  str(e),
                            'date_mark': datetime.now(),
                        })
                        #_logger.info("Error:- %r", str(e))
        return True

class ValueLine(models.Model):
    _name = 'value.line'
    _description = 'value.line'

    sap_material_id = fields.Many2one('sap.material',translate=True)
    CHARC_TXT = fields.Char(size=30,string="Descripcion de atributo",translate=True)
    VALUE = fields.Char(size=30,string="Value",translate=True)
    VALUE_TO = fields.Text(string="Value To")

class SapMaterialline(models.Model):
    _name = 'sap.material.line'
    _description = 'sap.material.line'

    sap_material_id = fields.Many2one('sap.material',ondelete='cascade',translate=True)
    VKORG = fields.Char(size=4,string="Organizacion de ventas",translate=True)
    VRKME = fields.Char(size=3,string="Unidad de medida de venta",translate=True)
    VTWEG = fields.Char(size=2,string="Canal de distribucion",translate=True)
    product_id = fields.Many2one('product.product',string="Family Product",translate=True)
    TDLINE = fields.Char(string="TDLINE",size=50,translate=True)
    TDSPRAS = fields.Char(string="TDSPRAS",size=50,translate=True)

class SapDelivery(models.Model):
    _name = 'sap.delivery'
    _description = 'sap.delivery'

    LIKP_VBELN = fields.Char(size=10,string="LIKP_VBELN",translate=True)
    LIKP_XBLNR = fields.Char(size=20,string="LIKP_XBLNR",translate=True)
    LIKP_WADAT_IST = fields.Char(size=10,string="LIKP_WADAT_IST",translate=True)
    sap_delivery_interlocutor_ids = fields.One2many('sap.delivery.interlocutor','sap_delivery_id',string="Interlocutor",translate=True)
    sap_delivery_position_ids = fields.One2many('sap.delivery.position','sap_delivery_id',string="Position",translate=True)
    RETURN = fields.Selection([('S','Si'),('N','No')],string="Devolucion",translate=True)
    DELIVERY = fields.Selection([('S','Si'),('N','No')],string="Despachado",translate=True)
    LIKP_UPDKZ = fields.Char(size=30,string="LIKP_UPDKZ",translate=True)
    sinced = fields.Boolean(string="Sinced",index=True)

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, rec.LIKP_VBELN))
        return result

    def cron_create_deliveries(self):
        del_lines = self.env['sap.delivery.position'].search([('sinced', '=', False)])
        for del_line in del_lines:
            print (del_line)
            if del_line.LIPS_UPDKZ in ('I', 'U'):
                order = self.env['sale.order'].search([('sap_code', '=', del_line.LIPS_VGBEL)])
                print (order)
                if order:
                    order_line = self.env['sale.order.line'].search([('order_id', '=', order.id),('sequence', '=', del_line.LIPS_VGPOS)])

                    if del_line.LIPS_UPDKZ == 'U':
                        move = self.env['stock.move'].search([('sale_line_id', '=', order_line.id)])
                        oldpick = move.picking_id
                        if oldpick.state == 'done':
                            oldpick.action_cancel()
                        oldpick.unlink()

                    print (order_line)
                    if order_line:
                        partner = order.partner_shipping_id
                        print (partner)
                        pick_type = self.env['stock.picking.type'].search([('code', '=', 'outgoing')],limit=1)
                        if partner:
                            if del_line.sap_delivery_id.LIKP_WADAT_IST != '00.00.0000' and del_line.sap_delivery_id.LIKP_WADAT_IST:
                                the_date = del_line.sap_delivery_id.LIKP_WADAT_IST.replace('.', '')
                                new_date = the_date[4:8] + '-' + the_date[2:4] + '-' + the_date[0:2]
                            else:
                                new_date = fields.Date.to_string(fields.Date.today())
                            hvals = {
                                'move_type': 'direct',
                                'priority': '1',
                                'company_id': order_line.company_id.id,
                                'picking_type_id': pick_type.id,
                                'scheduled_date': new_date,
                                'sap_code': del_line.sap_delivery_id.LIKP_VBELN,
                                'official_nr': del_line.sap_delivery_id.LIKP_XBLNR,
                                'partner_id': partner.id,
                                'location_id': pick_type.default_location_src_id.id,
                                'location_dest_id': pick_type.default_location_dest_id.id,
                            }
                            pick = self.env['stock.picking'].create(hvals)
                            print (pick)
                            move = pick.move_ids_without_package.create({
                                'product_id': order_line.product_id.id,
                                'name': order_line.product_id.name,
                                'product_uom': order_line.product_id.uom_id.id,
                                'product_uom_qty': del_line.LIPS_LFIMG,
                                'location_id': pick_type.default_location_src_id.id,
                                'location_dest_id': pick_type.default_location_dest_id.id,
                                'picking_id': pick.id,
                                'sale_line_id': order_line.id,
                            })
                            if del_line.sap_delivery_id.RETURN == 'S':
                                move.write({'to_refund': True})
                            if del_line.sap_delivery_id.DELIVERY == 'S':
                                pick.action_confirm()
                                pick.action_assign()
                                pick.action_pack_operation_auto_fill()
                                pick.button_validate()



            if del_line.LIPS_UPDKZ == 'D':
                oldpicks = self.env['stock.picking'].search([('sap_code', '=', del_line.sap_delivery_id.LIKP_VBELN)])
                for oldpick in oldpicks:
                    if oldpick.state == 'done':
                        oldpick.action_cancel()
                    oldpick.unlink()


            del_line.write({'sinced': True})



class SapDeliveryInterlocutor(models.Model):
    _name = 'sap.delivery.interlocutor'
    _description = 'sap.delivery.interlocutor'

    VBPA_PARVW = fields.Char(size=2,string="VBPA_PARVW",translate=True)
    VBPA_KUNNR = fields.Char(size=18,string="VBPA_KUNNR",translate=True)
    sap_delivery_id = fields.Many2one('sap.delivery',translate=True)
    VBPA_PERNR = fields.Char(size=30,string='VBPA_PERNR',translate=True)

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, rec.VBPA_PARVW))
        return result


class SapDeliveryPosition(models.Model):
    _name = 'sap.delivery.position'
    _description = 'sap.delivery.position'

    VBKD_BSTKD = fields.Char(size=12,string="VBKD_BSTKD",translate=True)
    LIPS_POSNR = fields.Char(size=6,string="LIPS_POSNR",translate=True)
    LIPS_MATNR = fields.Char(size=18,string="LIPS_MATNR",translate=True)
    LIPS_LFIMG = fields.Char(size=10,string="LIP_LFIMG",translate=True)
    LIPS_VRKME = fields.Char(size=4,string="LIPS_VRKME",translate=True)
    LIPS_WERKS = fields.Char(size=10,string="LIPS_WERKS",translate=True)
    LIPS_VGBEL = fields.Char(size=12,string="LIPS_VGBEL",translate=True)
    LIPS_VGPOS = fields.Char(size=6,string="LIPS_VGPOS",translate=True)
    sap_delivery_id = fields.Many2one('sap.delivery',translate=True)
    LIPS_UPDKZ = fields.Char(size=30,string="LIPS_UPDKZ",translate=True)
    sinced = fields.Boolean(string="Sinced",index=True)

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, rec.VBKD_BSTKD))
        return result

class SapVbakAuart(models.Model):
    _name = 'sap.vbak.auart'
    _description = 'sap.vbak.auart'

    name = fields.Char(size=50,string="Name",translate=True)
    code = fields.Char(size=4,string="Code",translate=True)
    type = fields.Selection([('sale',_('Sale')),('contract',_('Contract'))],string="Type",translate=True)

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, rec.code))
        return result

class SapWerk(models.Model):
    _name = 'sap.werk'
    _description = 'sap.werk'

    name = fields.Char(size=50,string="Name",translate=True)
    code = fields.Char(size=4,string="Code",translate=True)

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, rec.code + "/" + rec.name))
        return result

class SapInvoice(models.Model):
    _name = 'sap.invoice'
    _description = 'sap.invoice'

    VBRK_VBELN = fields.Char(size=10,string="VBRK_VBELN",translate=True)
    VBRK_XBLNR = fields.Char(size=13,string="VBRK_XBLNR",translate=True)
    VBRK_FKDAT = fields.Char(size=10,string="VBRK_FKDAT",translate=True)
    RETURN = fields.Selection([('S', 'Si'),('N','No')],string="Devolucion",translate=True)
    sap_invoice_interlocutor_ids = fields.One2many('sap.invoice.interlocutor','sap_invoice_id',string="Interlocutors",translate=True)
    sap_invoice_position_ids = fields.One2many('sap.invoice.position','sap_invoice_id',string="Positions",translate=True)
    sinced = fields.Boolean(string="sinced",boolean=True)

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, rec.VBRK_VBELN))
        return result

    def cron_create_invoices(self):
        sapinvs = self.env['sap.invoice'].search([('sinced', '=', False)])
        print (sapinvs)

        company = self.env['res.company']
        order = self.env['sale.order']
        partner = self.env['res.partner']
        for sapinv in sapinvs:
            save_it = True
            inv_date = False
            if sapinv.VBRK_FKDAT != '00.00.0000':
                the_date = sapinv.VBRK_FKDAT.replace('.', '')
                inv_date = the_date[4:8] + '-' + the_date[2:4] + '-' + the_date[0:2]
            if sapinv.sap_invoice_position_ids:
                order = self.env['sale.order'].search([('name', '=', sapinv.sap_invoice_position_ids[0].VBKD_BSTKD)])
                company = order.company_id

            for interlocutor in sapinv.sap_invoice_interlocutor_ids:
                if interlocutor.VBPA_PARVW == 'SO':
                    print ('SO', interlocutor.VBPA_KUNNR, order.partner_id.sap_code)
                    if interlocutor.VBPA_KUNNR != order.partner_id.sap_code:
                        self.env['sap.sinc.errors'].create({
                            'model_name': 'sap.invoice',
                            'id_model': sapinv.id,
                            'error_str': "SAP INVOICE: interlocutor de la orden con distinto sap_code al de sap.invoice, id:" + str(sapinv.id),
                            'date_mark': datetime.now(),
                        })
                        #_logger.error("SAP INVOICE: interlocutor de la orden con distinto sap_code al de sap.invoice, id:" + str(sapinv.id))
                        save_it = False

                if interlocutor.VBPA_PARVW == 'EM':
                    print ('EM', interlocutor.VBPA_KUNNR, order.partner_id.sap_code)
                    if interlocutor.VBPA_KUNNR != order.partner_shipping_id.sap_code:
                        self.env['sap.sinc.errors'].create({
                            'model_name': 'sap.invoice',
                            'id_model': sapinv.id,
                            'error_str': "SAP INVOICE: interlocutor de la orden con distinto sap_code al de sap.invoice, id:" + str(sapinv.id),
                            'date_mark': datetime.now(),
                        })
                        #_logger.error("SAP INVOICE: interlocutor de la orden con distinto sap_code al de sap.invoice, id:" + str(sapinv.id))
                        save_it = False

            # for interlocutor in sapinv.sap_invoice_interlocutor_ids:
            #     if interlocutor.VBPA_PARVW == 'SO':
            #         print (interlocutor.VBPA_KUNNR)
            #         print (company)
            #         partner = self.env['res.partner'].search([
            #             ('company_id', '=', company.id),
            #             ('sap_code', '=', interlocutor.VBPA_KUNNR),
            #             ('type', '=', 'contact'),
            #         ])
            #     if interlocutor.VBPA_PARVW == 'EM':
            #         partner_del = self.env['res.partner'].search([
            #             ('company_id', '=', company.id),
            #             ('sap_code', '=', interlocutor.VBPA_KUNNR),
            #             ('type', '=', 'delivery'),
            #         ])
            print (order)
            print (company)
            if not order:
                self.env['sap.sinc.errors'].create({
                    'model_name': 'sap.invioice',
                    'id_model': sapinv.id,
                    'error_str': "SAP INVOICES: no order, id:" + str(sapinv.id),
                    'date_mark': datetime.now(),
                })
                #_logger.error("SAP INVOICES: no order, id:" + str(sapinv.id))
                save_it = False
            if not company:
                self.env['sap.sinc.errors'].create({
                    'model_name': 'sap.invioice',
                    'id_model': sapinv.id,
                    'error_str': "SAP INVOICES: no company, id:" + str(sapinv.id),
                    'date_mark': datetime.now(),
                })
                #_logger.error("SAP INVOICES: no company, id:" + str(sapinv.id))
                save_it = False
            if order and company:
                if sapinv.RETURN == 'N':
                    type = 'out_invoice'
                else:
                    type = 'out_refund'
                vals = {
                    'type': type,
                    'company_id': company.id,
                    'partner_id': order.partner_id.id,
                    'partner_shipping_id': order.partner_shipping_id.id,
                    'name': sapinv.VBRK_XBLNR,
                    'invoice_date': inv_date,
                }
                lines = list()
                order_lines = list()
                for position in sapinv.sap_invoice_position_ids:
                    prod = self.env['product.product'].search([
                        ('company_id', '=', company.id),
                        ('sap_code', '=', position.VBRP_MATNR)
                    ])
                    uom = self.env['uom.uom'].search([('sap_code', '=', position.VBRP_VRKME)])
                    if not uom:
                        self.env['sap.sinc.errors'].create({
                            'model_name': 'sap.invioice',
                            'id_model': sapinv.id,
                            'error_str': "SAP INVOICES: no uom, id:" + str(sapinv.id),
                            'date_mark': datetime.now(),
                        })
                        #_logger.error("SAP INVOICES: no uom, id:" + str(sapinv.id))
                        save_it = False
                    if not prod:
                        self.env['sap.sinc.errors'].create({
                            'model_name': 'sap.invioice',
                            'id_model': sapinv.id,
                            'error_str': "SAP INVOICES: no prod, id:" + str(sapinv.id),
                            'date_mark': datetime.now(),
                        })
                        #_logger.error("SAP INVOICES: no prod, id:" + str(sapinv.id))
                        save_it = False
                    if len(prod)>1:
                        self.env['sap.sinc.errors'].create({
                            'model_name': 'sap.invioice',
                            'id_model': sapinv.id,
                            'error_str': "SAP INVOICES: muchos prod, id:" + str(sapinv.id),
                            'date_mark': datetime.now(),
                        })
                        #_logger.error("SAP INVOICES: muchos prod, id:" + str(sapinv.id))
                        save_it = False

                    if prod and uom and save_it:
                        lines.append((0,0,{
                            'product_id': prod.id,
                            'quantity': position.VBRP_FKIMG,
                            'product_uom_id': uom.id,
                            'price_unit': position.VBRP_NETWR,

                        }))
                    else:
                        save_it = False
                    oline = self.env['sale.order.line'].search([
                        ('sequence', '=', position.VBRP_AUPOS),
                        ('order_id', '=', order.id),
                    ])
                    if oline:
                        order_lines.append((4,oline.id,False))
                    else:
                        self.env['sap.sinc.errors'].create({
                            'model_name': 'sap.invioice',
                            'id_model': sapinv.id,
                            'error_str': "SAP INVOICES: no sale order line, id:" + str(sapinv.id),
                            'date_mark': datetime.now(),
                        })
                        #_logger.error("SAP INVOICES: no sale order line, id:" + str(sapinv.id))
                        save_it = False

                if lines:
                    vals.update({'invoice_line_ids': lines})
                    vals.update({'sale_line_ids ': order_lines})
                else:
                    save_it = False
            else:
                save_it = False
            if save_it:
                try:
                    the_inv = self.env['account.move'].create(vals)
                    print (the_inv)
                    sapinv.write({'sinced': True})
                except Exception as e:
                    self.env['sap.sinc.errors'].create({
                        'model_name': 'sap.invioice',
                        'id_model': sapinv.id,
                        'error_str': "Error SAP INVOICE: " + str(e),
                        'date_mark': datetime.now(),
                    })
                    #_logger.info("Error SAP INVOICE:- %r", str(e))


class SapInvoiceInterlocutor(models.Model):
    _name = 'sap.invoice.interlocutor'
    _description = 'sap.invoice.interlocutor'

    VBPA_PARVW = fields.Char(size=2,string="VBPA_PARVW",translate=True)
    VBPA_KUNNR = fields.Char(size=18,string="VBPA_KUNNR",translate=True)
    sap_invoice_id =fields.Many2one('sap.invoice')

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, rec.VBPA_PARVW))
        return result

class SapInvoicePosition(models.Model):
    _name = 'sap.invoice.position'
    _description = 'sap.invoice.position'

    VBKD_BSTKD = fields.Char(size=8,string="VBKD_BSTKD",translate=True)
    VBRP_POSNR = fields.Char(size=6,string="VBRP_POSNR",translate=True)
    VBRP_MATNR = fields.Char(size=18,string="VBRP_MATNR",translate=True)
    VBRP_FKIMG = fields.Char(size=5,string="VBRP_FKIMG",translate=True)
    VBRP_VRKME = fields.Char(size=3,string="VBRP_VRKME",translate=True)
    VBRP_NETWR = fields.Char(size=15,string="VBRP_NETWR",translate=True)
    VBRP_MWSBP = fields.Char(size=12,string="VBRP_MWSBP",translate=True)
    NETWR_MWSBP = fields.Char(size=15,string="NETWR_MWSBP",translate=True)
    VBRK_WAERK = fields.Char(size=3,string="VBRK_WAERK",translate=True)
    VBRP_AUBEL = fields.Char(size=10,string="VBRP_AUBEL",translate=True)
    VBRP_AUPOS = fields.Char(size=6,string="VBRP_AUPOS",translate=True)
    VBRP_VGBEL = fields.Char(size=10,string="VBRP_VGBEL",translate=True)
    VBRP_VGPOS = fields.Char(size=6,string="VBRP_VGPOS",translate=True)
    sap_invoice_id = fields.Many2one('sap.invoice')

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, rec.VBKD_BSTKD))
        return result

class SapWaers(models.Model):
    _name = 'sap.waers'
    _description = 'sap.waers'

    code = fields.Char(size=10,string="Code",translate=True)
    name = fields.Char(size=50,string="Name",translate=True)

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, rec.code + "/" + rec.name))
        return result

class SapBrsch(models.Model):
    _name = 'sap.brsch'
    _description = 'sap.brsch'

    code = fields.Char(size=4,string="Code",translate=True)
    name = fields.Char(size=50,string="Name",translate=True)

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, rec.name[0:20]))
        return result

class SapWsCredentials(models.Model):
    _name = 'sap.ws.credentials'
    _description = 'sap.ws.credentials'

    user = fields.Char(string="User",translate=True)
    passwd = fields.Char(string="Password",translate=True)
    alias = fields.Char(string="Alias",translate=True)
    apikey = fields.Char(string="Api Key",translate=True)
    endpoint_token = fields.Char(string="EndPoint Token",translate=True)
    endpoint_pedidos = fields.Char(string="EndPoint Pedidos",translate=True)
    token = fields.Char(string="Token",translate=True,readonly=True)
    date_from = fields.Datetime(string="Validate From",readonly=True)
    date_to = fields.Datetime(string="Validate To",readonly=True)

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, rec.user))
        return result

    def Get_token(self):
        credential = self.env['sap.ws.credentials'].search([],limit=1)
        token = ""
        if not credential:
            raise UserError(_("ERROR: NO Credentials"))

        now = datetime.now()
        _logger.info(credential.date_from)
        _logger.info(credential.date_to)
        _logger.info(now)
        if credential.token and credential.date_from < now and now < credential.date_to:
            _logger.info("valido dentro de fechas")
            token = credential.token
        else:
            _logger.info("expirado pidiendo un nuevo token")
            message = credential.user + ":" + credential.passwd
            message_bytes = message.encode('ascii')
            base64_bytes = base64.b64encode(message_bytes)
            base64_message = base64_bytes.decode('ascii')
            headers = {
                'content-type': 'application/json',
                'Authorization': 'Basic ' + base64_message
            }
            print (headers)
            data = "{\"alias\":\"" + credential.alias + "\",\n\"apiKey\":\"" + credential.apikey + "\"\n}"
            base_url = credential.endpoint_token
            req = requests.post(base_url, data=data, headers=headers)
            res =  safe_eval(req.text)
            if 'ObtenerToken_Resp' in res.keys():
                if 'token' in res['ObtenerToken_Resp'].keys():
                    token = res['ObtenerToken_Resp']['token']
                    credential.token = token
                    credential.date_from = now
                    credential.date_to = now + timedelta(days=1)
                else:
                    raise UserError(res['ObtenerToken_Resp'])
            else:
                raise UserError(req.text)

        return token, credential

class SapStock(models.Model):
    _name = 'sap.stock'
    _description = 'sap.stock'

    transaction_date = fields.Datetime(string="Creation Date",translate=True,readonly=True)
    sap_stock_line_ids = fields.One2many('sap.stock.line','sap_stock_id',string="Lines",translate=True)

    @api.model
    def create(self, vals):
        vals.update({'transaction_date': datetime.now()})
        return super(SapStock, self).create(vals)

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, rec.transaction_date))
        return result

class SapStockLine(models.Model):
    _name = 'sap.stock.line'
    _description = 'sap.stock.line'

    sap_stock_id = fields.Many2one('sap.stock')
    COD_CENTRO = fields.Char(string="Cod Centro",translate=True)
    NRO_MATERIAL_SAP = fields.Char(string="Nro Material SAP",translate=True)
    STOCK_LIBRE_UTILIZACION = fields.Char(string="Texto Libre",translate=True)



class SapSincErrors(models.Model):
    _name = 'sap.sinc.errors'
    _description = 'sap.sinc.errors'

    model_name = fields.Char(string="Model Name",readonly=True)
    id_model = fields.Integer(string="ID",readonly=True)
    error_str = fields.Char(string="Error String",readonly=True)
    date_mark = fields.Datetime(string="Datetime of Error",readonly=True)

    def log_error(self, arg_model, arg_id_model, arg_error_str):
        for rec in self:
            rec.create({
                'model_name': arg_model,
                'id_model': arg_id_model,
                'error_str': arg_error_str,
            })


class SapLfa1(models.Model):
    _name = 'sap.lfa1'
    _description = 'sap.lfa1'

    LIFNR = fields.Integer(string="LIFNR",translate=True)
    KTOKK = fields.Char(string="KTOKK",size=4,translate=True)
    LAND1 = fields.Char(string="LAND1",size=2,translate=True)
    NAME1 = fields.Char(string="NAME1",size=35,translate=True)
    ORT01 = fields.Char(string="ORT01",size=35,translate=True)
    PSTLZ = fields.Char(string="PSTLZ",size=10,translate=True)
    REGIO = fields.Char(string="REGIO",size=3,translate=True)
    SPRAS = fields.Char(string="SPRAS",size=2,translate=True)
    STCD1 = fields.Integer(string="STCD1",translate=True)
    STRAS = fields.Char(string="STRAS",size=35,translate=True)
    TELF1 = fields.Integer(string="TELF1",translate=True)
    ZZCONDREG1 = fields.Char(string="ZZCONDREG1",size=2,translate=True)
    LFURL = fields.Char(string="LFURL",size=35,translate=True)
    BUKRS = fields.Integer(string="BUKRS",translate=True)

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, rec.NAME1))
        return result
