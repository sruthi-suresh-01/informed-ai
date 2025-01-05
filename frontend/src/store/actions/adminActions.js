import * as actionTypes from '../ActionTypes';

export const addWeatherAlertRequest = () => ({
    type: actionTypes.ADD_WEATHER_ALERT_REQUEST
});

export const addWeatherAlertSuccess = (weatherAlert) => ({
    type: actionTypes.ADD_WEATHER_ALERT_SUCCESS,
    payload: weatherAlert
});

export const addWeatherAlertFailure = (error) => ({
    type: actionTypes.ADD_WEATHER_ALERT_FAILURE,
    payload: error
});

export const cancelWeatherAlertRequest = () => ({
    type: actionTypes.CANCEL_WEATHER_ALERT_REQUEST
});

export const cancelWeatherAlertSuccess = (weatherAlertId) => ({
    type: actionTypes.CANCEL_WEATHER_ALERT_SUCCESS,
    payload: weatherAlertId
});

export const cancelWeatherAlertFailure = (error) => ({
    type: actionTypes.CANCEL_WEATHER_ALERT_FAILURE,
    payload: error
});

export const fetchWeatherAlertsRequest = () => ({
    type: actionTypes.FETCH_WEATHER_ALERT_REQUEST
});

export const fetchWeatherAlertsSuccess = (weatherAlerts) => ({
    type: actionTypes.FETCH_WEATHER_ALERT_SUCCESS,
    payload: weatherAlerts
});

export const fetchWeatherAlertsFailure = (error) => ({
    type: actionTypes.FETCH_WEATHER_ALERT_FAILURE,
    payload: error
});
