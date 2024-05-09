import { actions } from '../actions'
import apiClient from '../apiClient';
import { Constants } from "../../Config/Constants";

const api_urls = Constants.apis
const userActions = actions.user

// Async action creator example using thunk middleware

export const login = ({ username, password }) => dispatch => {
    dispatch(userActions.loginRequest());

    if (username) {
        apiClient.post(api_urls.login, { username })
            .then(response => {
                const data = response.data;
                if (data.error) {
                    dispatch(userActions.loginFailure(data.error));
                } else {
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

