import { actions } from '../actions'
import apiClient from '../apiClient';
import { Constants } from "../../Config/Constants";


const api_urls = Constants.apis
const chatActions = actions.chat

export const submitQuestion = (question) => dispatch => {
    dispatch(chatActions.chatUserMessageRequest());
    if(question) {
        apiClient.post(api_urls.submit, { question })
            .then(response => {
                const data = response.data;
                if (data.error) {
                    dispatch(chatActions.chatUserMessageFailure(data.error));
                } else {
                    const questionId = data && data.id || ''
                    dispatch(chatActions.chatUserMessageSuccess({ question, questionId }));
                }
            })
            .catch(error => {
                dispatch(chatActions.chatUserMessageFailure(error.message));
            });
    }
}

export const getQuestionAndFacts = () => dispatch => {
    dispatch(chatActions.chatAgentPollRequest());
    apiClient.get(api_urls.generateResponse)
        .then(response => {
            const data = response.data
            if (data.error) {
                dispatch(chatActions.chatAgentPollFailure(data.error));
            } else {
                if (data.status === 'processing') {
                    console.info('Data is still processing, retrying...');
                } else if (data.status === 'done') {
                    console.info('Processing complete');
                    dispatch(chatActions.chatAgentPollSuccess(data));
                }
                
            }
        })
        .catch(error => {
            console.log("chat error")
            dispatch(chatActions.chatAgentPollFailure(error.message))
        });
}


