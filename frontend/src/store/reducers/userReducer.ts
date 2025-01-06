import * as actionTypes from '../ActionTypes';
import { UserAction, UserState } from '../types';
import { User } from '../../types';

const initialState: UserState = {
  user: null,
  user_details: null,
  user_medical_details: null,
  error: null,
  isLoading: false,
  isNotificationsLoading: false,
  loggedIn: false,
  notifications: [],
  user_settings: null
};

const userReducer = (
  state: UserState = initialState,
  action: UserAction
): UserState => {
  switch (action.type) {
    // Register Actions
    case actionTypes.REGISTER_USER_REQUEST:
      return { ...state, isLoading: true, error: null };
    case actionTypes.REGISTER_USER_SUCCESS:
      return { ...state, isLoading: false, user: action.payload as User, loggedIn: true, error: null };
    case actionTypes.REGISTER_USER_FAILURE:
      return { ...state, isLoading: false, loggedIn: false, error: action.payload as string };

    // Login Actions
    case actionTypes.LOGIN_REQUEST:
      return { ...state, isLoading: true, error: null };
    case actionTypes.LOGIN_SUCCESS:
      return { ...state, isLoading: false, user: action.payload as User, loggedIn: true, error: null };
    case actionTypes.LOGIN_FAILURE:
      return { ...state, isLoading: false, loggedIn: false, error: action.payload as string };

    // Logout Actions
    case actionTypes.LOGOUT_REQUEST:
      return { ...state, isLoading: true, error: null };
    case actionTypes.LOGOUT_SUCCESS:
      return { ...state, isLoading: false, loggedIn: false, user: null, error: null };
    case actionTypes.LOGOUT_FAILURE:
      return { ...state, isLoading: false, error: action.payload as string };

    // Verify Login Actions
    case actionTypes.VERIFY_LOGIN_REQUEST:
      return { ...state, isLoading: true, error: null };
    case actionTypes.VERIFY_LOGIN_SUCCESS:
      return { ...state, isLoading: false, loggedIn: true, user: action.payload as User, error: null };
    case actionTypes.VERIFY_LOGIN_FAILURE:
      return { ...state, isLoading: false, loggedIn: false, error: action.payload as string };

    // User Details Actions
    case actionTypes.GET_USER_DETAILS_REQUEST:
      return { ...state, isLoading: true, user_details: null, error: null };
    case actionTypes.GET_USER_DETAILS_SUCCESS:
      return { ...state, isLoading: false, user_details: action.payload, error: null };
    case actionTypes.GET_USER_DETAILS_FAILURE:
      return { ...state, isLoading: false, user_details: null, error: action.payload as string };
    case actionTypes.SET_USER_DETAILS_REQUEST:
      return { ...state, isLoading: true, user_details: null, error: null };
    case actionTypes.SET_USER_DETAILS_SUCCESS:
      return { ...state, isLoading: false, user_details: action.payload, error: null };
    case actionTypes.SET_USER_DETAILS_FAILURE:
      return { ...state, isLoading: false, user_details: null, error: action.payload as string };

    // Medical Details Actions
    case actionTypes.GET_USER_MEDICAL_DETAILS_REQUEST:
      return { ...state, isLoading: true, user_medical_details: null, error: null };
    case actionTypes.GET_USER_MEDICAL_DETAILS_SUCCESS:
      return { ...state, isLoading: false, user_medical_details: action.payload, error: null };
    case actionTypes.GET_USER_MEDICAL_DETAILS_FAILURE:
      return { ...state, isLoading: false, user_medical_details: null, error: action.payload as string };
    case actionTypes.SET_USER_MEDICAL_DETAILS_REQUEST:
      return { ...state, isLoading: true, error: null };
    case actionTypes.SET_USER_MEDICAL_DETAILS_SUCCESS:
      return { ...state, isLoading: false, error: null };
    case actionTypes.SET_USER_MEDICAL_DETAILS_FAILURE:
      return { ...state, isLoading: false, error: action.payload as string };

    // User Settings Actions
    case actionTypes.GET_USER_SETTINGS_REQUEST:
      return { ...state, isLoading: true, user_settings: null, error: null };
    case actionTypes.GET_USER_SETTINGS_SUCCESS:
      return { ...state, isLoading: false, user_settings: action.payload, error: null };
    case actionTypes.GET_USER_SETTINGS_FAILURE:
      return { ...state, isLoading: false, user_settings: null, error: action.payload as string };
    case actionTypes.SET_USER_SETTINGS_REQUEST:
      return { ...state, isLoading: true, user_settings: null, error: null };
    case actionTypes.SET_USER_SETTINGS_SUCCESS:
      return { ...state, isLoading: false, user_settings: action.payload, error: null };
    case actionTypes.SET_USER_SETTINGS_FAILURE:
      return { ...state, isLoading: false, user_settings: null, error: action.payload as string };

    // Notifications Actions
    case actionTypes.FETCH_NOTIFICATIONS_REQUEST:
      return { ...state, isNotificationsLoading: true, error: null };
    case actionTypes.FETCH_NOTIFICATIONS_SUCCESS:
      return { ...state, isNotificationsLoading: false, notifications: action.payload as any[], error: null };
    case actionTypes.FETCH_NOTIFICATIONS_FAILURE:
      return { ...state, isNotificationsLoading: false, error: action.payload as string };
    case actionTypes.UPDATE_NOTIFICATION_STATUS_REQUEST:
      return { ...state, isLoading: true, error: null };
    case actionTypes.UPDATE_NOTIFICATION_STATUS_SUCCESS:
      return { ...state, isLoading: false, notifications: action.payload as any[], error: null };
    case actionTypes.UPDATE_NOTIFICATION_STATUS_FAILURE:
      return { ...state, isLoading: false, error: action.payload as string };

    default:
      return state;
  }
};

export default userReducer;
