import React, { useState, useEffect } from 'react';
import styles from './LoginModal.module.css';
import { useDispatch, useSelector } from 'react-redux';
import * as userActions from '../../store/actionCreators/userActionCreators'
import LoginDialog from './LoginDialog';
import DialogWrapper from '../DialogWrapper/DialogWrapper';



const AuthComponent = () => {
  const dispatch = useDispatch();
  const user = useSelector(state => state.user.user)
  const isLoggedIn = useSelector(state => state.user.loggedIn)

  const displayName = (user && user.details && user.details.first_name && user.details.last_name &&  `${user.details.first_name} ${user.details.last_name}`) || ''

  const [isRegistering, setIsRegistering] = useState(false);
  const [isDialogOpen, setIsDialogOpen] = useState(false);

  const handleOpenDialog = () => {
    setIsDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setIsDialogOpen(false);
  };

  const handleLogin = (loginDetails) => {
    console.log('Login Details:', loginDetails);
    dispatch(userActions.login({ ...loginDetails }))
    // Handle login logic here
  };

  const handleRegister = (registerDetails) => {
    console.log('Register Details:', registerDetails);
    dispatch(userActions.registerUser({ ...registerDetails }))
    // Handle registration logic here
  };

  const handleLogout = () => {
    dispatch(userActions.logout())
  };

  return (
    <div className={styles.AuthComponent}>
        <div className={styles.loginlogoutContainer}>
            {isLoggedIn ? (
            <button className={styles.close} onClick={handleLogout}>Logout</button>
            ) : (
                <button className={styles.loginButton} onClick={handleOpenDialog}>Login</button>
            )}
        </div>

        {
        isLoggedIn &&
            <div className={styles.loggedInMsg}><p>Welcome, {displayName}!</p></div>
        }

      <LoginDialog
        open={isDialogOpen}
        onClose={handleCloseDialog}
        onLogin={handleLogin}
        onRegister={handleRegister}
      />
      {/* <DialogWrapper
            open={isDialogOpen}
            title={'Login'}
            actions={[
                {
                    type: "primary",
                    text: "Cancel",
                    invoke: () => {
                        handleDialogClose()
                    }
                },
                {
                    type: "primary",
                    text: "Login",
                    invoke: () => {
                        showNotification({ severity: 'success', message: "Logged in successfully" });
                        handleDialogClose()
                    }
                },
            ]}
        >

        </DialogWrapper> */}
    </div>
  );
};



// const LoginModal = ({ onClose }) => {

//   const dispatch = useDispatch();
//   const user = useSelector(state => state.user.user);
//   const [username, setUsername] = useState('');
//   const [password, setPassword] = useState('');

//   const handleLogin = () => {
//     dispatch(userActions.login({ username }))
//     setUsername('');
//     setPassword('')
//   };

//   useEffect(() => {
//     // console.info(`Waiting for response: ${waitingForResponse}`);
//     if(user && user.username) {
//       onClose();
//     }

//     return () => {
//         // clearInterval(intervalID)
//     };
// }, [user]);

//   return (
//     <div className={styles.modal}>
//       <div className={styles.modalContent}>

//         <div className={styles.loginModalHeading}>
//             <p>Enter User Details</p>
//             <div className={styles.closeButtonContainer} onClick={onClose}>
//                 x
//             </div>
//         </div>

//         <div className={styles.loginActionsContainer}>
//           <div className={styles.loginFormContainer}>
//             <div className={styles.userNameInputContainer}>
//                 <input
//                 type="text"
//                 placeholder="Username"
//                 value={username}
//                 onChange={(e) => setUsername(e.target.value)}
//                 className={styles.userNameInput}
//                 />
//             </div>
//             <div className={styles.passwordInputContainer}>
//                 <input
//                 type="password"
//                 placeholder="Password"
//                 value={password}
//                 onChange={(e) => setPassword(e.target.value)}
//                 className={styles.userNameInput}
//                 />
//             </div>
//           </div>
//             <div className={styles.usernameSubmitContainer}>
//                 <button className={styles.usernameSubmit} onClick={handleLogin}>Login</button>
//             </div>

//         </div>

//       </div>
//     </div>
//   );
// };

// const AuthComponent = () => {
//   const dispatch = useDispatch();
//   const user = useSelector(state => state.user.user)
//   const isLoggedIn = useSelector(state => state.user.loggedIn)
//   const [showModal, setShowModal] = useState(false);
//   const displayName = (user && user.details && user.details.first_name && user.details.last_name &&  `${user.details.first_name} ${user.details.last_name}`) || ''


//   const handleLogout = () => {
//     dispatch(userActions.logout())
//   };

//   return (
//     <div className={styles.AuthComponent}>
//         <div className={styles.loginlogoutContainer}>
//             {isLoggedIn ? (
//             <button className={styles.close} onClick={handleLogout}>Logout</button>
//             ) : (
//                 <button className={styles.loginButton} onClick={() => setShowModal(true)}>Login</button>
//             )}
//         </div>

//         {
//         isLoggedIn &&
//             <div className={styles.loggedInMsg}><p>Welcome, {displayName}!</p></div>
//         }

//         {showModal && (
//         <LoginModal
//             onClose={() => setShowModal(false)}
//         />
//         )}
//     </div>
//   );
// };

export default AuthComponent;
