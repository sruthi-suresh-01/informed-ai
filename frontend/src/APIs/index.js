import { Constants } from "../Config/Constants";

const api_urls = Constants.apis
export function submitQuestion(question, userId) {
    const apiUrl = api_urls.submit;

    const data = {
        question, user_id : userId
    };
    
    try {
        fetch(apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok'); // TODO: Handle gracefully
            }
            return response.json(); 
        })
        .then(data => {
            return data
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }
    catch {
        console.error("API Error")

    }

    
}

export function getQuestionAndFacts() {
    const apiUrl = api_urls.generateResponse;
    return fetch(apiUrl)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'processing') {
                console.info('Data is still processing, retrying...');
            } else if (data.status === 'done') {
                console.info('Processing complete');
            }
            return data
        })
        .catch(error => {
            console.error('Error polling the API:', error)
            return { status : "error" }
        });
}

