import React, { useState, useEffect, useRef } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import * as chatActions from '../../store/actionCreators/chatActionCreators'
import { useNavigate, useLocation } from 'react-router-dom';

import { SubmitButton } from '../../Components/SubmitButton';
import { MessagesContainer } from '../MessagesContainer/';
import styles from './ChatScreen.module.css';
import { ResponseTypeSelector, MESSAGE_RESPONSE_TYPES } from './ResponseTypeSelector';

export function ChatScreen() {
    const dispatch = useDispatch();
    const messages = useSelector(state => state.chat.messages);
    const waitingForResponse = useSelector(state => state.chat.waitingForResponse);
    const currentChatThreadId = useSelector(state => state.chat.currentChatThreadId);
    const [messageResponseType, setMessageResponseType] = useState(MESSAGE_RESPONSE_TYPES.TEXT);
    const [query, setQuery] = useState('');
    const [isInputFocused, setIsFocused] = useState(false)
    const questionInputRef = useRef(null);
    const queryRef = useRef(query)
    const intervalID = useRef(null);
    const navigate = useNavigate();
    const location = useLocation();

    useEffect(() => {
        const params = new URLSearchParams(location.search);
        const id = params.get('id');
        if (id) {
            dispatch(chatActions.setCurrentChatThreadId(id));
        } else {
            dispatch(chatActions.setCurrentChatThreadId(null));
        }
    }, []);

    useEffect(() => {
        if (currentChatThreadId) {
            navigate(`?id=${currentChatThreadId}`, { replace: true });
        } else {
            navigate('', { replace: true });
        }
    }, [currentChatThreadId]);

    useEffect(() => {
        queryRef.current = query;
    });

    useEffect(() => {
        const handleKeyPress = (event) => {
            if (event && event.key === 'Enter') {
                if(event.target && event.target == questionInputRef.current) {
                    handleSendMessage()
                }
            }
        }

        window.addEventListener('keydown', handleKeyPress);

        return () => {
            if (intervalID.current) {
                clearInterval(intervalID.current);
                intervalID.current = null;
            }
            window.removeEventListener('keydown', handleKeyPress);
        };
    }, [currentChatThreadId, messageResponseType])

    useEffect(() => {
        if (waitingForResponse && !intervalID.current) {
            dispatch(chatActions.getChatThread(currentChatThreadId));

            intervalID.current = setInterval(() => {
                dispatch(chatActions.getChatThread(currentChatThreadId));
            }, 5000);
        }
        else if (!waitingForResponse && intervalID.current) {
            clearInterval(intervalID.current);
            intervalID.current = null;
        }

    }, [waitingForResponse]);

    const handleSendMessage = () => {
        const currentQuery = queryRef.current

        // Check if we have a question and call log document paths
        if (!currentQuery.trim()) return;

        dispatch(chatActions.addUserMessage(currentQuery, currentChatThreadId, messageResponseType))

        // Clearing the input fields
        setQuery('');
    };

    return (
        <div className={styles.chatContainer}>
            <MessagesContainer messages={messages} showLoader={waitingForResponse}/>

            <div className={styles.chatActionContainer}>
                <div className={styles.responseTypeSelectorContainer}>
                    <ResponseTypeSelector
                        currentType={messageResponseType}
                        onTypeChange={setMessageResponseType}
                    />
                </div>
                <div className={styles.formContainer}>
                    <div className={`${styles.questionContainer} ${isInputFocused && styles.focus || ''}`}>
                        <input
                            ref={questionInputRef}
                            type="text"
                            placeholder="Type your question here..."
                            className={styles.questionInput}
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
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
