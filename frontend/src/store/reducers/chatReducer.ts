import * as actionTypes from '../ActionTypes';
import { ChatAction, ChatState } from '../types';

const initialState: ChatState = {
  error: null,
  isLoading: false,
  currentChatThreadId: null,
  waitingForResponse: false,
  messages: []
};

const chatReducer = (
  state: ChatState = initialState,
  action: ChatAction
): ChatState => {
  switch (action.type) {
    case actionTypes.CHAT_USER_MESSAGE_REQUEST:
      return { ...state, isLoading: true, error: null };

    case actionTypes.CHAT_USER_MESSAGE_SUCCESS:
      return {
        ...state,
        isLoading: false,
        waitingForResponse: true,
        currentChatThreadId: action.chat_thread_id || null,
        messages: action.messages || [],
        error: null
      };

    case actionTypes.CHAT_USER_MESSAGE_FAILURE:
      return {
        ...state,
        isLoading: false,
        error: action.payload as string
      };

    case actionTypes.CHAT_AGENT_POLL_REQUEST:
      return { ...state, error: null };

    case actionTypes.CHAT_AGENT_POLL_SUCCESS:
      if (Array.isArray(action.messages) && action.messages.length > state.messages.length) {
        return {
          ...state,
          messages: action.messages,
          currentChatThreadId: action.chat_thread_id || null,
          waitingForResponse: false,
          error: null
        };
      }
      return state;

    case actionTypes.CHAT_AGENT_POLL_FAILURE:
      return {
        ...state,
        waitingForResponse: false,
        error: action.payload as string
      };

    case actionTypes.SET_CURRENT_CHAT_THREAD_ID:
      if (!action.chatThreadId) {
        return {
          ...state,
          currentChatThreadId: null,
          waitingForResponse: false,
          messages: []
        };
      }
      return {
        ...state,
        currentChatThreadId: action.chatThreadId,
        waitingForResponse: true,
        messages: action.resetMessages ? [] : state.messages
      };

    case actionTypes.LOGOUT_SUCCESS:
      return { ...state, messages: [] };

    default:
      return state;
  }
};

export default chatReducer;
