import { createContext, useState, useContext, type ReactNode } from 'react';
import { Toast, ToastContainer } from 'react-bootstrap';
import { useTranslation } from 'react-i18next';

interface ToastMessage {
    id: number;
    message: string;
}

type ShowToastFn = (message: string) => void;

const ToastContext = createContext<ShowToastFn | undefined>(undefined);

export const ToastProvider = ({ children }: { children: ReactNode }) => {
    const [toasts, setToasts] = useState<ToastMessage[]>([]);
    const { t } = useTranslation();

    const addToast: ShowToastFn = (message) => {
        const id = Date.now();
        setToasts((prev) => [...prev, { id, message }]);
    };

    const removeToast = (id: number) => {
        setToasts((prev) => prev.filter((t) => t.id !== id));
    };


    return (
        <ToastContext.Provider value={addToast}>
            {children}
            <ToastContainer position="bottom-end" className="p-3" style={{ zIndex: 9999 }}>
                {
                    toasts.map((toast) => (
                        <Toast
                            key={toast.id}
                            onClose={() => removeToast(toast.id)}
                            delay={5000}
                            animation={false}
                            autohide
                        >
                            <Toast.Header>
                                <strong className="me-auto">{t("toast.title")}</strong>
                            </Toast.Header>
                            <Toast.Body>
                                {toast.message}
                            </Toast.Body>
                        </Toast>
                    ))}
            </ToastContainer>
        </ToastContext.Provider>
    );
};

export function useToast() {
    const context = useContext(ToastContext);
    if (!context) {
        throw new Error('useToast must be used within a ToastProvider');
    }
    return context;
};