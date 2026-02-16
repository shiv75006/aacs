import React from 'react';
import Toast from './Toast';
import './Toast.css';

const ToastContainer = ({ toasts, onRemoveToast }) => {
  React.useEffect(() => {
    console.log('Toasts updated:', toasts);
  }, [toasts]);

  return (
    <div className="toast-container">
      {toasts.map((toast) => (
        <Toast
          key={toast.id}
          id={toast.id}
          type={toast.type}
          message={toast.message}
          duration={toast.duration}
          onClose={onRemoveToast}
        />
      ))}
    </div>
  );
};

export default ToastContainer;
