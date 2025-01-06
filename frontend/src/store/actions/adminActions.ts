import * as actionTypes from '../ActionTypes';
import { AdminAction } from '../types';
import { WeatherAlert } from '../../types';

export const addWeatherAlertRequest = (): AdminAction => ({
  type: actionTypes.ADD_WEATHER_ALERT_REQUEST
});

export const addWeatherAlertSuccess = (weatherAlert: WeatherAlert): AdminAction => ({
  type: actionTypes.ADD_WEATHER_ALERT_SUCCESS,
  payload: weatherAlert
});

export const addWeatherAlertFailure = (error: string): AdminAction => ({
  type: actionTypes.ADD_WEATHER_ALERT_FAILURE,
  payload: error
});

export const cancelWeatherAlertRequest = (): AdminAction => ({
  type: actionTypes.CANCEL_WEATHER_ALERT_REQUEST
});

export const cancelWeatherAlertSuccess = (weatherAlertId: string): AdminAction => ({
  type: actionTypes.CANCEL_WEATHER_ALERT_SUCCESS,
  payload: weatherAlertId
});

export const cancelWeatherAlertFailure = (error: string): AdminAction => ({
  type: actionTypes.CANCEL_WEATHER_ALERT_FAILURE,
  payload: error
});

export const fetchWeatherAlertsRequest = (): AdminAction => ({
  type: actionTypes.FETCH_WEATHER_ALERT_REQUEST
});

export const fetchWeatherAlertsSuccess = (weatherAlerts: WeatherAlert[]): AdminAction => ({
  type: actionTypes.FETCH_WEATHER_ALERT_SUCCESS,
  payload: weatherAlerts
});

export const fetchWeatherAlertsFailure = (error: string): AdminAction => ({
  type: actionTypes.FETCH_WEATHER_ALERT_FAILURE,
  payload: error
});
