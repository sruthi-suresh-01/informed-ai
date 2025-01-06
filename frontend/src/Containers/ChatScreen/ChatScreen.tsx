import React, { useState, useEffect, useRef } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate, useLocation } from 'react-router-dom';
import * as chatActions from '../../store/actionCreators/chatActionCreators';
import { RootState } from '../../store/types';
import { AppDispatch } from '../../store/store';
import {
    ResponseTypeSelector,
    MESSAGE_RESPONSE_TYPES,
    type MessageResponseType
} from './ResponseTypeSelector';

import { SubmitButton } from '../../Components/SubmitButton';
import { MessagesContainer } from '../MessagesContainer/';
import styles from './ChatScreen.module.css';

export const ChatScreen: React.FC = () => {
    const dispatch = useDispatch<AppDispatch>();
    const messages = useSelector((state: RootState) => state.chat.messages);
    const waitingForResponse = useSelector((state: RootState) => state.chat.waitingForResponse);
    const currentChatThreadId = useSelector((state: RootState) => state.chat.currentChatThreadId);
    const [messageResponseType, setMessageResponseType] = useState<MessageResponseType>(MESSAGE_RESPONSE_TYPES.TEXT);
    const [query, setQuery] = useState('');
    const [isInputFocused, setIsFocused] = useState(false);
    const questionInputRef = useRef<HTMLInputElement>(null);
    const queryRef = useRef(query);
    const intervalID = useRef<NodeJS.Timeout | null>(null);
    const navigate = useNavigate();
    const location = useLocation();

    useEffect(() => {
        const params = new URLSearchParams(location.search);
        const id = params.get('id');
        if (id) {
            dispatch(chatActions.setCurrentChatThreadId(id, true));
        } else {
            dispatch(chatActions.setCurrentChatThreadId(null));
        }
    }, [location.search, dispatch]);

    useEffect(() => {
        if (currentChatThreadId) {
            const newUrl = new URL(window.location.href);
            newUrl.searchParams.set('id', currentChatThreadId);
            window.history.replaceState({}, '', newUrl);
        }
    }, [currentChatThreadId]);

    useEffect(() => {
        queryRef.current = query;
    });

    useEffect(() => {
        const handleKeyPress = (event: KeyboardEvent) => {
            if (event.key === 'Enter') {
                if (event.target instanceof HTMLElement && event.target === questionInputRef.current) {
                    handleSendMessage();
                }
            }
        };

        window.addEventListener('keydown', handleKeyPress);

        return () => {
            if (intervalID.current) {
                clearInterval(intervalID.current);
                intervalID.current = null;
            }
            window.removeEventListener('keydown', handleKeyPress);
        };
    }, [currentChatThreadId, messageResponseType]);

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
    }, [waitingForResponse, currentChatThreadId, dispatch]);

    const handleSendMessage = () => {
        const currentQuery = queryRef.current;

        if (!currentQuery.trim()) return;

        dispatch(chatActions.addUserMessage(currentQuery, currentChatThreadId, messageResponseType));
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
                    <div className={`${styles.questionContainer} ${isInputFocused ? styles.focus : ''}`}>
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
                    <SubmitButton onClick={handleSendMessage} />
                </div>
            </div>
        </div>
    );
};

export default ChatScreen;
