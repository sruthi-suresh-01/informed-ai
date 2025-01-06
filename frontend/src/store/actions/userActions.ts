import * as actionTypes from '../ActionTypes';
import { UserAction } from '../types';
import { User } from '../../types';

export const registerUserRequest = (): UserAction => ({
  type: actionTypes.REGISTER_USER_REQUEST
});

export const registerUserSuccess = (user: User): UserAction => ({
  type: actionTypes.REGISTER_USER_SUCCESS,
  payload: user
});

export const registerUserFailure = (error: string): UserAction => ({
  type: actionTypes.REGISTER_USER_FAILURE,
  payload: error
});

export const loginRequest = (): UserAction => ({
  type: actionTypes.LOGIN_REQUEST
});

export const loginSuccess = (user: User): UserAction => ({
  type: actionTypes.LOGIN_SUCCESS,
  payload: user
});

export const loginFailure = (error: string): UserAction => ({
  type: actionTypes.LOGIN_FAILURE,
  payload: error
});

export const logoutRequest = (): UserAction => ({
  type: actionTypes.LOGOUT_REQUEST
});

export const logoutSuccess = (data: any): UserAction => ({
  type: actionTypes.LOGOUT_SUCCESS,
  payload: data
});

export const logoutFailure = (error: string): UserAction => ({
  type: actionTypes.LOGOUT_FAILURE,
  payload: error
});

export const verifyLoginRequest = (): UserAction => ({
  type: actionTypes.VERIFY_LOGIN_REQUEST
});

export const verifyLoginSuccess = (user: User): UserAction => ({
  type: actionTypes.VERIFY_LOGIN_SUCCESS,
  payload: user
});

export const verifyLoginFailure = (error: string): UserAction => ({
  type: actionTypes.VERIFY_LOGIN_FAILURE,
  payload: error
});

export const getUserDetailsRequest = (): UserAction => ({
  type: actionTypes.GET_USER_DETAILS_REQUEST
});

export const getUserDetailsSuccess = (details: any): UserAction => ({
  type: actionTypes.GET_USER_DETAILS_SUCCESS,
  payload: details
});

export const getUserDetailsFailure = (error: string): UserAction => ({
  type: actionTypes.GET_USER_DETAILS_FAILURE,
  payload: error
});

export const setUserDetailsRequest = (): UserAction => ({
  type: actionTypes.SET_USER_DETAILS_REQUEST
});

export const setUserDetailsSuccess = (details: any): UserAction => ({
  type: actionTypes.SET_USER_DETAILS_SUCCESS,
  payload: details
});

export const setUserDetailsFailure = (error: string): UserAction => ({
  type: actionTypes.SET_USER_DETAILS_FAILURE,
  payload: error
});

export const getUserMedicalDetailsRequest = (): UserAction => ({
  type: actionTypes.GET_USER_MEDICAL_DETAILS_REQUEST
});

export const getUserMedicalDetailsSuccess = (details: any): UserAction => ({
  type: actionTypes.GET_USER_MEDICAL_DETAILS_SUCCESS,
  payload: details
});

export const getUserMedicalDetailsFailure = (error: string): UserAction => ({
  type: actionTypes.GET_USER_MEDICAL_DETAILS_FAILURE,
  payload: error
});

export const setUserMedicalDetailsRequest = (): UserAction => ({
  type: actionTypes.SET_USER_MEDICAL_DETAILS_REQUEST
});

export const setUserMedicalDetailsSuccess = (details: any): UserAction => ({
  type: actionTypes.SET_USER_MEDICAL_DETAILS_SUCCESS,
  payload: details
});

export const setUserMedicalDetailsFailure = (error: string): UserAction => ({
  type: actionTypes.SET_USER_MEDICAL_DETAILS_FAILURE,
  payload: error
});

export const getUserSettingsRequest = (): UserAction => ({
  type: actionTypes.GET_USER_SETTINGS_REQUEST
});

export const getUserSettingsSuccess = (settings: any): UserAction => ({
  type: actionTypes.GET_USER_SETTINGS_SUCCESS,
  payload: settings
});

export const getUserSettingsFailure = (error: string): UserAction => ({
  type: actionTypes.GET_USER_SETTINGS_FAILURE,
  payload: error
});

export const setUserSettingsRequest = (): UserAction => ({
  type: actionTypes.SET_USER_SETTINGS_REQUEST
});

export const setUserSettingsSuccess = (settings: any): UserAction => ({
  type: actionTypes.SET_USER_SETTINGS_SUCCESS,
  payload: settings
});

export const setUserSettingsFailure = (error: string): UserAction => ({
  type: actionTypes.SET_USER_SETTINGS_FAILURE,
  payload: error
});

export const fetchNotificationsRequest = (): UserAction => ({
  type: actionTypes.FETCH_NOTIFICATIONS_REQUEST
});

export const fetchNotificationsSuccess = (notifications: any[]): UserAction => ({
  type: actionTypes.FETCH_NOTIFICATIONS_SUCCESS,
  payload: notifications
});

export const fetchNotificationsFailure = (error: string): UserAction => ({
  type: actionTypes.FETCH_NOTIFICATIONS_FAILURE,
  payload: error
});

export const updateNotificationStatusRequest = (): UserAction => ({
  type: actionTypes.UPDATE_NOTIFICATION_STATUS_REQUEST
});

export const updateNotificationStatusSuccess = (notifications: any[]): UserAction => ({
  type: actionTypes.UPDATE_NOTIFICATION_STATUS_SUCCESS,
  payload: notifications
});

export const updateNotificationStatusFailure = (error: string): UserAction => ({
  type: actionTypes.UPDATE_NOTIFICATION_STATUS_FAILURE,
  payload: error
});
