/**
 * Copyright 2020 Ketan Kachhela <l.kachhela28@gmail.com>
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
 */
odoo.define('website_product_extended.utils_extended', function (require) {
'use strict';

var wSaleUtils = require('website_sale.utils');

// FIXME : Need to check logic regarding updation on qty change from cart page.
wSaleUtils.updateCartNavBar = function updateCartNavBar(data){
    var $qtyNavBar = $(".my_cart_quantity");
    _.each($qtyNavBar, function (qty) {
        var $qty = $(qty);
        $qty.parents('li:first').removeClass('d-none');
        $qty.html(data.cart_categ_qty).hide().fadeIn(600);
    });
    $(".js_cart_lines").first().before(data['website_sale.cart_lines']).end().remove();
    $(".js_cart_summary").first().before(data['website_sale.short_cart_summary']).end().remove();
}

});