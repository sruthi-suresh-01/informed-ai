import React, { useState, useEffect, useRef } from 'react';
import { SubmitButton } from '../../Components/SubmitButton';
import { CustomSelect } from '../../Components/CustomSelect/CustomSelect';
import { MessagesContainer } from '../MessagesContainer/';
import styles from './ChatScreen.module.css';
import { submitQuestion, getQuestionAndFacts } from '../../APIs';

const user_profiles = {
    'user_1' : 'Rahul | English | Healthy',
    'user_2' : 'Rahul | English | Asthma',
    'user_3' : 'Raúl | Spanish | Asthma'
}

export function ChatScreen() {
    const [messages, setMessages] = useState([]);
    const [question, setQuestion] = useState('');
    const [waitingForResponse, setResponseState] = useState(false)
    const [userId, setUserId] = useState('')
    const [isInputFocused, setIsFocused] = useState(false)
    const questionInputRef = useRef(null);
    const questionRef = useRef(question)
    const selectedUserIdRef = useRef(userId)
    let intervalID = null
    
    useEffect(() => {
        questionRef.current = question;
        selectedUserIdRef.current = userId; 
    });

    useEffect(() => {
        // Listening for keydown so that I can trigger the Send Action
        window.addEventListener('keydown', handleKeyPress);

        return () => {
            // Clearing Interval and Keyboard listener
            clearInterval(intervalID)
            window.removeEventListener('keydown', handleKeyPress);
        };
    }, []); // Runs only on mount and unmount

    const updateMessagesFromResponse = () => {
        try {
            getQuestionAndFacts().then(response => {
            
                setMessages(currentMessages => {
    
                    // Access the last question asked by the user
                    const lastMessage = currentMessages.length > 0 ? currentMessages[currentMessages.length - 1] : null;
    
                    // if The response recieved is for the last question (handling just in case), only then display the response
                    if (response && response.status === "done" && lastMessage && lastMessage.question  && lastMessage.question === response.question) {
    
                        // Stop polling for response
                        clearInterval(intervalID);
                        setResponseState(false);
    
                        return [...currentMessages, {
                            question: response.question,
                            facts: response.facts,
                            type: "response"
                        }];
                    } else if (response && response.status == "error") {
                        // Stop polling for response
                        clearInterval(intervalID);
                        setResponseState(false);
                    }
                    return currentMessages; // Return current state if no updates are necessary
                });
            }).catch(error => {
                console.error("Failed to get question and facts:", error);
            });
        }
        catch {
            console.error("Failed to get question and facts");
        }
        
    };

    // Checks for messages at a certain interval if it is expecting a message
    const pollForResponse = () => {
        clearInterval(intervalID)
        intervalID = setInterval(updateMessagesFromResponse, 5000)
    }

    useEffect(() => {
        console.info(`Waiting for response: ${waitingForResponse}`);
        // Poll for response if we are expecting one
        if(waitingForResponse) {
            clearInterval(intervalID)
            pollForResponse()
        }      
        return () => {
            clearInterval(intervalID)
        };
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
        const selectedUser = selectedUserIdRef.current

        // Check if we have a question and call log docuument paths
        if (!currentQuestion.trim() || !selectedUser.length) return;

        setMessages(currentMessages => [
            ...currentMessages,
            {
                question: currentQuestion,
                type: 'question'
            }
        ]);

        submitQuestion(currentQuestion, selectedUser);
        
        // Set a state to indicate that we are waiting for a response
        setResponseState(true); 

        // Clearing the input fields
        setQuestion('');
        setUserId('')
    };

    return (
        <div className={styles.chatContainer}>
            <div className={styles.bannerContainer}>
                <p>
                    Informed
                </p>
            </div>

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
                    <div className={styles.linksContainer}>
                        <CustomSelect
                            isMulti={false}
                            value={{ label : user_profiles[userId], value: userId}}
                            onChange={(selectedOption) => {
                                if(selectedOption && selectedOption.value) {
                                    setUserId(selectedOption.value)
                                }
                        
                            }}
                            options={
                                Object.keys(user_profiles).map((u_id) => ({ label : user_profiles[u_id], value: u_id }))}

                            placeholder="Select User"
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
