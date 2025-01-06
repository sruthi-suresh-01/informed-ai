import { Dispatch } from 'redux';
import { actions } from '../actions';
import apiClient from '../apiClient';
import { Constants } from "../../Config/Constants";
import { AdminAction } from '../types';
import { WeatherAlert } from '../../types';

const api_urls = Constants.apis;
const adminActions = actions.admin;

// API response interfaces
interface ApiWeatherAlert {
  weather_alert_id: string;
  zip_code: string;
  message: string;
  created_by: string;
  created_at: string;
  expires_at: string;
  cancelled_at: string | null;
  is_active: boolean;
}

interface WeatherAlertInput {
  zipCode: string;
  message: string;
  expiresAt: string;
}

interface WeatherAlertFilters {
  zipCode?: string;
  isActive?: boolean;
}

const transformWeatherAlert = (apiAlert: ApiWeatherAlert): WeatherAlert => ({
  id: apiAlert.weather_alert_id,
  zipCode: apiAlert.zip_code,
  message: apiAlert.message,
  createdBy: apiAlert.created_by,
  createdAt: apiAlert.created_at,
  expiresAt: apiAlert.expires_at,
  cancelledAt: apiAlert.cancelled_at,
  isActive: apiAlert.is_active
});

export const addWeatherAlert = (weatherAlert: WeatherAlertInput) =>
  (dispatch: Dispatch<AdminAction>) => {
    dispatch(adminActions.addWeatherAlertRequest());

    apiClient.post<ApiWeatherAlert>(api_urls.weatherAlerts, {
      zip_code: weatherAlert.zipCode,
      message: weatherAlert.message,
      expires_at: weatherAlert.expiresAt
    })
      .then(response => {
        dispatch(adminActions.addWeatherAlertSuccess(transformWeatherAlert(response.data)));
      })
      .catch(error => {
        dispatch(adminActions.addWeatherAlertFailure(error.message));
      });
};

export const fetchWeatherAlerts = (filters: WeatherAlertFilters = {}) =>
  (dispatch: Dispatch<AdminAction>) => {
    dispatch(adminActions.fetchWeatherAlertsRequest());

    const params = new URLSearchParams();
    if (filters.zipCode) params.append('zip_code', filters.zipCode);
    if (filters.isActive !== undefined && filters.isActive !== null) {
      params.append('is_active', filters.isActive.toString());
    }

    const url = `${api_urls.weatherAlerts}${params.toString() ? '?' + params.toString() : ''}`;

    apiClient.get<ApiWeatherAlert[]>(url)
      .then(response => {
        const transformedAlerts = response.data.map(transformWeatherAlert);
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
