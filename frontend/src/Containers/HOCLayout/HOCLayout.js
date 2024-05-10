import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import styles from './HOCLayout.module.css';
import Header from '../../Components/Header/Header';
import * as userActions from '../../store/actionCreators/userActionCreators'

export const HOCLayout = React.memo(function HOCLayout(props) {
    const dispatch = useDispatch();
    const user = useSelector(state => state.user.user);
    useEffect(() => {
        if(!user) {
            dispatch(userActions.verifyLogin())
        }
        return () => {
            // Cleanup on App unmount if needed
        };
    }, []);

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
})

export default HOCLayout;
