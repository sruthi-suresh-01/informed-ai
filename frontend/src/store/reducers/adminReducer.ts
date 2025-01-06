import * as actionTypes from '../ActionTypes';
import { AdminAction } from '../types';
import { WeatherAlert } from '../../types';
import { AdminState } from '../types';

const initialState: AdminState = {
  weatherAlerts: [],
  isLoading: false,
  error: null
};

const adminReducer = (
  state: AdminState = initialState,
  action: AdminAction
): AdminState => {
  switch (action.type) {
    case actionTypes.ADD_WEATHER_ALERT_REQUEST:
    case actionTypes.CANCEL_WEATHER_ALERT_REQUEST:
    case actionTypes.FETCH_WEATHER_ALERT_REQUEST:
      return { ...state, isLoading: true, error: null };

    case actionTypes.ADD_WEATHER_ALERT_SUCCESS:
      return {
        ...state,
        isLoading: false,
        weatherAlerts: [...state.weatherAlerts, action.payload as WeatherAlert],
        error: null
      };

    case actionTypes.CANCEL_WEATHER_ALERT_SUCCESS:
      return {
        ...state,
        isLoading: false,
        weatherAlerts: state.weatherAlerts.map(weatherAlert =>
          weatherAlert.id === action.payload
            ? { ...weatherAlert, isActive: false }
            : weatherAlert
        ),
        error: null
      };

    case actionTypes.FETCH_WEATHER_ALERT_SUCCESS:
      return {
        ...state,
        isLoading: false,
        weatherAlerts: action.payload as WeatherAlert[],
        error: null
      };

    case actionTypes.ADD_WEATHER_ALERT_FAILURE:
    case actionTypes.CANCEL_WEATHER_ALERT_FAILURE:
    case actionTypes.FETCH_WEATHER_ALERT_FAILURE:
      return {
        ...state,
        isLoading: false,
        error: action.payload as string
      };

    default:
      return state;
  }
};

export default adminReducer;
