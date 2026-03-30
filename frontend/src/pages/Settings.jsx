import { useState, useEffect } from 'react';
import { useBusiness, useOnboarding, useConnections } from '../api/useBusinesses';
import AlertBanner from '../components/AlertBanner';
import api from '../api/client';

const TONOS = [
  { value: 'cercano', label: 'Cercano', desc: 'Amigable y de confianza' },
  { value: 'profesional', label: 'Profesional', desc: 'Formal y cortés' },
  { value: 'divertido', label: 'Divertido', desc: 'Con humor y dinamismo' },
];

const PLANES = [
  { id: 'basico', nombre: 'Básico', precio: 'S/89', features: ['1 negocio', 'FB + IG', 'Bandeja unificada'] },
  { id: 'pro', nombre: 'Pro', precio: 'S/179', features: ['1 negocio', 'FB + IG + Google', 'Modo automático'] },
  { id: 'agencia', nombre: 'Agencia', precio: 'S/399', features: ['5 negocios', 'Todo incluido', 'Soporte prioritario'] },
];

export default function Settings() {
  const { data: business, isLoading } = useBusiness();
  const { data: connections } = useConnections();
  const onboardingMutation = useOnboarding();

  const [form, setForm] = useState({
    nombre: '',
    rubro: '',
    tono: 'profesional',
    descripcion: '',
    publico_objetivo: '',
    horario: '',
    whatsapp: '',
  });
  const [success, setSuccess] = useState(false);
  const [activeTab, setActiveTab] = useState('perfil');

  useEffect(() => {
    if (business) {
      setForm({
        nombre: business.nombre || '',
        rubro: business.rubro || '',
        tono: business.tono || 'profesional',
        descripcion: business.descripcion || '',
        publico_objetivo: business.publico_objetivo || '',
        horario: business.horario || '',
        whatsapp: business.whatsapp || '',
      });
    }
  }, [business]);

  const handleSave = (e) => {
    e.preventDefault();
    onboardingMutation.mutate(form, {
      onSuccess: () => {
        setSuccess(true);
        setTimeout(() => setSuccess(false), 3000);
      },
    });
  };

  const handleConnectMeta = async () => {
    try {
      const resp = await api.get('/auth/meta');
      window.location.href = resp.data.url;
    } catch (err) {
      console.error('Error al conectar Meta:', err);
    }
  };

  const handleConnectGoogle = async () => {
    try {
      const resp = await api.get('/auth/google');
      window.location.href = resp.data.url;
    } catch (err) {
      console.error('Error al conectar Google:', err);
    }
  };

  if (isLoading) return <div className="text-gray-400 text-sm">Cargando configuración...</div>;

  return (
    <div className="space-y-6 max-w-3xl">
      <div>
        <h1 className="text-2xl font-bold text-gray-800">Configuración</h1>
        <p className="text-gray-500 text-sm mt-0.5">Perfil del negocio y conexiones</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-gray-100 rounded-xl p-1 w-fit">
        {['perfil', 'conexiones', 'plan'].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 rounded-lg text-sm font-medium capitalize transition-colors ${
              activeTab === tab ? 'bg-white shadow-sm text-gray-800' : 'text-gray-500'
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Perfil del negocio */}
      {activeTab === 'perfil' && (
        <form onSubmit={handleSave} className="bg-white rounded-xl shadow-sm p-6 space-y-5">
          <h2 className="font-semibold text-gray-800 text-lg">Perfil del negocio</h2>

          {success && <AlertBanner type="success" message="Configuración guardada exitosamente." />}
          {onboardingMutation.isError && (
            <AlertBanner type="error" message="Error al guardar. Intenta de nuevo." />
          )}

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Nombre del negocio *</label>
              <input
                required type="text" value={form.nombre}
                onChange={(e) => setForm({ ...form, nombre: e.target.value })}
                className="w-full border border-gray-300 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Rubro *</label>
              <input
                required type="text" value={form.rubro}
                onChange={(e) => setForm({ ...form, rubro: e.target.value })}
                className="w-full border border-gray-300 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          {/* Tono */}
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-2">Tono de comunicación</label>
            <div className="grid grid-cols-3 gap-3">
              {TONOS.map((tono) => (
                <button
                  key={tono.value}
                  type="button"
                  onClick={() => setForm({ ...form, tono: tono.value })}
                  className={`p-3 rounded-xl border text-left transition-colors ${
                    form.tono === tono.value
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <p className="font-medium text-sm text-gray-800">{tono.label}</p>
                  <p className="text-xs text-gray-500 mt-0.5">{tono.desc}</p>
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Descripción del negocio</label>
            <textarea
              value={form.descripcion}
              onChange={(e) => setForm({ ...form, descripcion: e.target.value })}
              className="w-full border border-gray-300 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows={3}
              placeholder="Describe tu negocio brevemente..."
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Público objetivo</label>
              <input
                type="text" value={form.publico_objetivo}
                onChange={(e) => setForm({ ...form, publico_objetivo: e.target.value })}
                className="w-full border border-gray-300 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Ej: Familias, jóvenes de 18-35 años..."
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Horario de atención</label>
              <input
                type="text" value={form.horario}
                onChange={(e) => setForm({ ...form, horario: e.target.value })}
                className="w-full border border-gray-300 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Ej: Lun-Vie 9am-6pm"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">WhatsApp para pedidos</label>
              <input
                type="tel" value={form.whatsapp}
                onChange={(e) => setForm({ ...form, whatsapp: e.target.value })}
                className="w-full border border-gray-300 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="+51 999 888 777"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={onboardingMutation.isPending}
            className="px-6 py-2.5 bg-blue-600 text-white rounded-xl text-sm font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            {onboardingMutation.isPending ? 'Guardando...' : 'Guardar cambios'}
          </button>
        </form>
      )}

      {/* Conexiones OAuth */}
      {activeTab === 'conexiones' && (
        <div className="bg-white rounded-xl shadow-sm p-6 space-y-4">
          <h2 className="font-semibold text-gray-800 text-lg">Conexiones de redes sociales</h2>

          <div className="space-y-3">
            <div className="flex items-center justify-between p-4 border border-gray-200 rounded-xl">
              <div className="flex items-center gap-3">
                <span className="text-2xl">📘</span>
                <div>
                  <p className="font-medium text-gray-800 text-sm">Facebook & Instagram</p>
                  <p className="text-xs text-gray-500">Comentarios, DMs y métricas</p>
                </div>
              </div>
              {connections?.facebook ? (
                <span className="text-xs text-green-600 bg-green-50 px-3 py-1 rounded-full font-medium">✅ Conectado</span>
              ) : (
                <button
                  onClick={handleConnectMeta}
                  className="px-4 py-2 bg-blue-600 text-white rounded-xl text-xs font-medium hover:bg-blue-700"
                >
                  Conectar
                </button>
              )}
            </div>

            <div className="flex items-center justify-between p-4 border border-gray-200 rounded-xl">
              <div className="flex items-center gap-3">
                <span className="text-2xl">⭐</span>
                <div>
                  <p className="font-medium text-gray-800 text-sm">Google My Business</p>
                  <p className="text-xs text-gray-500">Reseñas y calificaciones</p>
                </div>
              </div>
              {connections?.google ? (
                <span className="text-xs text-green-600 bg-green-50 px-3 py-1 rounded-full font-medium">✅ Conectado</span>
              ) : (
                <button
                  onClick={handleConnectGoogle}
                  className="px-4 py-2 bg-red-500 text-white rounded-xl text-xs font-medium hover:bg-red-600"
                >
                  Conectar
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Plan */}
      {activeTab === 'plan' && (
        <div className="space-y-4">
          <div className="bg-white rounded-xl shadow-sm p-4">
            <p className="text-sm text-gray-600">
              Plan actual: <span className="font-semibold text-blue-600 capitalize">{business?.plan}</span>
            </p>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {PLANES.map((plan) => (
              <div
                key={plan.id}
                className={`bg-white rounded-xl p-5 border-2 ${
                  business?.plan === plan.id ? 'border-blue-500' : 'border-gray-200'
                }`}
              >
                <h3 className="font-bold text-gray-800 text-lg">{plan.nombre}</h3>
                <p className="text-2xl font-bold text-blue-600 mt-1">{plan.precio}</p>
                <p className="text-xs text-gray-500 mb-3">/mes</p>
                <ul className="space-y-1 mb-4">
                  {plan.features.map((f) => (
                    <li key={f} className="text-xs text-gray-600 flex items-center gap-1">
                      <span className="text-green-500">✓</span> {f}
                    </li>
                  ))}
                </ul>
                {business?.plan !== plan.id && (
                  <button className="w-full py-2 bg-blue-600 text-white rounded-xl text-xs font-medium hover:bg-blue-700">
                    Cambiar plan
                  </button>
                )}
                {business?.plan === plan.id && (
                  <p className="text-xs text-center text-blue-600 font-medium">Plan actual</p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
