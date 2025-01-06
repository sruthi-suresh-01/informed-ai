import { Dispatch } from 'redux';
import { actions } from '../actions';
import apiClient from '../apiClient';
import { Constants } from "../../Config/Constants";
import { ChatAction } from '../types';
import { Message, ResponseType } from '../../types';
const api_urls = Constants.apis;
const chatActions = actions.chat;

interface ChatMessageInput {
  message: string;
  requested_response_type: ResponseType;
  chat_thread_id?: string | null;
}

interface ApiResponse<T> {
  data: T;
  error?: string;
}

interface ChatResponse {
  chat_thread_id: string;
  messages: Message[];
}

export const addUserMessage = (
  message: string,
  chatThreadID: string | null = null,
  responseType: ResponseType = "text"
) => (dispatch: Dispatch<ChatAction>) => {
  dispatch(chatActions.chatUserMessageRequest());

  if (message) {
    let apiUrl = api_urls.addUserMessage;
    const payload: ChatMessageInput = {
      message,
      requested_response_type: responseType
    };

    if (chatThreadID) {
      apiUrl = `${apiUrl}/${chatThreadID}`;
      payload.chat_thread_id = chatThreadID;
    }

    apiClient.post<ApiResponse<ChatResponse>>(apiUrl, payload)
      .then(response => {
        const data = response.data;
        if (data.error) {
          dispatch(chatActions.chatUserMessageFailure(data.error));
        } else {
          dispatch(chatActions.chatUserMessageSuccess(data));
        }
      })
      .catch(error => {
        dispatch(chatActions.chatUserMessageFailure(error.message));
      });
  }
};

export const getChatThread = (chatThreadId: string) => (dispatch: Dispatch<ChatAction>) => {
  if (!chatThreadId) {
    // TODO: Raise error here
    return;
  }
  dispatch(chatActions.chatAgentPollRequest());

  apiClient.get<ApiResponse<ChatResponse>>(`${api_urls.getChatThread}/${chatThreadId}`)
    .then(response => {
      const data = response.data;
      if (data.error) {
        dispatch(chatActions.chatAgentPollFailure(data.error));
      } else {
        dispatch(chatActions.chatAgentPollSuccess(data));
      }
    })
    .catch(error => {
      dispatch(chatActions.chatAgentPollFailure(error.message));
    });
};

export const setCurrentChatThreadId = (
  chatThreadId: string | null = null,
  resetMessages = false
) => (dispatch: Dispatch<ChatAction>) => {
  dispatch(chatActions.setCurrentChatThreadId(chatThreadId, resetMessages));
};
