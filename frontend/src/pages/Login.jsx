import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import api from '../api/client';
import * as mockAuth from '../utils/mockAuth';

export default function Login() {
  const [mode, setMode] = useState('login'); // 'login' | 'register'
  const [form, setForm] = useState({ email: '', password: '', nombre: '', rubro: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    
    try {
      if (mode === 'login') {
        try {
          // Intentar con servidor real (con timeout corto)
          const params = new URLSearchParams();
          params.append('username', form.email);
          params.append('password', form.password);
          
          // Promise que se rechaza después de 4 segundos
          const timeoutPromise = new Promise((_, reject) =>
            setTimeout(() => reject(new Error('Timeout - BD no disponible')), 4000)
          );
          
          const resp = await Promise.race([
            api.post('/auth/login', params, {
              headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            }),
            timeoutPromise
          ]);
          
          localStorage.setItem('token', resp.data.access_token);
          localStorage.removeItem('mockMode');
          navigate('/dashboard');
          return;
        } catch (apiError) {
          // Si falla, usar mock
          console.warn('🐛 BD no disponible, usando mock auth:', apiError.message);
          const mockResult = mockAuth.loginUser(form.email, form.password);
          if (mockResult.success) {
            localStorage.setItem('token', mockResult.token);
            localStorage.setItem('mockMode', 'true');
            navigate('/dashboard');
            return;
          } else {
            setError(mockResult.error);
            setLoading(false);
            return;
          }
        }
      } else {
        // REGISTRAR
        try {
          // Intentar con servidor real (con timeout corto)
          const timeoutPromise = new Promise((_, reject) =>
            setTimeout(() => reject(new Error('Timeout - BD no disponible')), 4000)
          );
          
          const resp = await Promise.race([
            api.post('/auth/register', form),
            timeoutPromise
          ]);
          
          localStorage.setItem('token', resp.data.access_token);
          localStorage.removeItem('mockMode');
          navigate('/onboarding');
          return;
        } catch (apiError) {
          // Si falla, usar mock
          console.warn('🐛 BD no disponible, usando mock auth:', apiError.message);
          const mockResult = mockAuth.registerUser(
            form.email,
            form.password,
            form.nombre,
            form.rubro
          );
          if (mockResult.success) {
            localStorage.setItem('token', mockResult.token);
            localStorage.setItem('mockMode', 'true');
            navigate('/onboarding');
            return;
          } else {
            setError(mockResult.error);
            setLoading(false);
            return;
          }
        }
      }
    } catch (err) {
      console.error('❌ Error inesperado:', err);
      setError('Error inesperado. Intenta de nuevo.');
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-md p-8">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="w-14 h-14 bg-blue-600 rounded-2xl flex items-center justify-center text-white text-2xl font-bold mx-auto mb-3">R</div>
          <h1 className="text-2xl font-bold text-gray-800">RepuBot</h1>
          <p className="text-gray-500 text-sm mt-1">Agente de marketing digital con IA</p>
        </div>

        {/* Tabs */}
        <div className="flex bg-gray-100 rounded-xl p-1 mb-6">
          <button
            onClick={() => setMode('login')}
            className={`flex-1 py-2 rounded-lg text-sm font-medium transition-colors ${mode === 'login' ? 'bg-white text-gray-800 shadow-sm' : 'text-gray-500'}`}
          >
            Iniciar sesión
          </button>
          <button
            onClick={() => setMode('register')}
            className={`flex-1 py-2 rounded-lg text-sm font-medium transition-colors ${mode === 'register' ? 'bg-white text-gray-800 shadow-sm' : 'text-gray-500'}`}
          >
            Crear cuenta
          </button>
        </div>

        {/* Formulario */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {mode === 'register' && (
            <>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Nombre del negocio</label>
                <input
                  type="text"
                  required
                  value={form.nombre}
                  onChange={(e) => setForm({ ...form, nombre: e.target.value })}
                  className="w-full border border-gray-300 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Ej: Pollería Los Andes"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Rubro</label>
                <input
                  type="text"
                  required
                  value={form.rubro}
                  onChange={(e) => setForm({ ...form, rubro: e.target.value })}
                  className="w-full border border-gray-300 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Ej: Restaurante, Tienda, Servicio..."
                />
              </div>
            </>
          )}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Correo electrónico</label>
            <input
              type="email"
              required
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
              className="w-full border border-gray-300 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="correo@negocio.com"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Contraseña</label>
            <input
              type="password"
              required
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              className="w-full border border-gray-300 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="••••••••"
            />
          </div>

          {error && (
            <p className="text-red-600 text-sm bg-red-50 p-3 rounded-xl">{error}</p>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-3 rounded-xl font-medium text-sm hover:bg-blue-700 transition-colors disabled:opacity-50"
          >
            {loading ? 'Cargando...' : mode === 'login' ? 'Iniciar sesión' : 'Crear cuenta'}
          </button>
        </form>

        <p className="text-center text-xs text-gray-400 mt-6">
          Al usar RepuBot aceptas nuestros términos de servicio
        </p>
      </div>
    </div>
  );
}
