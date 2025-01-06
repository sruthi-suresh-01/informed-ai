import * as actionTypes from '../ActionTypes';
import { ChatAction } from '../types';

export const chatUserMessageRequest = (): ChatAction => ({
  type: actionTypes.CHAT_USER_MESSAGE_REQUEST
});

export const chatUserMessageSuccess = (data: any): ChatAction => ({
  type: actionTypes.CHAT_USER_MESSAGE_SUCCESS,
  ...data
});

export const chatUserMessageFailure = (error: string): ChatAction => ({
  type: actionTypes.CHAT_USER_MESSAGE_FAILURE,
  payload: error
});

export const chatAgentPollRequest = (): ChatAction => ({
  type: actionTypes.CHAT_AGENT_POLL_REQUEST
});

export const chatAgentPollSuccess = (payload: any): ChatAction => ({
  type: actionTypes.CHAT_AGENT_POLL_SUCCESS,
  ...payload
});

export const chatAgentPollFailure = (error: string): ChatAction => ({
  type: actionTypes.CHAT_AGENT_POLL_FAILURE,
  payload: error
});

export const setCurrentChatThreadId = (
  chatThreadId: string | null,
  resetMessages = false
): ChatAction => ({
  type: actionTypes.SET_CURRENT_CHAT_THREAD_ID,
  chatThreadId,
  resetMessages
});
