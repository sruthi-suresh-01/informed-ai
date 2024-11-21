import * as actionTypes from '../ActionTypes';

const initialState = {
    notifications: [],
    isLoading: false,
    error: null
};

function adminReducer(state = initialState, action) {
    switch (action.type) {
        case actionTypes.ADD_NOTIFICATION_REQUEST:
        case actionTypes.CANCEL_NOTIFICATION_REQUEST:
        case actionTypes.FETCH_NOTIFICATIONS_REQUEST:
            return { ...state, isLoading: true, error: null };

        case actionTypes.ADD_NOTIFICATION_SUCCESS:
            return {
                ...state,
                isLoading: false,
                notifications: [...state.notifications, action.payload],
                error: null
            };

        case actionTypes.CANCEL_NOTIFICATION_SUCCESS:
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

        case actionTypes.FETCH_NOTIFICATIONS_SUCCESS:
            return {
                ...state,
                isLoading: false,
                notifications: action.payload,
                error: null
            };

        case actionTypes.ADD_NOTIFICATION_FAILURE:
        case actionTypes.CANCEL_NOTIFICATION_FAILURE:
        case actionTypes.FETCH_NOTIFICATIONS_FAILURE:
            return { ...state, isLoading: false, error: action.payload };

        default:
            return state;
    }
}

export default adminReducer;
