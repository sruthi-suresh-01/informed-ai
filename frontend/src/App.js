import './App.css';
import { ChatScreen } from './Containers'; 
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HOCLayout from './Containers/HOCLayout/HOCLayout';
function App() {
  return (
    <Router basename="/informed">
    <HOCLayout>
      <Routes>
          <Route path="/" element={<ChatScreen />} />
        </Routes>

    </HOCLayout>
  </Router>
  );
}


export default App;
