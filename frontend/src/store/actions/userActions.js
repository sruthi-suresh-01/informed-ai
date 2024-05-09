import * as actionTypes from '../ActionTypes';

export const loginRequest = () => {
    return { type: actionTypes.LOGIN_REQUEST };
}

export const loginSuccess = (user) => {
    return { type: actionTypes.LOGIN_SUCCESS, payload: user };
}

export const loginFailure = (error) => {
    return { type: actionTypes.LOGIN_FAILURE, payload: error };
}

export const logoutRequest = () => {
    return { type: actionTypes.LOGOUT_REQUEST };
}

export const logoutSuccess = (message) => {
    return { type: actionTypes.LOGOUT_SUCCESS, payload: message };
}

export const logoutFailure = (error) => {
    return { type: actionTypes.LOGOUT_FAILURE, payload: error };
}