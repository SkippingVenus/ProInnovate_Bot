/**
 * Demo/Test del componente OnboardingFlow
 * 
 * Para usar este archivo:
 * 1. Importa OnboardingFlow en tu App.jsx
 * 2. Renderiza este componente en una ruta de prueba
 * 3. Abre la consola del navegador para ver los logs
 * 4. Completa el onboarding y verifica localStorage
 */

import { useState } from 'react';
import OnboardingFlow from '../components/OnboardingFlow';

export default function OnboardingDemo() {
  const [completed, setCompleted] = useState(false);
  const [savedData, setSavedData] = useState(null);

  const handleOnboardingComplete = (data) => {
    console.log('✅ Onboarding completado:', data);
    setSavedData(data);
    setCompleted(true);

    // Simular guardado en backend
    setTimeout(() => {
      console.log('📤 Enviando datos al servidor...');
      // await api.post('/businesses/setup', data);
    }, 1000);
  };

  const handleReset = () => {
    localStorage.removeItem('onboarding_data');
    setCompleted(false);
    setSavedData(null);
    window.location.reload();
  };

  if (!completed) {
    return <OnboardingFlow onComplete={handleOnboardingComplete} />;
  }

  // Vista de confirmación después de completar
  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-100 flex items-center justify-center p-4">
      <div className="w-full max-w-2xl bg-white rounded-lg shadow-xl p-8">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-green-600 mb-3">
            ✅ ¡Onboarding Completado!
          </h1>
          <p className="text-gray-600 text-lg">
            Los datos fueron guardados exitosamente en localStorage
          </p>
        </div>

        {/* Mostrar datos guardados */}
        <div className="bg-gray-50 rounded-lg p-6 mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Datos Capturados:</h2>
          
          <div className="space-y-4">
            <div className="border-l-4 border-blue-500 pl-4">
              <p className="text-sm text-gray-600 font-semibold">Nombre del Negocio:</p>
              <p className="text-lg text-gray-900">{savedData?.nombre}</p>
            </div>

            <div className="border-l-4 border-purple-500 pl-4">
              <p className="text-sm text-gray-600 font-semibold">Tono de Comunicación:</p>
              <p className="text-lg text-gray-900 capitalize">{savedData?.tono}</p>
            </div>

            <div className="border-l-4 border-indigo-500 pl-4">
              <p className="text-sm text-gray-600 font-semibold">Público Objetivo:</p>
              <p className="text-lg text-gray-900">{savedData?.publico_objetivo}</p>
            </div>

            <div className="border-l-4 border-pink-500 pl-4">
              <p className="text-sm text-gray-600 font-semibold">Horario y Contacto:</p>
              <p className="text-lg text-gray-900">{savedData?.horario_contacto}</p>
            </div>

            <div className="border-l-4 border-orange-500 pl-4">
              <p className="text-sm text-gray-600 font-semibold">Competidores:</p>
              <p className="text-lg text-gray-900">{savedData?.competidores}</p>
            </div>
          </div>
        </div>

        {/* Mostrar cómo recuperar datos */}
        <div className="bg-blue-50 rounded-lg p-6 mb-8 border border-blue-200">
          <h3 className="text-lg font-bold text-blue-900 mb-3">📋 Cómo acceder a los datos:</h3>
          
          <p className="text-blue-800 mb-3">
            Los datos están guardados en <code className="bg-blue-100 px-2 py-1 rounded">localStorage</code> con la clave <code className="bg-blue-100 px-2 py-1 rounded">onboarding_data</code>
          </p>

          <pre className="bg-gray-900 text-green-400 p-4 rounded-lg overflow-x-auto text-sm mb-3">
{`const data = JSON.parse(
  localStorage.getItem('onboarding_data')
);

console.log(data.nombre);
// Output: "${savedData?.nombre}"`}
          </pre>

          <p className="text-blue-800 text-sm">
            Abre la consola del navegador y ejecuta el código arriba para verificar.
          </p>
        </div>

        {/* Acciones */}
        <div className="flex gap-4 justify-center">
          <button
            onClick={handleReset}
            className="px-8 py-3 rounded-lg font-semibold bg-orange-500 text-white hover:bg-orange-600 transition-colors"
          >
            🔄 Reiniciar Onboarding
          </button>

          <button
            onClick={() => {
              const data = JSON.parse(localStorage.getItem('onboarding_data'));
              console.log('Datos en localStorage:', data);
              alert('Verifica la consola del navegador (F12) para ver los datos');
            }}
            className="px-8 py-3 rounded-lg font-semibold bg-green-500 text-white hover:bg-green-600 transition-colors"
          >
            🔍 Ver en Consola
          </button>
        </div>

        {/* Info dev */}
        <div className="mt-8 pt-6 border-t border-gray-200 text-center text-sm text-gray-500">
          <p>🧪 Modo Demo - Para desarrollo y pruebas</p>
          <p className="mt-1">Los datos persisten incluso después de recargar la página</p>
        </div>
      </div>
    </div>
  );
}
