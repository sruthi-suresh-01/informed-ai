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
                        if(message.type == "query") {
                            return (
                                <div key={index} className={`${styles.message} ${styles.user}`}>
                                    <strong>Question:</strong>
                                    <p>{message.query}</p>
                                </div>
                            )
                        }
                        else if (message.type == "response" && Array.isArray(message.findings)) {

                            return (
                                <div key={index} className={`${styles.message} ${styles.agent}`}>
                                    <strong>Response:</strong>
                                    {
                                        message.findings.map((fact, factIndex) => (
                                            <p key={factIndex}> {fact}</p>
                                        ))
                                    }
                                    {message.sources && Array.isArray(message.sources) && message.sources.length > 0 && (
                                        <p>
                                            <strong>Source: </strong>
                                            {message.sources.map((source, sourceIndex) => (
                                                <React.Fragment key={sourceIndex}>
                                                    {sourceIndex > 0 && ', '}
                                                    <a style={{'cursor': 'pointer'}} href={source.source}>{source.source}</a>
                                                </React.Fragment>
                                            ))}
                                        </p>
                                    )}
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
