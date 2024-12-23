import React, { useEffect, useState } from 'react';
import { Loader } from '../../Components/Loader';
import { SupportAgent } from '@mui/icons-material';
import apiClient from '../../store/apiClient';

import styles from './MessagesContainer.module.css';

const AudioPlayer = ({ messageId }) => {
    const [audioUrl, setAudioUrl] = useState(null);

    useEffect(() => {
        const fetchAudio = async () => {
            try {
                const response = await apiClient.blob(`/api/v1/chat/tts/${messageId}`);
                const url = URL.createObjectURL(response.data);
                setAudioUrl(url);
            } catch (error) {
                console.error('Error fetching audio:', error);
            }
        };

        fetchAudio();

        return () => {
            if (audioUrl) {
                URL.revokeObjectURL(audioUrl);
            }
        };
    }, [messageId]);

    return audioUrl ? (
        <audio controls className={styles.audioPlayer} src={audioUrl}>
            Your browser does not support the audio element.
        </audio>
    ) : (
        <div>Loading audio...</div>
    );
};

export function MessagesContainer(props) {
    const {
        messages = [],
        showLoader = false,
    } = props
    return (
        <div className={styles.messagesContainer}>
                {messages.map((message, index) => {
                    if(message) {
                        if(message.source === "webapp") {
                            return (
                                <div key={index} className={`${styles.message} ${styles.user}`}>
                                    <p>{message.content}</p>
                                </div>
                            )
                        }
                        else if (message.source === "assistant" && message.content) {

                            return (
                                <div key={index} className={`${styles.message} ${styles.agent}`}>
                                    <div className={styles.messageHeader}>
                                        <div className={styles.agentIcon}>
                                            <SupportAgent />
                                        </div>
                                        <span className={styles.agentTitle}>Assistant</span>
                                    </div>
                                    {(message.response_type || 'text') === 'audio' ? (
                                        <AudioPlayer messageId={message.message_id} />
                                    ) : (
                                        <>
                                            <p>{message.content}</p>
                                        </>
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
