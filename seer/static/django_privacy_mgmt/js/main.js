var django_privacy_mgmt = {
    __init__: function () {

    },

    PREFERENCE_COOKIE_NAME: 'django_privacy_mgmt_preferences',

    PREFERENCES: {
        'ESSENTIALS': {
            'required': true,
            'default': true
        },
        'STATISTICS': {
            'required': false,
            'default': false
        },
        'MARKETING': {
            'required': false,
            'default': false
        },
    },

    _isBoolean: function (value) {
        return typeof(value) === typeof(true);
    },

    setPreference: function (name, value) {
        // sets preferences in the preferences cookie
        // used by the preferences modal

        if (!this._isBoolean(value)) {
            console.log('Preference value must be boolean.');
            return;
        }

        preferences = this._getPreferences();

        try {
            preferences[name] = value
        } catch (e) {
            console.log(e);
            // fail silently
        }
        var date = new Date();
        if (preferences[name]) {
	    date.setUTCFullYear(date.getUTCFullYear() + 2);
        } else {
            date.setUTCFullYear(2099);
            date.setUTCMonth(11);
            date.setUTCDate(31);
            date.setUTCHours(23);
            date.setUTCMinutes(59);
            date.setUTCSeconds(59);
        }
        Cookies.set(this.PREFERENCE_COOKIE_NAME, preferences, {
            // in FF this is required so that the cookie is not deleted after ending the browser session
            // we set it to a very high number of dates so that this cookie 'never' expires.
            expires: date
        })
    },

    _getPreferences: function () {
        preferences = Cookies.getJSON(this.PREFERENCE_COOKIE_NAME);
        if (!preferences) {
            preferences = {}
        }
        return preferences;
    },

    getPreference: function (name) {
        preferences = this._getPreferences();

        if (preferences.hasOwnProperty(name)) {
            return Boolean(preferences[name]);
        } else {
            // default
            this.setPreference(name, this.PREFERENCES[name]['default']);
            return this.PREFERENCES[name]['default'];
        }
    }
};
