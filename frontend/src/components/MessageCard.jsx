import { useState } from 'react';
import { useApproveMessage, useIgnoreMessage, useRegenerateResponse } from '../api/useMessages';

const PLATAFORMA_ICONS = {
  facebook: '📘',
  instagram: '📸',
  google: '⭐',
};

const TIPO_COLORS = {
  queja: 'bg-red-100 text-red-700',
  consulta: 'bg-blue-100 text-blue-700',
  elogio: 'bg-green-100 text-green-700',
  spam: 'bg-gray-100 text-gray-600',
};

const URGENCIA_COLORS = {
  alta: 'border-l-4 border-red-500',
  media: 'border-l-4 border-yellow-400',
  baja: 'border-l-4 border-green-400',
};

export default function MessageCard({ message }) {
  const [editingResponse, setEditingResponse] = useState(false);
  const [responseText, setResponseText] = useState(message.respuesta_sugerida || '');

  const approveMutation = useApproveMessage();
  const ignoreMutation = useIgnoreMessage();
  const regenerateMutation = useRegenerateResponse();

  const handleApprove = () => {
    approveMutation.mutate({ id: message.id, respuesta: responseText });
  };

  const handleIgnore = () => {
    ignoreMutation.mutate(message.id);
  };

  const handleRegenerate = () => {
    regenerateMutation.mutate(message.id, {
      onSuccess: (data) => {
        // La nueva respuesta se cargará del servidor vía invalidación
      },
    });
  };

  const isLoading = approveMutation.isPending || ignoreMutation.isPending || regenerateMutation.isPending;

  if (message.estado === 'ignorado') return null;

  return (
    <div className={`bg-white rounded-xl shadow-sm p-4 mb-3 ${URGENCIA_COLORS[message.urgencia] || ''}`}>
      {/* Cabecera */}
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-2">
          <span className="text-xl">{PLATAFORMA_ICONS[message.plataforma] || '💬'}</span>
          <div>
            <p className="font-semibold text-gray-800 text-sm">{message.autor || 'Anónimo'}</p>
            <p className="text-xs text-gray-400 capitalize">{message.plataforma}</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {message.urgente && (
            <span className="text-xs bg-red-100 text-red-600 font-medium px-2 py-0.5 rounded-full">
              🚨 Urgente
            </span>
          )}
          {message.tipo && (
            <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${TIPO_COLORS[message.tipo] || ''}`}>
              {message.tipo}
            </span>
          )}
        </div>
      </div>

      {/* Mensaje original */}
      <p className="text-gray-700 text-sm mb-3 bg-gray-50 rounded-lg p-3">
        {message.contenido_original}
      </p>

      {/* Respuesta sugerida */}
      {message.estado === 'pendiente' && (
        <div className="mb-3">
          <p className="text-xs text-gray-500 mb-1 font-medium">💡 Respuesta sugerida por IA:</p>
          {editingResponse ? (
            <textarea
              className="w-full border border-gray-300 rounded-lg p-2 text-sm text-gray-700 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows={3}
              value={responseText}
              onChange={(e) => setResponseText(e.target.value)}
            />
          ) : (
            <p
              className="text-sm text-gray-700 bg-blue-50 rounded-lg p-3 cursor-pointer hover:bg-blue-100 transition-colors"
              onClick={() => setEditingResponse(true)}
            >
              {responseText || 'Sin respuesta sugerida'}
            </p>
          )}
        </div>
      )}

      {/* Respuesta enviada */}
      {message.estado !== 'pendiente' && message.respuesta_enviada && (
        <div className="mb-3">
          <p className="text-xs text-gray-500 mb-1 font-medium">✅ Respuesta enviada:</p>
          <p className="text-sm text-gray-700 bg-green-50 rounded-lg p-3">
            {message.respuesta_enviada}
          </p>
        </div>
      )}

      {/* Acciones */}
      {message.estado === 'pendiente' && (
        <div className="flex gap-2 flex-wrap">
          <ApproveButton onClick={handleApprove} loading={approveMutation.isPending} />
          <button
            onClick={() => setEditingResponse(!editingResponse)}
            className="px-3 py-1.5 text-xs text-blue-600 border border-blue-300 rounded-lg hover:bg-blue-50 transition-colors"
            disabled={isLoading}
          >
            ✏️ Editar
          </button>
          <button
            onClick={handleRegenerate}
            className="px-3 py-1.5 text-xs text-purple-600 border border-purple-300 rounded-lg hover:bg-purple-50 transition-colors"
            disabled={isLoading}
          >
            🔄 Otra versión
          </button>
          <button
            onClick={handleIgnore}
            className="px-3 py-1.5 text-xs text-gray-500 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            disabled={isLoading}
          >
            Ignorar
          </button>
        </div>
      )}

      {/* Estado final */}
      {message.estado === 'enviado' && (
        <span className="text-xs text-green-600 font-medium">✅ Publicado</span>
      )}
      {message.estado === 'aprobado' && (
        <span className="text-xs text-blue-600 font-medium">✔️ Aprobado</span>
      )}
    </div>
  );
}

export function ApproveButton({ onClick, loading }) {
  return (
    <button
      onClick={onClick}
      disabled={loading}
      className="px-3 py-1.5 text-xs text-white bg-green-500 rounded-lg hover:bg-green-600 transition-colors disabled:opacity-50 font-medium"
    >
      {loading ? '...' : '✅ Aprobar y publicar'}
    </button>
  );
}
