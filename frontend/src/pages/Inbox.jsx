import { useState } from 'react';
import MessageCard from '../components/MessageCard';
import AlertBanner from '../components/AlertBanner';
import { useMessages, useSyncMessages } from '../api/useMessages';

const PLATFORM_FILTERS = ['todos', 'facebook', 'instagram', 'google'];
const STATE_FILTERS = ['pendiente', 'enviado', 'ignorado'];

export default function Inbox() {
  const [platform, setPlatform] = useState('todos');
  const [showUrgent, setShowUrgent] = useState(false);
  const syncMutation = useSyncMessages();

  const filters = {
    ...(platform !== 'todos' && { plataforma: platform }),
    ...(showUrgent && { urgente: true }),
    estado: 'pendiente',
    limit: 50,
  };

  const { data: messages, isLoading, error } = useMessages(filters);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Bandeja unificada</h1>
          <p className="text-gray-500 text-sm mt-0.5">
            Comentarios, DMs y reseñas de todas las plataformas
          </p>
        </div>
        <button
          onClick={() => syncMutation.mutate()}
          disabled={syncMutation.isPending}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-xl text-sm font-medium hover:bg-blue-700 transition-colors disabled:opacity-50"
        >
          {syncMutation.isPending ? '⟳ Sincronizando...' : '🔄 Sincronizar'}
        </button>
      </div>

      {/* Resultado de sincronización */}
      {syncMutation.isSuccess && (
        <AlertBanner
          type="success"
          message={syncMutation.data?.detail || 'Sincronización completada.'}
        />
      )}

      {/* Filtros */}
      <div className="flex flex-wrap gap-2">
        {PLATFORM_FILTERS.map((p) => (
          <button
            key={p}
            onClick={() => setPlatform(p)}
            className={`px-3 py-1.5 rounded-xl text-xs font-medium capitalize transition-colors ${
              platform === p
                ? 'bg-blue-600 text-white'
                : 'bg-white text-gray-600 border border-gray-200 hover:bg-gray-50'
            }`}
          >
            {p}
          </button>
        ))}
        <button
          onClick={() => setShowUrgent(!showUrgent)}
          className={`px-3 py-1.5 rounded-xl text-xs font-medium transition-colors ${
            showUrgent
              ? 'bg-red-500 text-white'
              : 'bg-white text-red-600 border border-red-200 hover:bg-red-50'
          }`}
        >
          🚨 Solo urgentes
        </button>
      </div>

      {/* Mensajes */}
      {isLoading && (
        <div className="text-center py-12 text-gray-400 text-sm">Cargando mensajes...</div>
      )}

      {error && (
        <AlertBanner type="error" message="Error al cargar los mensajes." />
      )}

      {!isLoading && !error && messages?.length === 0 && (
        <div className="text-center py-16">
          <p className="text-5xl mb-3">📭</p>
          <p className="text-gray-500 font-medium">No hay mensajes pendientes</p>
          <p className="text-gray-400 text-sm mt-1">
            Haz clic en "Sincronizar" para obtener mensajes nuevos de tus plataformas
          </p>
        </div>
      )}

      {messages?.map((msg) => (
        <MessageCard key={msg.id} message={msg} />
      ))}
    </div>
  );
}
