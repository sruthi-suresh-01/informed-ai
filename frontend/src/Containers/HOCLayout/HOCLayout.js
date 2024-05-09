import React from 'react';
import styles from './HOCLayout.module.css';
import Header from '../../Components/Header/Header';
export function HOCLayout(props) {

    return (
        <div className="p-6 max-w-sm mx-auto bg-white rounded-xl shadow-md flex items-center space-x-4">
            <div className={styles.layout}>
                <Header />
                <div className={styles.contentContainer}>
                    {props.children || null}
                </div>
            </div>
        </div>
    );
}

export default HOCLayout;
