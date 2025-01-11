import { Dispatch } from 'redux';
import { actions } from '../actions';
import apiClient from '../apiClient';
import { Constants } from "../../Config/Constants";
import { ChatAction } from '../types';
import { ResponseType } from '../../types';
import { ApiChatResponse, ApiChatMessageInput } from './types';
import { transformRequestToSnakeCase, transformResponseToCamelCase } from '../../utils/apiUtils';

const api_urls = Constants.apis;
const chatActions = actions.chat;

interface ApiResponse<T> {
  data: T;
  error?: string;
}

export const addUserMessage = (
  message: string,
  chatThreadId: string | null = null,
  responseType: ResponseType = "text"
) => (dispatch: Dispatch<ChatAction>) => {
  dispatch(chatActions.chatUserMessageRequest());

  if (message) {
    let apiUrl = api_urls.addUserMessage;
    const payload: ApiChatMessageInput = {
      message,
      requestedResponseType: responseType
    };

    if (chatThreadId) {
      apiUrl = `${apiUrl}/${chatThreadId}`;
      payload.chatThreadId = chatThreadId;
    }

    const apiPayload = transformRequestToSnakeCase(payload);
    apiClient.post<ApiResponse<ApiChatResponse>>(apiUrl, apiPayload)
      .then(response => {
        const data = response.data;
        const transformedData = transformResponseToCamelCase(data);
        dispatch(chatActions.chatUserMessageSuccess(transformedData));
      })
      .catch(error => {
        dispatch(chatActions.chatUserMessageFailure(error.message));
      });
  }
};

export const getChatThread = (chatThreadId: string) => (dispatch: Dispatch<ChatAction>) => {
  dispatch(chatActions.chatAgentPollRequest());

  apiClient.get<ApiResponse<ApiChatResponse>>(`${api_urls.getChatThread}/${chatThreadId}`)
    .then(response => {
      const data = response.data;
      const transformedData = transformResponseToCamelCase(data);
      dispatch(chatActions.chatAgentPollSuccess(transformedData));
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
