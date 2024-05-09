import React, { useState, useEffect, useRef } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import * as chatActions from '../../store/actionCreators/chatActionCreators'

import { SubmitButton } from '../../Components/SubmitButton';
import { MessagesContainer } from '../MessagesContainer/';
import styles from './ChatScreen.module.css';

export function ChatScreen() {
    const dispatch = useDispatch();
    const messages = useSelector(state => state.chat.messages);
    const waitingForResponse = useSelector(state => state.chat.waitingForResponse);
    const isChatLoading = useSelector(state => state.chat.isAgentRequestLoading);
    const [question, setQuestion] = useState('');
    const [isInputFocused, setIsFocused] = useState(false)
    const questionInputRef = useRef(null);
    const questionRef = useRef(question)
    const intervalID = useRef(null);
    
    useEffect(() => {
        questionRef.current = question;
    });

    useEffect(() => {
        // Listening for keydown so that I can trigger the Send Action
        window.addEventListener('keydown', handleKeyPress);

        return () => {
            // Clearing Interval and Keyboard listener
            if (intervalID.current) {
                clearInterval(intervalID.current);
                intervalID.current = null;
            }
            window.removeEventListener('keydown', handleKeyPress);
        };
    }, []); // Runs only on mount and unmount


    
    useEffect(() => {

    
        if (waitingForResponse && !intervalID.current) {
            intervalID.current = setInterval(() => {
                dispatch(chatActions.getQuestionAndFacts());
            }, 5000);
        } 
        else if (!waitingForResponse && intervalID.current) {
            clearInterval(intervalID.current);
            intervalID.current = null;
        }

    }, [waitingForResponse]);




    const  handleKeyPress = (event) => {
        if (event && event.key === 'Enter') {

            // Triggering Submit on Key press except if the the user is interacting with the multi select dropdown
            if(event.target && event.target.nodeName != "INPUT" ||  event.target == questionInputRef.current) {
                handleSendMessage()
            }        
        }
    }

    const handleSendMessage = () => {
        const currentQuestion = questionRef.current

        // Check if we have a question and call log docuument paths
        if (!currentQuestion.trim()) return;

        dispatch(chatActions.submitQuestion(currentQuestion))

        // Clearing the input fields
        setQuestion('');
    };

    return (
        <div className={styles.chatContainer}>
            <MessagesContainer messages={messages} showLoader={waitingForResponse}/>

            <div className={styles.chatActionContainer}>
                <div className={styles.formContainer}>
                    <div className={`${styles.questionContainer} ${isInputFocused && styles.focus || ''}`}>
                        <input
                            ref={questionInputRef}
                            type="text"
                            placeholder="Type your question here..."
                            className={styles.questionInput}
                            value={question}
                            onChange={(e) => setQuestion(e.target.value)}
                            onFocus={() => setIsFocused(true)}
                            onBlur={() => setIsFocused(false)}
                        />
                    </div>
                </div>
                <div className={styles.submitBtnContainer}>
                    <SubmitButton
                        onClick={handleSendMessage}
                    />
                </div>
            </div>
        </div>
    );
}

export default ChatScreen;
