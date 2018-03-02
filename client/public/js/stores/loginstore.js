import { EventEmitter } from "events";
import dispatcher from '../dispatchers/dispatcher.js'

import cookie from 'react-cookies'

import * as LoginActions from  '../actions/loginactions.js'

class LoginStore extends EventEmitter {
	constructor() {
		super()

		this.user = null;
		this.loggedInState = 'unknown';

		this.loginStatus = 'idle';
		this.loginError = '';

		this.logoutStatus = 'idle';
		this.logoutError = '';

		this.checkSessionStatus = 'idle';
		this.checkSessionError = '';

		this.otpauth = null;
		this.getTwoFactorTokenStatus = 'idle';
		this.getTwoFactorTokenError = '';

		this.enableTwoFactorAuthenticationStatus = 'idle';
		this.enableTwoFactorAuthenticationError = '';

		this.disableTwoFactorAuthenticationStatus = 'idle';
		this.disableTwoFactorAuthenticationError = '';
	}
	
	handleActions(action) {
		switch(action.type) {
			//Changed logged in state
			case "CHANGE_LOGGED_IN_STATE": {
				if (this.loggedInState !== action.data) {
					this.loggedInState = action.data;
					this.emit('changedLoggedInState');

					if (this.loggedInState === 'loggedout') {
						this.user = null;
						window.location.href = '#';
						LoginActions.logout();
					}
				}
				break;
			}

			case "UPDATE_USER" : {
				if (this.user && this.user.userId === action.data.userId) {
					this.user = action.data;
					this.emit('updatedUser');
				}
				break;
			}

			case "OPEN_2FA_DIALOG": {
				this.emit('open2FADialog');
				break;
			}

			//Logging In
			case "LOGGING_IN": {
				this.loginStatus = 'fetching'
				this.emit('changedLoggedInStatus');
				break;
			}
			case "LOGGED_IN": {
				this.user = action.data.user;

				const expires = new Date()
				expires.setTime(expires.getTime() + 4000*60*60*1000)

				cookie.save('userid', this.user.userId, { path: '/', expires, maxAge: 4000*60*60 })
				cookie.save('sessiontoken', action.data.sessionToken, { path: '/', expires, maxAge: 4000*60*60 })

				if (this.loggedInState !== 'loggedin') {
					this.loggedInState = 'loggedin';
					this.emit('changedLoggedInState');
				}
				this.loginStatus = 'fetched'
				this.emit('changedLoggedInStatus');
				this.loginStatus = 'idle'
				this.emit('changedLoggedInStatus');
				break;
			}
			case "ERROR_LOGGING_IN": {
				this.loginError = action.data;
				this.loginStatus = 'error'
				this.emit('changedLoggedInStatus');
				this.loginStatus = 'idle'
				this.emit('changedLoggedInStatus');
				break;
			}

			//Logging Out
			case "LOGGING_OUT": {
				setTimeout(() => {
					cookie.remove('userid');
					cookie.remove('sessiontoken');
					this.user = null;					
				}, 100);

				if (this.loggedInState !== 'loggedout') {
					this.loggedInState = 'loggedout';
					this.emit('changedLoggedInState');
				}

				this.logoutStatus = 'fetching'
				this.emit('changedLoggedOutStatus');
				break;
			}
			case "LOGGED_OUT": {
				this.logoutStatus = 'fetched'
				this.emit('changedLoggedOutStatus');
				this.logoutStatus = 'idle'
				this.emit('changedLoggedOutStatus');
				break;
			}
			case "ERROR_LOGGING_OUT": {
				this.logoutError = action.data;
				this.logoutStatus = 'error'
				this.emit('changedLoggedOutStatus');
				this.logoutStatus = 'idle'
				this.emit('changedLoggedOutStatus');
				break;
			}

			//Checking Session
			case "CHECKING_SESSION": {
				this.checkSessionStatus = 'fetching'
				this.emit('changedCheckSessionStatus');
				break;
			}
			case "CHECKED_SESSION": {
				this.user = action.data.user

				const expires = new Date()
				expires.setTime(expires.getTime() + 4000*60*60*1000)

				cookie.save('userid', this.user.userId, { path: '/', expires, maxAge: 4000*60*60 })
				cookie.save('sessiontoken', cookie.load('sessiontoken'), { path: '/', expires, maxAge: 4000*60*60 })

				if (this.loggedInState !== 'loggedin') {
					this.loggedInState = 'loggedin';
					this.emit('changedLoggedInState');
				}
				this.checkSessionStatus = 'fetched'
				this.emit('changedCheckSessionStatus');
				this.checkSessionStatus = 'idle'
				this.emit('changedCheckSessionStatus');
				break;
			}
			case "ERROR_CHECKING_SESSION": {
				cookie.remove('userid');
				cookie.remove('sessiontoken');
				this.user = null;

				if (this.loggedInState !== 'loggedout') {
					this.loggedInState = 'loggedout';
					this.emit('changedLoggedInState');
				}
				this.checkSessionError = action.data;
				this.checkSessionStatus = 'error'
				this.emit('changedCheckSessionStatus');
				this.checkSessionStatus = 'idle'
				this.emit('changedCheckSessionStatus');
				break;
			}

			//Get Two Factor Token
			case "GETTING_TWO_FACTOR_TOKEN": {
				this.otpauth = null;
				this.getTwoFactorTokenStatus = 'fetching';
				this.emit('changedGetTwoFactorTokenStatus');
				break;
			}
			case "GOT_TWO_FACTOR_TOKEN": {
				this.otpauth = action.data.otpauth;
				this.getTwoFactorTokenStatus = 'fetched';
				this.emit('changedGetTwoFactorTokenStatus');
				this.getTwoFactorTokenStatus = 'idle';
				this.emit('changedGetTwoFactorTokenStatus');
				break;
			}
			case "ERROR_GETTING_TWO_FACTOR_TOKEN": {
				this.getTwoFactorTokenError = action.data;
				this.getTwoFactorTokenStatus = 'error';
				this.emit('changedGetTwoFactorTokenStatus');
				this.getTwoFactorTokenStatus = 'idle';
				this.emit('changedGetTwoFactorTokenStatus');				
				break;
			}

			//Enable Two Factor Authentication
			case "ENABLING_TWO_FACTOR_AUTHENTICATION": {
				this.enableTwoFactorAuthenticationStatus = 'fetching';
				this.emit('changedEnableTwoFactorAuthenticationStatus');
				break;
			}
			case "ENABLED_TWO_FACTOR_AUTHENTICATION": {
				this.user = action.data.user
				setTimeout(() => { this.emit('updatedUser'); }, 0);
				this.enableTwoFactorAuthenticationStatus = 'fetched';
				this.emit('changedEnableTwoFactorAuthenticationStatus');
				this.enableTwoFactorAuthenticationStatus = 'idle';
				this.emit('changedEnableTwoFactorAuthenticationStatus');
				break;
			}
			case "ERROR_ENABLING_TWO_FACTOR_AUTHENTICATION": {
				this.enableTwoFactorAuthenticationError = action.data;				
				this.enableTwoFactorAuthenticationStatus = 'error';
				this.emit('changedEnableTwoFactorAuthenticationStatus');
				this.enableTwoFactorAuthenticationStatus = 'idle';
				this.emit('changedEnableTwoFactorAuthenticationStatus');
				break;
			}

			//Disable Two Factor Authentication
			case "DISABLING_TWO_FACTOR_AUTHENTICATION": {
				this.disableTwoFactorAuthenticationStatus = 'fetching';
				this.emit('changedDisableTwoFactorAuthenticationStatus');
				break;
			}
			case "DISABLED_TWO_FACTOR_AUTHENTICATION": {
				this.user = action.data.user
				setTimeout(() => { this.emit('updatedUser'); }, 0);
				this.disableTwoFactorAuthenticationStatus = 'fetched';
				this.emit('changedDisableTwoFactorAuthenticationStatus');
				this.disableTwoFactorAuthenticationStatus = 'idle';
				this.emit('changedDisableTwoFactorAuthenticationStatus');
				break;
			}
			case "ERROR_DISABLING_TWO_FACTOR_AUTHENTICATION": {
				this.disableTwoFactorAuthenticationError = action.data;
				this.disableTwoFactorAuthenticationStatus = 'error';
				this.emit('changedDisableTwoFactorAuthenticationStatus');
				this.disableTwoFactorAuthenticationStatus = 'idle';
				this.emit('changedDisableTwoFactorAuthenticationStatus');
				break;
			}
		}
	}
}

const loginStore = new LoginStore();
dispatcher.register(loginStore.handleActions.bind(loginStore));

if (cookie.load('userid') && cookie.load('sessiontoken')) {
	LoginActions.checkSession();
} else {
	loginStore.loggedInState = 'loggedout';
}

export default loginStore;