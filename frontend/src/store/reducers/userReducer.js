import { LOGIN_REQUEST, LOGIN_SUCCESS, LOGIN_FAILURE } from '../ActionTypes';

const initialState = {
  user: null,
  error: null,
  isLoading: false,
};

  
function userReducer(state = initialState, action) {
    switch (action.type) {
        case LOGIN_REQUEST:
        return { ...state, isLoading: true, error: null };
        case LOGIN_SUCCESS:
        return { ...state, isLoading: false, user: action.payload, error: null };
        case LOGIN_FAILURE:
        return { ...state, isLoading: false, error: action.payload };
        default:
        return state;
    }
}

export default userReducer;
  