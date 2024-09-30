import { actions } from '../actions'
import apiClient from '../apiClient';
import { Constants } from "../../Config/Constants";


const api_urls = Constants.apis
const chatActions = actions.chat

export const submitQuestion = (query) => dispatch => {
    dispatch(chatActions.chatUserMessageRequest());
    if(query) {
        apiClient.post(api_urls.submit, { query })
            .then(response => {
                const data = response.data;
                if (data.error) {
                    dispatch(chatActions.chatUserMessageFailure(data.error));
                } else {
                    const queryId = data && data.id || ''
                    dispatch(chatActions.chatUserMessageSuccess({ query, queryId }));
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
                if (data.state != 'completed') {
                    console.info('Data is still processing, retrying...');
                } else {
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
