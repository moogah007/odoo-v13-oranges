odoo.define('website_portal_date.portal.chatter', function (require) {
'use strict';

var portalChatter = require('portal.chatter');
var PortalChatter = portalChatter.PortalChatter;
var core = require('web.core');
var time = require('web.time');

var _t = core._t;

/**
 * PortalChatter
 *
 * Extends Frontend Chatter to handle rating
 */
PortalChatter.include({
    /**
     * Update the messages format
     *
     * @param {Array<Object>}
     * @returns {Array}
     */
    preprocessMessages: function (messages) {
        _.each(messages, function (m) {
            m['author_avatar_url'] = _.str.sprintf('/web/image/%s/%s/author_avatar/50x50', 'mail.message', m.id);
            m['published_date_str'] = _.str.sprintf(_t('Published on %s'), moment(time.str_to_datetime(m.date)).format(time.getLangDatetimeFormat()));
        });
        return messages;
    },

});
});
