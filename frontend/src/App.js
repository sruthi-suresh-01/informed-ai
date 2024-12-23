import './App.css';
import { ChatScreen, Admin } from './Containers';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import HOCLayout from './Containers/HOCLayout/HOCLayout';

function App() {
  return (
    <Router>
      <HOCLayout>
        <Routes>
            <Route path="/" element={<Navigate to="/chat" replace />} />
            <Route path="/chat" element={<ChatScreen />} />
            <Route path="/admin" element={<Admin />} />
        </Routes>
      </HOCLayout>
    </Router>
  );
}

export default App;
