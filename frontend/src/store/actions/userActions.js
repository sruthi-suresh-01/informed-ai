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

export const verifyLoginRequest = () => {
    return { type: actionTypes.VERIFY_LOGIN_REQUEST };
}

export const verifyLoginSuccess = (user) => {
    return { type: actionTypes.VERIFY_LOGIN_SUCCESS, payload: user };
}

export const verifyLoginFailure = (error) => {
    return { type: actionTypes.VERIFY_LOGIN_FAILURE, payload: error };
}

export const registerUserRequest = () => {
    return { type: actionTypes.REGISTER_USER_REQUEST };
}

export const registerUserSuccess = (user) => {
    return { type: actionTypes.REGISTER_USER_SUCCESS, payload: user };
}

export const registerUserFailure = (error) => {
    return { type: actionTypes.REGISTER_USER_FAILURE, payload: error };
}

export const getUserDetailsRequest = () => {
    return { type: actionTypes.GET_USER_DETAILS_REQUEST };
}

export const getUserDetailsSuccess = (payload) => {
    return { type: actionTypes.GET_USER_DETAILS_SUCCESS, payload };
}

export const getUserDetailsFailure = (error) => {
    return { type: actionTypes.GET_USER_DETAILS_FAILURE, payload: error };
}

export const setUserDetailsRequest = () => {
    return { type: actionTypes.SET_USER_DETAILS_REQUEST };
}

export const setUserDetailsSuccess = (payload) => {
    return { type: actionTypes.SET_USER_DETAILS_SUCCESS, payload };
}

export const setUserDetailsFailure = (error) => {
    return { type: actionTypes.SET_USER_DETAILS_FAILURE, payload: error };
}

//
export const getUserMedicalDetailsRequest = () => {
    return { type: actionTypes.GET_USER_MEDICAL_DETAILS_REQUEST };
}

export const getUserMedicalDetailsSuccess = (user) => {
    return { type: actionTypes.GET_USER_MEDICAL_DETAILS_SUCCESS, payload: user };
}

export const getUserMedicalDetailsFailure = (error) => {
    return { type: actionTypes.GET_USER_MEDICAL_DETAILS_FAILURE, payload: error };
}

export const setUserMedicalDetailsRequest = () => {
    return { type: actionTypes.SET_USER_MEDICAL_DETAILS_REQUEST };
}

export const setUserMedicalDetailsSuccess = (user) => {
    return { type: actionTypes.SET_USER_MEDICAL_DETAILS_SUCCESS, payload: user };
}

export const setUserMedicalDetailsFailure = (error) => {
    return { type: actionTypes.SET_USER_MEDICAL_DETAILS_FAILURE, payload: error };
}
