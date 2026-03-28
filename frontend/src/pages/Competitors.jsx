import { useState } from 'react';
import { useCompetitors, useCreateCompetitor, useDeleteCompetitor } from '../api/useCompetitors';
import AlertBanner from '../components/AlertBanner';

export default function Competitors() {
  const { data: competitors, isLoading } = useCompetitors();
  const createMutation = useCreateCompetitor();
  const deleteMutation = useDeleteCompetitor();
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ nombre: '', fb_page_url: '', ig_username: '', gmb_place_id: '' });

  const handleSubmit = (e) => {
    e.preventDefault();
    createMutation.mutate(form, {
      onSuccess: () => {
        setForm({ nombre: '', fb_page_url: '', ig_username: '', gmb_place_id: '' });
        setShowForm(false);
      },
    });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Competidores</h1>
          <p className="text-gray-500 text-sm mt-0.5">Monitorea la presencia digital de tus competidores</p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="px-4 py-2 bg-blue-600 text-white rounded-xl text-sm font-medium hover:bg-blue-700 transition-colors"
        >
          + Agregar competidor
        </button>
      </div>

      {/* Formulario */}
      {showForm && (
        <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow-sm p-5 space-y-4">
          <h2 className="font-semibold text-gray-800">Nuevo competidor</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Nombre *</label>
              <input
                required
                type="text"
                value={form.nombre}
                onChange={(e) => setForm({ ...form, nombre: e.target.value })}
                className="w-full border border-gray-300 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Ej: Pollería El Buen Gusto"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">URL Facebook</label>
              <input
                type="url"
                value={form.fb_page_url}
                onChange={(e) => setForm({ ...form, fb_page_url: e.target.value })}
                className="w-full border border-gray-300 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="https://facebook.com/pagina"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Usuario Instagram</label>
              <input
                type="text"
                value={form.ig_username}
                onChange={(e) => setForm({ ...form, ig_username: e.target.value })}
                className="w-full border border-gray-300 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="@usuario"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Google Place ID</label>
              <input
                type="text"
                value={form.gmb_place_id}
                onChange={(e) => setForm({ ...form, gmb_place_id: e.target.value })}
                className="w-full border border-gray-300 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="ChIJ..."
              />
            </div>
          </div>
          <div className="flex gap-3">
            <button
              type="submit"
              disabled={createMutation.isPending}
              className="px-4 py-2 bg-blue-600 text-white rounded-xl text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
            >
              {createMutation.isPending ? 'Guardando...' : 'Guardar'}
            </button>
            <button
              type="button"
              onClick={() => setShowForm(false)}
              className="px-4 py-2 border border-gray-300 text-gray-600 rounded-xl text-sm hover:bg-gray-50"
            >
              Cancelar
            </button>
          </div>
        </form>
      )}

      {/* Lista */}
      {isLoading && <p className="text-gray-400 text-sm">Cargando competidores...</p>}

      {!isLoading && competitors?.length === 0 && (
        <div className="text-center py-16">
          <p className="text-5xl mb-3">🔍</p>
          <p className="text-gray-500 font-medium">Sin competidores agregados</p>
          <p className="text-gray-400 text-sm mt-1">Agrega competidores para monitorear su actividad</p>
        </div>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
        {competitors?.map((comp) => (
          <div key={comp.id} className="bg-white rounded-xl shadow-sm p-4">
            <div className="flex items-start justify-between mb-3">
              <h3 className="font-semibold text-gray-800">{comp.nombre}</h3>
              <button
                onClick={() => deleteMutation.mutate(comp.id)}
                className="text-gray-400 hover:text-red-500 text-sm transition-colors"
              >
                🗑️
              </button>
            </div>
            <div className="space-y-1 text-xs text-gray-500">
              {comp.fb_page_url && (
                <a href={comp.fb_page_url} target="_blank" rel="noopener noreferrer" className="flex items-center gap-1 text-blue-600 hover:underline">
                  📘 Facebook
                </a>
              )}
              {comp.ig_username && (
                <p>📸 @{comp.ig_username}</p>
              )}
              {comp.gmb_place_id && (
                <p>⭐ Google Places: {comp.gmb_place_id.substring(0, 20)}...</p>
              )}
            </div>
            {comp.ultimo_analisis && (
              <p className="text-xs text-gray-400 mt-2">
                Último análisis: {new Date(comp.ultimo_analisis).toLocaleDateString('es-PE')}
              </p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
