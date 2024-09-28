import { actions } from '../actions'
import apiClient from '../apiClient';
import { Constants } from "../../Config/Constants";

const api_urls = Constants.apis
const userActions = actions.user

export const login = ({ username, password }) => dispatch => {
    dispatch(userActions.loginRequest());

    if (username) {
        apiClient.post(api_urls.login, { username })
            .then(response => {
                const data = response.data;
                if (data.error) {
                    dispatch(userActions.loginFailure(data.error));
                } else if(data && data.data) {
                    dispatch(userActions.loginSuccess(data.data));
                }
            })
            .catch(error => {
                dispatch(userActions.loginFailure(error.message));
            });
    } else {
        dispatch(userActions.loginFailure("Username is required"));
    }
}


export const logout = () => dispatch => {
    dispatch(userActions.logoutRequest());

    apiClient.get(api_urls.logout)
        .then(response => {
            const data = response.data
            if (data.error) {
            dispatch(userActions.logoutFailure(data.error));
            } else {
            dispatch(userActions.logoutSuccess(data));
            }
        })
        .catch(error => dispatch(userActions.logoutFailure(error.message)));
}

export const verifyLogin = () => dispatch => {
    dispatch(userActions.verifyLoginRequest());

    apiClient.get(api_urls.verifyLogin)
        .then(response => {
            const data = response.data
            if (data.error) {
            dispatch(userActions.verifyLoginFailure(data.error));
            } else if(!data.sessionAlive){
                dispatch(userActions.verifyLoginFailure("No Session found"));
            } else {
            dispatch(userActions.verifyLoginSuccess(data.data));
            }
        })
        .catch(error => {
            dispatch(userActions.verifyLoginFailure(error.message))
        });
}

export const register = ({ username, password }) => dispatch => {
    dispatch(userActions.loginRequest());

    if (username) {
        apiClient.post(api_urls.login, { username })
            .then(response => {
                const data = response.data;
                if (data.error) {
                    dispatch(userActions.loginFailure(data.error));
                } else if(data && data.data) {
                    dispatch(userActions.loginSuccess(data.data));
                }
            })
            .catch(error => {
                dispatch(userActions.loginFailure(error.message));
            });
    } else {
        dispatch(userActions.loginFailure("Username is required"));
    }
}

export const getUserDetails = ({ username }) => dispatch => {
    dispatch(userActions.getUserDetailsRequest());

    apiClient.get(api_urls.getUserDetails.replace('{username}', username))
        .then(response => {
            const data = response.data
            console.log(data)
            if (data.error) {
            dispatch(userActions.getUserDetailsFailure(data.error));
            } else {
            dispatch(userActions.getUserDetailsSuccess(data));
            }
        })
        .catch(error => dispatch(userActions.getUserDetailsFailure(error.message)));
}

export const setUserDetails = ({ username, payload }) => dispatch => {
    dispatch(userActions.setUserDetailsRequest());

    if (username) {
        apiClient.post(api_urls.setUserDetails.replace('{username}', username), payload)
            .then(response => {
                const data = response.data;
                console.log(data)
                if (data.error) {
                    dispatch(userActions.setUserDetailsFailure(data.error));
                } else if(data && data.data) {
                    dispatch(userActions.setUserDetailsSuccess(data.data));
                }
            })
            .catch(error => {
                dispatch(userActions.setUserDetailsFailure(error.message));
            });
    } else {
        dispatch(userActions.setUserDetailsFailure("Username is required"));
    }
}

// Update User Medical Details

export const getUserMedicalDetails = ({ username }) => dispatch => {
    dispatch(userActions.getUserMedicalDetailsRequest());

    apiClient.get(api_urls.getUserMedicalDetails.replace('{username}', username))
        .then(response => {
            const data = response.data
            console.log(data)
            if (data.error) {
            dispatch(userActions.getUserMedicalDetailsFailure(data.error));
            } else {
            dispatch(userActions.getUserMedicalDetailsSuccess(data));
            }
        })
        .catch(error => dispatch(userActions.getUserMedicalDetailsFailure(error.message)));
}

export const setUserMedicalDetails = ({ username, payload }) => dispatch => {
    dispatch(userActions.setUserMedicalDetailsRequest());

    if (username) {
        apiClient.post(api_urls.setUserMedicalDetails.replace('{username}', username), payload)
            .then(response => {
                const data = response.data;
                console.log(data)
                if (data.error) {
                    dispatch(userActions.setUserMedicalDetailsFailure(data.error));
                } else if(data && data.data) {
                    dispatch(userActions.setUserMedicalDetailsSuccess(data.data));
                }
            })
            .catch(error => {
                dispatch(userActions.setUserMedicalDetailsFailure(error.message));
            });
    } else {
        dispatch(userActions.setUserMedicalDetailsFailure("Username is required"));
    }
}