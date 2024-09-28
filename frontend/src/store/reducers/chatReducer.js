import * as actionTypes from '../ActionTypes';

const initialState = {
  user: null,
  error: null,
  isLoading: false,
  isQuestionLoading: false,
  isAgentRequestLoading: false,
  waitingForResponse: false,
  messages: []
};

  
function chatReducer(state = initialState, action) {
    switch (action.type) {
        case actionTypes.CHAT_USER_MESSAGE_REQUEST:
            return { ...state, isLoading: true, error: null };
        case actionTypes.CHAT_USER_MESSAGE_SUCCESS:
            return { ...state, isLoading: false, waitingForResponse: true, messages: [...state.messages, { type: 'question', question: action.question, id: action.questionId }], error: null };
        case actionTypes.CHAT_USER_MESSAGE_FAILURE:
            return { ...state, isLoading: false, error: action.payload };
        case actionTypes.CHAT_AGENT_POLL_REQUEST:
            return { ...state, isAgentRequestLoading: true, error: null };
        case actionTypes.CHAT_AGENT_POLL_SUCCESS:
            let messages = state.messages
            if(state.waitingForResponse)
                messages = [...messages, { type: 'response', facts: action.facts, questionId : action.questionId, source: action.source }]
            return { ...state, isAgentRequestLoading: false, waitingForResponse: false, messages: messages, error: null };
        case actionTypes.CHAT_AGENT_POLL_FAILURE:
            return { ...state, isAgentRequestLoading: false, waitingForResponse: false, error: action.payload };

        case actionTypes.LOGOUT_SUCCESS:
            return { ...state, messages: [] };
        default:
        return state;
    }
}

export default chatReducer;
  