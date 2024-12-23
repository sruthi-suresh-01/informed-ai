import { actions } from '../actions';
import apiClient from '../apiClient';
import { Constants } from "../../Config/Constants";

const api_urls = Constants.apis;
const adminActions = actions.admin;

export const addWeatherAlert = (weatherAlert) => dispatch => {
    dispatch(adminActions.addWeatherAlertRequest());

    apiClient.post(api_urls.weatherAlerts, {
        zip_code: weatherAlert.zipCode,
        message: weatherAlert.message,
        expires_at: weatherAlert.expiresAt
    })
        .then(response => {
            const data = response.data;
            if (data.error) {
                dispatch(adminActions.addWeatherAlertFailure(data.error));
            } else {
                dispatch(adminActions.addWeatherAlertSuccess(data));
            }
        })
        .catch(error => {
            dispatch(adminActions.addWeatherAlertFailure(error.message));
        });
};

export const cancelWeatherAlert = (weatherAlertId) => dispatch => {
    dispatch(adminActions.cancelWeatherAlertRequest());

    apiClient.delete(`${api_urls.weatherAlerts}/${weatherAlertId}`)
        .then(response => {
            const data = response.data;
            if (data.error) {
                dispatch(adminActions.cancelWeatherAlertFailure(data.error));
            } else {
                dispatch(adminActions.cancelWeatherAlertSuccess(weatherAlertId));
            }
        })
        .catch(error => {
            dispatch(adminActions.cancelWeatherAlertFailure(error.message));
        });
};

export const fetchWeatherAlerts = (filters = {}) => dispatch => {
    dispatch(adminActions.fetchWeatherAlertsRequest());

    const params = new URLSearchParams();
    if (filters.zipCode) params.append('zip_code', filters.zipCode);
    if (filters.isActive !== undefined && filters.isActive !== null) params.append('is_active', filters.isActive);

    const url = `${api_urls.weatherAlerts}${params.toString() ? '?' + params.toString() : ''}`;

    apiClient.get(url)
        .then(response => {
            const data = response.data;
            if (data.error) {
                dispatch(adminActions.fetchWeatherAlertsFailure(data.error));
            } else {
                dispatch(adminActions.fetchWeatherAlertsSuccess(data));
            }
        })
        .catch(error => {
            dispatch(adminActions.fetchWeatherAlertsFailure(error.message));
        });
};
