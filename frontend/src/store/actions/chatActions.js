import * as actionTypes from '../ActionTypes';

export const chatUserMessageRequest = () => {
    return { type: actionTypes.CHAT_USER_MESSAGE_REQUEST };
}

export const chatUserMessageSuccess = ({ question, questionId }) => {
    return { type: actionTypes.CHAT_USER_MESSAGE_SUCCESS, question, questionId };
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

