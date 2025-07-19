
import { toast } from 'sonner';
import { CheckCircle, AlertCircle, Info, XCircle, Sparkles } from 'lucide-react';

type ToastType = 'success' | 'error' | 'info' | 'warning' | 'ai';

interface EnhancedToastProps {
  type: ToastType;
  title: string;
  description?: string;
  duration?: number;
}

const getToastIcon = (type: ToastType) => {
  switch (type) {
    case 'success':
      return <CheckCircle className="w-5 h-5 text-green-500" />;
    case 'error':
      return <XCircle className="w-5 h-5 text-red-500" />;
    case 'warning':
      return <AlertCircle className="w-5 h-5 text-yellow-500" />;
    case 'ai':
      return <Sparkles className="w-5 h-5 text-blue-500" />;
    default:
      return <Info className="w-5 h-5 text-blue-500" />;
  }
};

const getToastStyles = (type: ToastType) => {
  const baseStyles = "border border-white/10 bg-background/95 backdrop-blur-xl text-white";
  
  switch (type) {
    case 'success':
      return `${baseStyles} border-green-500/30`;
    case 'error':
      return `${baseStyles} border-red-500/30`;
    case 'warning':
      return `${baseStyles} border-yellow-500/30`;
    case 'ai':
      return `${baseStyles} border-blue-500/30`;
    default:
      return `${baseStyles} border-blue-500/30`;
  }
};

export const enhancedToast = ({ type, title, description, duration = 4000 }: EnhancedToastProps) => {
  return toast.custom(
    () => (
      <div className={`${getToastStyles(type)} rounded-lg p-4 shadow-lg max-w-md`}>
        <div className="flex items-start gap-3">
          {getToastIcon(type)}
          <div className="flex-1 min-w-0">
            <div className="text-sm font-medium text-white">{title}</div>
            {description && (
              <div className="text-sm text-white/70 mt-1">{description}</div>
            )}
          </div>
        </div>
      </div>
    ),
    {
      duration,
      position: 'top-right',
    }
  );
};

// Convenience methods
export const toastSuccess = (title: string, description?: string) =>
  enhancedToast({ type: 'success', title, description });

export const toastError = (title: string, description?: string) =>
  enhancedToast({ type: 'error', title, description });

export const toastInfo = (title: string, description?: string) =>
  enhancedToast({ type: 'info', title, description });

export const toastWarning = (title: string, description?: string) =>
  enhancedToast({ type: 'warning', title, description });

export const toastAI = (title: string, description?: string) =>
  enhancedToast({ type: 'ai', title, description });
