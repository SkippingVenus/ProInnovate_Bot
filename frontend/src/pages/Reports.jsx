import MetricWidget from '../components/MetricWidget';
import { useDashboard, useMetrics } from '../api/useReports';

export default function Reports() {
  const { data: dashboard } = useDashboard();
  const { data: metrics } = useMetrics({ days: 30 });

  // Agrupar métricas por plataforma
  const byPlatform = (platform) =>
    metrics?.filter((m) => m.plataforma === platform) || [];

  const latestGoogle = byPlatform('google')[0];
  const latestFacebook = byPlatform('facebook')[0];
  const latestInstagram = byPlatform('instagram')[0];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-800">Reportes</h1>
        <p className="text-gray-500 text-sm mt-0.5">Métricas de rendimiento de los últimos 30 días</p>
      </div>

      {/* Resumen general */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
        <MetricWidget
          title="Tasa de respuesta"
          value={`${dashboard?.tasa_respuesta ?? 0}%`}
          icon="💬"
          color="green"
          subtitle="Mensajes respondidos / recibidos"
        />
        <MetricWidget
          title="Tiempo promedio respuesta"
          value={dashboard?.tiempo_promedio_respuesta_horas ? `${dashboard.tiempo_promedio_respuesta_horas}h` : '—'}
          icon="⏱️"
          color="yellow"
          subtitle="Tiempo hasta primera respuesta"
        />
        <MetricWidget
          title="Mensajes urgentes pendientes"
          value={dashboard?.mensajes_urgentes_pendientes ?? 0}
          icon="🚨"
          color={dashboard?.mensajes_urgentes_pendientes > 0 ? 'red' : 'green'}
          subtitle="Requieren atención inmediata"
        />
      </div>

      {/* Por plataforma */}
      <div>
        <h2 className="text-lg font-semibold text-gray-800 mb-3">Por plataforma</h2>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {/* Google Maps */}
          <div className="bg-white rounded-xl shadow-sm p-4">
            <div className="flex items-center gap-2 mb-3">
              <span className="text-2xl">⭐</span>
              <h3 className="font-semibold text-gray-800">Google Maps</h3>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Rating promedio</span>
                <span className="font-medium">{latestGoogle?.rating_promedio?.toFixed(1) ?? '—'}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Reseñas positivas</span>
                <span className="font-medium text-green-600">{latestGoogle?.resenas_positivas ?? '—'}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Reseñas negativas</span>
                <span className="font-medium text-red-500">{latestGoogle?.resenas_negativas ?? '—'}</span>
              </div>
            </div>
          </div>

          {/* Facebook */}
          <div className="bg-white rounded-xl shadow-sm p-4">
            <div className="flex items-center gap-2 mb-3">
              <span className="text-2xl">📘</span>
              <h3 className="font-semibold text-gray-800">Facebook</h3>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Seguidores</span>
                <span className="font-medium">{latestFacebook?.seguidores?.toLocaleString() ?? '—'}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Alcance orgánico</span>
                <span className="font-medium">{latestFacebook?.alcance_organico?.toLocaleString() ?? '—'}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Mensajes recibidos</span>
                <span className="font-medium">{latestFacebook?.mensajes_recibidos ?? '—'}</span>
              </div>
            </div>
          </div>

          {/* Instagram */}
          <div className="bg-white rounded-xl shadow-sm p-4">
            <div className="flex items-center gap-2 mb-3">
              <span className="text-2xl">📸</span>
              <h3 className="font-semibold text-gray-800">Instagram</h3>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Seguidores</span>
                <span className="font-medium">{latestInstagram?.seguidores?.toLocaleString() ?? '—'}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Alcance orgánico</span>
                <span className="font-medium">{latestInstagram?.alcance_organico?.toLocaleString() ?? '—'}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Mensajes recibidos</span>
                <span className="font-medium">{latestInstagram?.mensajes_recibidos ?? '—'}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
