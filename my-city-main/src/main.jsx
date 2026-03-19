import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css'; // если будешь использовать TailwindCSS или стили

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);