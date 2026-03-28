const TYPE_STYLES = {
  error: 'bg-red-50 border-red-300 text-red-800',
  warning: 'bg-yellow-50 border-yellow-300 text-yellow-800',
  info: 'bg-blue-50 border-blue-300 text-blue-800',
  success: 'bg-green-50 border-green-300 text-green-800',
};

const TYPE_ICONS = {
  error: '🚨',
  warning: '⚠️',
  info: 'ℹ️',
  success: '✅',
};

export default function AlertBanner({ message, type = 'info', onDismiss }) {
  return (
    <div className={`flex items-center gap-3 p-3 rounded-xl border ${TYPE_STYLES[type]} mb-4`}>
      <span className="text-xl flex-shrink-0">{TYPE_ICONS[type]}</span>
      <p className="flex-1 text-sm font-medium">{message}</p>
      {onDismiss && (
        <button
          onClick={onDismiss}
          className="text-current opacity-60 hover:opacity-100 text-lg leading-none ml-2"
          aria-label="Cerrar alerta"
        >
          ×
        </button>
      )}
    </div>
  );
}
