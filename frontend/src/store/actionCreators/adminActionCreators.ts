import { Dispatch } from 'redux';
import { actions } from '../actions';
import apiClient from '../apiClient';
import { Constants } from "../../Config/Constants";
import { AdminAction } from '../types';
import { WeatherAlert } from '../../types';
import { ApiWeatherAlert, WeatherAlertInput, WeatherAlertFilters } from './types';
import { transformRequestToSnakeCase, transformResponseToCamelCase } from '../../utils/apiUtils';

const api_urls = Constants.apis;
const adminActions = actions.admin;

export const addWeatherAlert = (weatherAlert: WeatherAlertInput) =>
  (dispatch: Dispatch<AdminAction>) => {
    dispatch(adminActions.addWeatherAlertRequest());

    const apiPayload = transformRequestToSnakeCase(weatherAlert);
    apiClient.post<ApiWeatherAlert>(api_urls.weatherAlerts, apiPayload)
      .then(response => {
        const transformedAlert = transformResponseToCamelCase(response.data) as WeatherAlert;
        dispatch(adminActions.addWeatherAlertSuccess(transformedAlert));
      })
      .catch(error => {
        dispatch(adminActions.addWeatherAlertFailure(error.message));
      });
};

export const fetchWeatherAlerts = (filters: WeatherAlertFilters = {}) =>
  (dispatch: Dispatch<AdminAction>) => {
    dispatch(adminActions.fetchWeatherAlertsRequest());

    const params = new URLSearchParams();
    const snakeCaseFilters = transformRequestToSnakeCase(filters);
    Object.entries(snakeCaseFilters).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        params.append(key, value.toString());
      }
    });

    const url = `${api_urls.weatherAlerts}${params.toString() ? '?' + params.toString() : ''}`;

    apiClient.get<ApiWeatherAlert[]>(url)
      .then(response => {
        const transformedAlerts = response.data.map(alert =>
          transformResponseToCamelCase(alert) as WeatherAlert
        );
        dispatch(adminActions.fetchWeatherAlertsSuccess(transformedAlerts));
      })
      .catch(error => {
        dispatch(adminActions.fetchWeatherAlertsFailure(error.message));
      });
};

export const cancelWeatherAlert = (weatherAlertId: string) =>
  (dispatch: Dispatch<AdminAction>) => {
    dispatch(adminActions.cancelWeatherAlertRequest());

    apiClient.delete(`${api_urls.weatherAlerts}/${weatherAlertId}`)
      .then(response => {
        dispatch(adminActions.cancelWeatherAlertSuccess(weatherAlertId));
      })
      .catch(error => {
        dispatch(adminActions.cancelWeatherAlertFailure(error.message));
      });
};
