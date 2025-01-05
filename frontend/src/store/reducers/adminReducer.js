import * as actionTypes from '../ActionTypes';

const initialState = {
    weatherAlerts: [],
    isLoading: false,
    error: null
};

function adminReducer(state = initialState, action) {
    switch (action.type) {
        case actionTypes.ADD_WEATHER_ALERT_REQUEST:
        case actionTypes.CANCEL_WEATHER_ALERT_REQUEST:
        case actionTypes.FETCH_WEATHER_ALERT_REQUEST:
            return { ...state, isLoading: true, error: null };

        case actionTypes.ADD_WEATHER_ALERT_SUCCESS:
            return {
                ...state,
                isLoading: false,
                weatherAlerts: [...state.weatherAlerts, action.payload],
                error: null
            };

        case actionTypes.CANCEL_WEATHER_ALERT_SUCCESS:
            return {
                ...state,
                isLoading: false,
                weatherAlerts: state.weatherAlerts.map(weatherAlert =>
                    weatherAlert.weather_alert_id === action.payload
                        ? { ...weatherAlert, is_active: false }
                        : weatherAlert
                ),
                error: null
            };

        case actionTypes.FETCH_WEATHER_ALERT_SUCCESS:
            return {
                ...state,
                isLoading: false,
                weatherAlerts: action.payload,
                error: null
            };

        case actionTypes.ADD_WEATHER_ALERT_FAILURE:
        case actionTypes.CANCEL_WEATHER_ALERT_FAILURE:
        case actionTypes.FETCH_WEATHER_ALERT_FAILURE:
            return { ...state, isLoading: false, error: action.payload };

        default:
            return state;
    }
}

export default adminReducer;
