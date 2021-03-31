odoo.define('ld_sap_integration.website_sale', function (require) {
'use strict';

var ajax = require('web.ajax');
var core = require('web.core');
var publicWidget = require('web.public.widget');
require('website_sale.website_sale');

var _t = core._t;

publicWidget.registry.WebsiteSale.include({

    events: _.extend({}, publicWidget.registry.WebsiteSale.prototype.events || {}, {
        'click span.btn-get-price': '_onChangeGetPrice',
    }),

    _onChangeGetPrice: function (ev) {
        var self = this;
        var so_id = $(ev.currentTarget).data('so_id');
        if (so_id) {
            this._rpc({
                model: 'sale.order',
                method: 'send_to_sap_web',
                args: [[so_id]]
            }).then(function (data) {
                window.location.reload()
            });
        }
        return false;
    },
});

});
