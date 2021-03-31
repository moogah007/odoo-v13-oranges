odoo.define('invisible_save_edit.FormController', function (require) {
    'use strict';

    const FormController = require('web.FormController');

    FormController.include({
        init: function (parent, model, renderer, params) {
            this._super.apply(this, arguments);
        },
        _updateButtons: function () {
            this._super.apply(this, arguments);
            if ('invisible_save_edit' in this.renderer.state.context) {
                let invisible = this.renderer.state.evalModifiers({invisible: this.renderer.state.context.invisible_save_edit}).invisible;
                if (!this.$buttons.find('.o_form_buttons_edit').hasClass('o_hidden')) {
                    this.$buttons
                        .find('.o_form_buttons_edit')
                        .toggleClass('o_hidden', invisible);
                }
                if (!this.$buttons.find('.o_form_buttons_view').hasClass('o_hidden')) {
                    this.$buttons
                        .find('.o_form_buttons_view')
                        .toggleClass('o_hidden', invisible);
                }
            }
        },
    });
});
