import { actions } from '../actions'
import apiClient from '../apiClient';
import { Constants } from "../../Config/Constants";


const api_urls = Constants.apis
const chatActions = actions.chat

export const addUserMessage = (message, chatThreadID=null, responseType="text") => dispatch => {
    dispatch(chatActions.chatUserMessageRequest());
    if(message) {
        let apiUrl = api_urls.addUserMessage
        let payload = {
            message,
            requested_response_type: responseType
        }
        if(chatThreadID) {
            apiUrl = apiUrl + "/" + chatThreadID
            payload["chat_thread_id"] = chatThreadID
        }
        apiClient.post(apiUrl, payload)
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
}

export const getChatThread = (chatThreadId) => dispatch => {
    if (!chatThreadId) {
        // TODO: Raise error here
        return;
    }
    dispatch(chatActions.chatAgentPollRequest());
    apiClient.get(api_urls.getChatThread + "/" + chatThreadId)
        .then(response => {
            const data = response.data
            if (data.error) {
                dispatch(chatActions.chatAgentPollFailure(data.error));
            } else {
                dispatch(chatActions.chatAgentPollSuccess(data));
            }
        })
        .catch(error => {
            console.log("chat error")
            dispatch(chatActions.chatAgentPollFailure(error.message))
        });
}


export const setCurrentChatThreadId = (chatThreadId=null) => dispatch => {
    dispatch(chatActions.setCurrentChatThreadId(chatThreadId));
}
