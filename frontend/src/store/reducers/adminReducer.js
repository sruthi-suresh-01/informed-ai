import * as actionTypes from '../ActionTypes';

const initialState = {
    notifications: [],
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
                notifications: [...state.notifications, action.payload],
                error: null
            };

        case actionTypes.CANCEL_WEATHER_ALERT_SUCCESS:
            return {
                ...state,
                isLoading: false,
                notifications: state.notifications.map(notification =>
                    notification.id === action.payload
                        ? { ...notification, is_active: false }
                        : notification
                ),
                error: null
            };

        case actionTypes.FETCH_WEATHER_ALERT_SUCCESS:
            return {
                ...state,
                isLoading: false,
                notifications: action.payload,
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
