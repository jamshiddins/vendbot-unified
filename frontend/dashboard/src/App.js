import React, { useEffect, useState } from 'react';
import './App.css';

function App() {
  const [apiStatus, setApiStatus] = useState('Проверяется...');
  const apiUrl = process.env.REACT_APP_API_URL || 'API URL не настроен';

  // Проверяем статус API при загрузке компонента
  useEffect(() => {
    if (process.env.REACT_APP_API_URL) {
      fetch(`${process.env.REACT_APP_API_URL}/health`)
        .then(response => response.ok ? setApiStatus(' Подключен') : setApiStatus(' Ошибка'))
        .catch(() => setApiStatus(' Недоступен'));
    }
  }, []);

  return (
    <div style={{
      padding: '40px', 
      fontFamily: 'Arial, sans-serif', 
      textAlign: 'center',
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      color: 'white'
    }}>
      <div style={{
        maxWidth: '800px',
        margin: '0 auto',
        background: 'rgba(255, 255, 255, 0.1)',
        padding: '40px',
        borderRadius: '20px',
        backdropFilter: 'blur(10px)'
      }}>
        <h1 style={{fontSize: '3em', marginBottom: '20px'}}> VendBot Dashboard</h1>
        <p style={{fontSize: '1.2em', marginBottom: '30px'}}> Успешно развернут на Vercel!</p>
        
        <div style={{
          marginTop: '30px', 
          padding: '20px', 
          background: 'rgba(0, 0, 0, 0.2)', 
          borderRadius: '10px',
          textAlign: 'left'
        }}>
          <h3> Конфигурация системы:</h3>
          <p><strong>API URL:</strong> {apiUrl}</p>
          <p><strong>Статус API:</strong> {apiStatus}</p>
          <p><strong>Среда:</strong> Production</p>
          <p><strong>Версия:</strong> 1.0.0</p>
        </div>

        <div style={{
          marginTop: '30px', 
          padding: '20px', 
          background: 'rgba(0, 0, 0, 0.2)', 
          borderRadius: '10px'
        }}>
          <h3> Возможности VendBot:</h3>
          <p> Управление вендинговыми машинами</p>
          <p> Учет бункеров и ингредиентов</p>
          <p> Ролевая система доступа</p>
          <p> Telegram-бот интерфейс</p>
        </div>
      </div>
    </div>
  );
}

export default App;
