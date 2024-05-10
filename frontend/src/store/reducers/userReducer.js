import * as actionTypes from '../ActionTypes';

const initialState = {
  user: null,
  error: null,
  isLoading: false,
  loggedIn: false
};

  
function userReducer(state = initialState, action) {
    switch (action.type) {
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
        default:
          return state;
    }
}

export default userReducer;
  