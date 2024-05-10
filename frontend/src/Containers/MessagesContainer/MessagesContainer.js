import React from 'react';
import { Loader } from '../../Components/Loader';

import styles from './MessagesContainer.module.css';

export function MessagesContainer(props) {
    const {
        messages = [],
        showLoader = false,
    } = props
    return (
        <div className={styles.messagesContainer}>
                {messages.map((message, index) => {
                    if(message) {
                        if(message.type == "question") {
                            return (
                                <div key={index} className={`${styles.message} ${styles.user}`}>
                                    <strong>Question:</strong> 
                                    <p>{message.question}</p>
                                </div>
                            )
                        }
                        else if (message.type == "response" && Array.isArray(message.facts)) {

                            return (
                                <div key={index} className={`${styles.message} ${styles.agent}`}>
                                    <strong>Response:</strong>
                                    {
                                        message.facts.map((fact, factIndex) => (
                                            <p key={factIndex}> {fact}</p>
                                        ))
                                    } 
                                    {message.source && 
                                        <div>
                                            <p><strong>Source: </strong><a style={{'cursor': 'pointer'}}href={message.source}>{message.source}</a></p>
                                        </div>
                                    }
                                    
                                </div>
                            )
                        }
                    }
                })}

                {showLoader && <Loader /> }
                
            </div>
    );
}

export default MessagesContainer;
