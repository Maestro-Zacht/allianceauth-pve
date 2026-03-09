import { createContext, useState, useContext, type ReactNode } from 'react';
import { Toast, ToastContainer } from 'react-bootstrap';
import { useTranslation } from 'react-i18next';
import type { ToastProps } from 'react-bootstrap';

interface ToastMessage {
    id: number;
    message: string;
    variant?: ToastProps['bg'];
}

type ShowToastFn = (message: string, variant?: ToastProps['bg']) => void;

const ToastContext = createContext<ShowToastFn | undefined>(undefined);

export const ToastProvider = ({ children }: { children: ReactNode }) => {
    const [toasts, setToasts] = useState<ToastMessage[]>([]);
    const { t } = useTranslation();

    const addToast: ShowToastFn = (message, variant) => {
        const id = Date.now();
        setToasts((prev) => [...prev, { id, message, variant }]);
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
                            bg={toast.variant}
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