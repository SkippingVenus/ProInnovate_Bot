/**
 * Debug Component para Mock Data
 * Muestra todos los datos almacenados en localStorage
 */

import { useState, useEffect } from 'react';
import * as mockAuth from './mockAuth';

export default function MockDebugger() {
  const [status, setStatus] = useState(null);
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    updateStatus();
  }, []);

  const updateStatus = () => {
    const status = mockAuth.getMockStatus();
    const token = localStorage.getItem('token');
    const mockMode = localStorage.getItem('mockMode') === 'true';
    const currentUser = token ? mockAuth.getUserByToken(token) : null;

    setStatus({
      ...status,
      mockMode,
      token: token?.substring(0, 20) + '...',
      currentUser,
    });
  };

  const handleReset = () => {
    if (window.confirm('¿Seguro? Esto borrará todos los datos de prueba.')) {
      mockAuth.clearAllMockData();
      localStorage.removeItem('token');
      localStorage.removeItem('mockMode');
      setStatus(mockAuth.getMockStatus());
      alert('Datos reseteados. Recarga la página.');
    }
  };

  const handleDemoLogin = (email, password) => {
    localStorage.removeItem('token');
    localStorage.removeItem('mockMode');
    const result = mockAuth.loginUser(email, password);
    if (result.success) {
      localStorage.setItem('token', result.token);
      localStorage.setItem('mockMode', 'true');
      updateStatus();
      alert(`✅ Login como: ${email}`);
      window.location.reload();
    }
  };

  if (!status) return null;

  return (
    <>
      {/* Botón flotante para abrir debugger */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-4 right-4 z-40 bg-purple-600 hover:bg-purple-700 text-white rounded-full w-12 h-12 flex items-center justify-center shadow-lg text-xl font-bold transition-all"
        title="Mock Debugger (Haz click para ver datos)"
      >
        🐛
      </button>

      {/* Panel de debug */}
      {isOpen && (
        <div className="fixed bottom-20 right-4 z-50 w-96 bg-white rounded-lg shadow-2xl border border-purple-200 p-4 max-h-96 overflow-y-auto">
          <div className="space-y-4">
            {/* Header */}
            <div className="border-b pb-3">
              <h3 className="font-bold text-purple-600 text-lg flex items-center gap-2">
                🐛 Mock Debug Panel
              </h3>
              <p className="text-xs text-gray-500 mt-1">
                Datos almacenados en localStorage
              </p>
            </div>

            {/* Estado */}
            <div className="bg-gray-50 p-3 rounded text-sm space-y-2">
              <div>
                <span className="font-medium">Modo Mock:</span>{' '}
                <span className={status.mockMode ? 'text-green-600 font-bold' : 'text-red-600'}>
                  {status.mockMode ? '✅ ACTIVO' : '❌ Inactivo (usando BD)'}
                </span>
              </div>
              <div>
                <span className="font-medium">Token:</span>
                <p className="text-xs text-gray-600 break-all">{status.token || 'No hay token'}</p>
              </div>
              {status.currentUser && (
                <div className="bg-blue-50 p-2 rounded">
                  <span className="font-medium text-blue-900">Usuario Actual:</span>
                  <p className="text-xs text-blue-800">
                    {status.currentUser.nombre} ({status.currentUser.email})
                  </p>
                </div>
              )}
            </div>

            {/* Contadores */}
            <div className="grid grid-cols-2 gap-2">
              <div className="bg-blue-50 p-3 rounded text-center">
                <p className="text-2xl font-bold text-blue-600">{status.usersCount}</p>
                <p className="text-xs text-blue-700">Usuarios</p>
              </div>
              <div className="bg-green-50 p-3 rounded text-center">
                <p className="text-2xl font-bold text-green-600">{status.businessesCount}</p>
                <p className="text-xs text-green-700">Negocios</p>
              </div>
            </div>

            {/* Usuarios */}
            <div>
              <p className="font-medium text-sm mb-2">👥 Usuarios Registrados:</p>
              <div className="space-y-1 text-xs">
                {status.users && status.users.length > 0 ? (
                  status.users.map((user) => (
                    <div key={user.id} className="bg-gray-100 p-2 rounded flex justify-between items-start">
                      <div>
                        <p className="font-medium">{user.nombre}</p>
                        <p className="text-gray-600">{user.email}</p>
                        {user.onboardingCompleted && (
                          <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded inline-block mt-1">
                            ✅ Onboarding Completado
                          </span>
                        )}
                      </div>
                      <button
                        onClick={() => handleDemoLogin(user.email, user.email.includes('demo') ? 'demo123' : 'test123')}
                        className="bg-blue-500 text-white px-2 py-1 rounded text-xs hover:bg-blue-600"
                      >
                        Login
                      </button>
                    </div>
                  ))
                ) : (
                  <p className="text-gray-500 italic">No hay usuarios</p>
                )}
              </div>
            </div>

            {/* Negocios */}
            {status.businessesCount > 0 && (
              <div>
                <p className="font-medium text-sm mb-2">🏢 Negocios Registrados:</p>
                <div className="space-y-1 text-xs">
                  {status.businesses && status.businesses.map((biz) => (
                    <div key={biz.id} className="bg-gray-100 p-2 rounded">
                      <p className="font-medium">{biz.razonSocial}</p>
                      <p className="text-gray-600">ID Usuario: {biz.userId}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Acciones */}
            <div className="border-t pt-3 space-y-2">
              <button
                onClick={updateStatus}
                className="w-full bg-blue-500 hover:bg-blue-600 text-white py-2 rounded text-sm font-medium"
              >
                🔄 Refrescar
              </button>
              <button
                onClick={handleReset}
                className="w-full bg-red-500 hover:bg-red-600 text-white py-2 rounded text-sm font-medium"
              >
                🗑️ Limpiar Todo
              </button>
            </div>

            {/* Tips */}
            <div className="bg-yellow-50 border border-yellow-200 p-3 rounded text-xs text-yellow-800">
              <p className="font-medium mb-1">💡 Tips:</p>
              <ul className="list-disc list-inside space-y-1">
                <li>Haz click en "Login" para entrar como ese usuario</li>
                <li>Los datos se guardan en localStorage</li>
                <li>Recarga la página (F5) para ver cambios</li>
                <li>Si la BD se conecta, los datos reales prevalecen</li>
              </ul>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
