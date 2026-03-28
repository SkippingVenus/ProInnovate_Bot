import MetricWidget from '../components/MetricWidget';
import AlertBanner from '../components/AlertBanner';
import { useDashboard } from '../api/useReports';
import { useMessages } from '../api/useMessages';

export default function Dashboard() {
  const { data: metrics, isLoading, error } = useDashboard();
  const { data: urgentMessages } = useMessages({ urgente: true, estado: 'pendiente', limit: 5 });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-400 text-sm">Cargando dashboard...</div>
      </div>
    );
  }

  if (error) {
    return (
      <AlertBanner
        type="error"
        message="Error al cargar el dashboard. Por favor recarga la página."
      />
    );
  }

  const tasa = metrics?.tasa_respuesta ?? 0;
  const tiempoPromedio = metrics?.tiempo_promedio_respuesta_horas;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-800">Dashboard</h1>
        <p className="text-gray-500 text-sm mt-1">Resumen de actividad de tu negocio</p>
      </div>

      {/* Alerta de mensajes urgentes */}
      {metrics?.mensajes_urgentes_pendientes > 0 && (
        <AlertBanner
          type="error"
          message={`Tienes ${metrics.mensajes_urgentes_pendientes} mensaje(s) urgente(s) pendiente(s) de respuesta.`}
        />
      )}

      {/* Métricas principales */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        <MetricWidget
          title="Mensajes hoy"
          value={metrics?.mensajes_hoy ?? 0}
          icon="📬"
          color="blue"
          subtitle="Recibidos en todas las plataformas"
        />
        <MetricWidget
          title="Tasa de respuesta"
          value={`${tasa}%`}
          icon="💬"
          color="green"
          subtitle="Últimos 30 días"
        />
        <MetricWidget
          title="Tiempo de respuesta"
          value={tiempoPromedio ? `${tiempoPromedio}h` : '—'}
          icon="⏱️"
          color="yellow"
          subtitle="Promedio últimos 30 días"
        />
        <MetricWidget
          title="Rating Google"
          value={metrics?.rating_google ? `${metrics.rating_google} ⭐` : '—'}
          icon="⭐"
          color="yellow"
          subtitle="Google Maps"
        />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <MetricWidget
          title="Seguidores totales"
          value={metrics?.seguidores_total?.toLocaleString() ?? '—'}
          icon="👥"
          color="purple"
          subtitle="Facebook + Instagram"
        />
        <MetricWidget
          title="Alcance orgánico"
          value={metrics?.alcance_organico_semana?.toLocaleString() ?? '—'}
          icon="📡"
          color="blue"
          subtitle="Esta semana"
        />
      </div>

      {/* Mensajes urgentes recientes */}
      {urgentMessages && urgentMessages.length > 0 && (
        <div>
          <h2 className="text-lg font-semibold text-gray-800 mb-3">🚨 Mensajes urgentes pendientes</h2>
          <div className="space-y-2">
            {urgentMessages.map((msg) => (
              <div key={msg.id} className="bg-red-50 border border-red-200 rounded-xl p-4">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-medium text-red-600 capitalize">{msg.plataforma}</span>
                  <span className="text-xs text-gray-400">{new Date(msg.created_at).toLocaleDateString('es-PE')}</span>
                </div>
                <p className="text-sm text-gray-700 line-clamp-2">{msg.contenido_original}</p>
                <a href="/inbox" className="text-xs text-blue-600 hover:underline mt-1 inline-block">
                  Responder →
                </a>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
