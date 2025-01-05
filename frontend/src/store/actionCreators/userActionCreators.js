import { actions } from '../actions'
import apiClient from '../apiClient';
import { Constants } from "../../Config/Constants";

const api_urls = Constants.apis
const userActions = actions.user


export const registerUser = ({ email, first_name, last_name }) => dispatch => {
    dispatch(userActions.registerUserRequest());

    if (email) {
        apiClient.post(api_urls.register, { email, first_name, last_name })
            .then(response => {
                const data = response.data;
                if (data.error) {
                    dispatch(userActions.registerUserFailure(data.error));
                } else if(data && data.user) {
                    dispatch(userActions.registerUserSuccess(data.user));
                }
            })
            .catch(error => {
                dispatch(userActions.registerUserFailure(error.message));
            });
    } else {
        dispatch(userActions.registerUserFailure("Email is required"));
    }
}

export const login = ({ email, password }) => dispatch => {
    dispatch(userActions.loginRequest());

    if (email) {
        apiClient.post(api_urls.login, { email })
            .then(response => {
                const data = response.data;
                if (data.error) {
                    dispatch(userActions.loginFailure(data.error));
                } else if(data && data.user) {
                    dispatch(userActions.loginSuccess(data.user));
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
            if(data && data.user) {
                dispatch(userActions.verifyLoginSuccess(data.user));
            }
        })
        .catch(error => {
            dispatch(userActions.verifyLoginFailure(error.message))
        });
}

export const getUserDetails = () => dispatch => {
    // dispatch(userActions.getUserDetailsRequest());

    apiClient.get(api_urls.getUserDetails)
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

export const setUserDetails = ({ payload }) => dispatch => {
    dispatch(userActions.setUserDetailsRequest());

    apiClient.post(api_urls.setUserDetails, payload)
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
}

// Update User Medical Details

export const getUserMedicalDetails = () => dispatch => {
    dispatch(userActions.getUserMedicalDetailsRequest());

    apiClient.get(api_urls.getUserMedicalDetails)
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

export const setUserMedicalDetails = ({ payload }) => dispatch => {
    dispatch(userActions.setUserMedicalDetailsRequest());

    apiClient.post(api_urls.setUserMedicalDetails, payload)
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
}

export const getUserSettings = () => dispatch => {
    dispatch(userActions.getUserSettingsRequest());

    apiClient.get(api_urls.getUserSettings)
        .then(response => {
            dispatch(userActions.getUserSettingsSuccess(response.data));
        })
        .catch(error => dispatch(userActions.getUserSettingsFailure(error.message)));
}

export const setUserSettings = ({ payload }) => dispatch => {
    dispatch(userActions.setUserSettingsRequest());

    apiClient.post(api_urls.setUserSettings, payload)
    .then(response => {
        dispatch(userActions.setUserSettingsSuccess(response.data));
    })
    .catch(error => dispatch(userActions.setUserSettingsFailure(error.message)));
}

export const fetchNotifications = () => dispatch => {
    dispatch(userActions.fetchNotificationsRequest());

    apiClient.get(api_urls.fetchNotifications)
        .then(response => {
            if(response.data && response.data.notifications) {
                dispatch(userActions.fetchNotificationsSuccess(response.data.notifications));
            }
        })
        .catch(error => dispatch(userActions.fetchNotificationsFailure(error.message)));
}

export const updateNotificationStatus = ({ notification_ids, status }) => dispatch => {
    dispatch(userActions.updateNotificationStatusRequest());

    apiClient.put(api_urls.updateNotificationStatus, { notification_ids, status })
    .then(response => {
        if(response.data && response.data.notifications) {
            dispatch(userActions.updateNotificationStatusSuccess(response.data.notifications));
        }
    })
    .catch(error => dispatch(userActions.updateNotificationStatusFailure(error.message)));
}
