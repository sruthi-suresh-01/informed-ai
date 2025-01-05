import * as actionTypes from '../ActionTypes';

const initialState = {
  user: null,
  error: null,
  isLoading: false,
  isQuestionLoading: false,
  currentChatThreadId: null,
  waitingForResponse: false,
  messages: []
};


function chatReducer(state = initialState, action) {
    switch (action.type) {
        case actionTypes.CHAT_USER_MESSAGE_REQUEST:
            return { ...state, isLoading: true, error: null };
        case actionTypes.CHAT_USER_MESSAGE_SUCCESS:
            return {
                ...state,
                isLoading: false,
                waitingForResponse: true,
                currentChatThreadId: action.chat_thread_id,
                messages: action.messages,
                // messages: [...state.messages, { type: 'query', query: action.query, id: action.query_id }],
                error: null
            };
        case actionTypes.CHAT_USER_MESSAGE_FAILURE:
            return { ...state, isLoading: false, error: action.payload };
        case actionTypes.CHAT_AGENT_POLL_REQUEST:
            return { ...state, error: null };
        case actionTypes.CHAT_AGENT_POLL_SUCCESS:
            if (Array.isArray(action.messages) && action.messages.length > state.messages.length) {
                return {
                    ...state,
                    messages: action.messages,
                    currentChatThreadId: action.chat_thread_id,
                    waitingForResponse: false,
                    error: null
                }
            }
            return state;
        case actionTypes.CHAT_AGENT_POLL_FAILURE:
            return { ...state, waitingForResponse: false, error: action.payload };

        case actionTypes.SET_CURRENT_CHAT_THREAD_ID:
            if(!action.chatThreadId) {
                return { ...state, currentChatThreadId: null, waitingForResponse: false, messages: [] };
            }
            let messages = action.resetMessages ? [] : state.messages;
            return { ...state, currentChatThreadId: action.chatThreadId, waitingForResponse: true, messages: messages };
        case actionTypes.LOGOUT_SUCCESS:
            return { ...state, messages: [] };
        default:
        return state;
    }
}

export default chatReducer;
