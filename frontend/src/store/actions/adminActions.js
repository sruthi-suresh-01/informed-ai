import * as actionTypes from '../ActionTypes';

export const addWeatherAlertRequest = () => ({
    type: actionTypes.ADD_WEATHER_ALERT_REQUEST
});

export const addWeatherAlertSuccess = (notification) => ({
    type: actionTypes.ADD_WEATHER_ALERT_SUCCESS,
    payload: notification
});

export const addWeatherAlertFailure = (error) => ({
    type: actionTypes.ADD_WEATHER_ALERT_FAILURE,
    payload: error
});

export const cancelWeatherAlertRequest = () => ({
    type: actionTypes.CANCEL_WEATHER_ALERT_REQUEST
});

export const cancelWeatherAlertSuccess = (notificationId) => ({
    type: actionTypes.CANCEL_WEATHER_ALERT_SUCCESS,
    payload: notificationId
});

export const cancelWeatherAlertFailure = (error) => ({
    type: actionTypes.CANCEL_WEATHER_ALERT_FAILURE,
    payload: error
});

export const fetchWeatherAlertsRequest = () => ({
    type: actionTypes.FETCH_WEATHER_ALERT_REQUEST
});

export const fetchWeatherAlertsSuccess = (notifications) => ({
    type: actionTypes.FETCH_WEATHER_ALERT_SUCCESS,
    payload: notifications
});

export const fetchWeatherAlertsFailure = (error) => ({
    type: actionTypes.FETCH_WEATHER_ALERT_FAILURE,
    payload: error
});
