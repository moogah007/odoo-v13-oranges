/**
 * Copyright 2020 Ketan Kachhela <l.kachhela28@gmail.com>
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
 */

odoo.define('website_sale_extend.website_sale', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');
    var wSaleUtils = require('website_sale.utils');
    var config = require('web.config');

    publicWidget.registry.WebsiteSale.include({
        events: _.extend({}, publicWidget.registry.WebsiteSale.prototype.events || {}, {
            'click .add_to_cart_custom': '_onClickAddCustom',
        }),
        /**
         * @private
         * @param {Event} ev
         */
        _onClickAddCustom: function (ev) {
            var $input = $(ev.currentTarget);
            if ($input.data('update_change')) {
                return;
            }
            var value = parseInt($input.val() || 0, 10);
            if (isNaN(value)) {
                value = 1;
            }
            var $dom = $input.closest('tr');
            var $dom_optional = $dom.nextUntil(':not(.optional_product.info)');
            var line_id = parseInt($input.data('line-id'), 10);
            var productIDs = [parseInt($input.data('product-id'), 10)];
            var $form = $(ev.currentTarget).closest('form');
            var productIDs = parseInt($form.find('input[name="product_id"]').val(), 10);
            this._changeCartQuantity(ev ,$input, 1, $dom_optional, line_id, productIDs, true);
            return false;
        },

        _changeCartQuantity: function (ev, $input, value, $dom_optional, line_id, productIDs, isCustom) {
            if (isCustom) {

                return this._rpc({
                    route: "/shop/cart/update_json",
                    params: {
                        line_id: line_id,
                        product_id: productIDs,
                        add_qty: value
                    },
                }).then(function (data) {
                    var $form = $(ev.currentTarget).closest('form');
                    var $cart_qty = $form.find('input[name="cart_qty"]');
                    var cart_qty = parseInt($cart_qty.val() || 1, 0)
                    $cart_qty.val(cart_qty+value).trigger('change');
                    wSaleUtils.updateCartNavBar(data);
                    $input.val(data.quantity);
                    $('.js_quantity[data-line-id=' + line_id + ']').val(data.quantity).html(data.quantity);

                    if (data.warning) {
                        var cart_alert = $('.oe_cart').parent().find('#data_warning');
                        if (cart_alert.length === 0) {
                            $('.oe_cart').prepend('<div class="alert alert-danger alert-dismissable" role="alert" id="data_warning">' +
                                '<button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button> ' + data.warning + '</div>');
                        } else {
                            cart_alert.html('<button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button> ' + data.warning);
                        }
                        $input.val(data.quantity);
                    }
                    var $navButton = wSaleUtils.getNavBarButton(".o_wsale_my_cart");
                    if (config.device.size_class > config.device.SIZES.MD) {
                        var animation = wSaleUtils.animateClone(
                            $navButton,
                            $(ev.currentTarget).parents(".o_wsale_product_grid_wrapper"),
                            25,
                            40
                        );
                    }
                    else {
                        var animation = wSaleUtils.animateClone(
                            $navButton,
                            $(ev.currentTarget).parents("#mobile_form_view"),
                            25,
                            40
                        );
                    }
                    Promise.all([animation]).then(function (values) {
                    });
                });
            } else {
                this._super.apply(this, arguments);
            }
            return false;
        },

    });
});
