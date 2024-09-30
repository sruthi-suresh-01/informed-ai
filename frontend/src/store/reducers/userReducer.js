import * as actionTypes from '../ActionTypes';

const initialState = {
  user: null,
  user_details: {},
  user_medical_details: {},
  error: null,
  isLoading: false,
  loggedIn: false
};


function userReducer(state = initialState, action) {
    switch (action.type) {
        case actionTypes.REGISTER_USER_REQUEST:
          return { ...state, isLoading: true, error: null };
        case actionTypes.REGISTER_USER_SUCCESS:
          return { ...state, isLoading: false, user: action.payload, loggedIn: true, error: null };
        case actionTypes.REGISTER_USER_FAILURE:
          return { ...state, isLoading: false, loggedIn: false, error: action.payload };
        case actionTypes.LOGIN_REQUEST:
          return { ...state, isLoading: true, error: null };
        case actionTypes.LOGIN_SUCCESS:
          return { ...state, isLoading: false, user: action.payload, loggedIn: true, error: null };
        case actionTypes.LOGIN_FAILURE:
          return { ...state, isLoading: false, loggedIn: false, error: action.payload };
        case actionTypes.LOGOUT_REQUEST:
          return { ...state, isLoading: true, error: null };
        case actionTypes.LOGOUT_SUCCESS:
          return { ...state, isLoading: false, loggedIn: false, user: null, error: null };
        case actionTypes.LOGIN_FAILURE:
          return { ...state, isLoading: false, error: action.payload };
        case actionTypes.VERIFY_LOGIN_REQUEST:
          return { ...state, isLoading: true, error: null };
        case actionTypes.VERIFY_LOGIN_SUCCESS:
          return { ...state, isLoading: false, loggedIn: true, user: action.payload, error: null };
        case actionTypes.VERIFY_LOGIN_FAILURE:
          return { ...state, isLoading: false, loggedIn: false, error: action.payload };

        //
        case actionTypes.GET_USER_DETAILS_REQUEST:
          return { ...state, isLoading: true, user_details: {}, error: null };
        case actionTypes.GET_USER_DETAILS_SUCCESS:
          return { ...state, isLoading: false, user_details: action.payload, error: null };
        case actionTypes.GET_USER_DETAILS_FAILURE:
          return { ...state, isLoading: false, user_details: {},  error: action.payload };
        case actionTypes.SET_USER_DETAILS_REQUEST:
          return { ...state, isLoading: true, user_details: {}, error: null };
        case actionTypes.SET_USER_DETAILS_SUCCESS:
          return { ...state, isLoading: false, user_details: action.payload, error: null };
        case actionTypes.SET_USER_DETAILS_FAILURE:
          return { ...state, isLoading: false, user_details: {}, error: action.payload };

        //
        case actionTypes.GET_USER_MEDICAL_DETAILS_REQUEST:
          return { ...state, isLoading: true, user_medical_details: {}, error: null };
        case actionTypes.GET_USER_MEDICAL_DETAILS_SUCCESS:
          return { ...state, isLoading: false, user_medical_details: action.payload, error: null };
        case actionTypes.GET_USER_MEDICAL_DETAILS_FAILURE:
          return { ...state, isLoading: false, user_medical_details: {},  error: action.payload };
        case actionTypes.SET_USER_MEDICAL_DETAILS_REQUEST:
          return { ...state, isLoading: true, user_medical_details: {}, error: null };
        case actionTypes.SET_USER_MEDICAL_DETAILS_SUCCESS:
          return { ...state, isLoading: false, user_medical_details: action.payload, error: null };
        case actionTypes.SET_USER_MEDICAL_DETAILS_FAILURE:
          return { ...state, isLoading: false, user_medical_details: {}, error: action.payload };
        default:
          return state;
    }
}

export default userReducer;
