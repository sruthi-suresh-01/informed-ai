import * as actionTypes from '../ActionTypes';

export const chatUserMessageRequest = () => {
    return { type: actionTypes.CHAT_USER_MESSAGE_REQUEST };
}

export const chatUserMessageSuccess = (data) => {
    return { type: actionTypes.CHAT_USER_MESSAGE_SUCCESS, ...data };
}

export const chatUserMessageFailure = (error) => {
    return { type: actionTypes.CHAT_USER_MESSAGE_FAILURE, payload: error };
}


export const chatAgentPollRequest = () => {
    return { type: actionTypes.CHAT_AGENT_POLL_REQUEST };
}

export const chatAgentPollSuccess = (payload) => {
    return { type: actionTypes.CHAT_AGENT_POLL_SUCCESS, ...payload };
}

export const chatAgentPollFailure = (error) => {
    return { type: actionTypes.CHAT_AGENT_POLL_FAILURE, payload: error };
}


export const setCurrentChatThreadId = (chatThreadId) => {
    return { type: actionTypes.SET_CURRENT_CHAT_THREAD_ID, chatThreadId };
}
