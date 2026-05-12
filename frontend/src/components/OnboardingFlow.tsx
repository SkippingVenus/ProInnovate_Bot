import React, { useState } from 'react';

interface OnboardingData {
  nombre: string;
  tono: string;
  publico_objetivo: string;
  horario_contacto: string;
  competidores: string;
}

interface OnboardingFlowProps {
  onComplete?: (data: OnboardingData) => void;
}

const OnboardingFlow: React.FC<OnboardingFlowProps> = ({ onComplete }) => {
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState<OnboardingData>({
    nombre: '',
    tono: '',
    publico_objetivo: '',
    horario_contacto: '',
    competidores: '',
  });

  const totalSteps = 5;
  const progressPercentage = (currentStep / totalSteps) * 100;

  const questions = [
    {
      step: 1,
      title: '¿Cómo se llama tu negocio y qué vende?',
      description: 'Cuéntanos sobre tu negocio para personalizar RepuBot',
      field: 'nombre',
      placeholder: 'Ej: Pizzería La Italia - Vendemos pizzas artesanales y pastas caseras',
      type: 'textarea',
    },
    {
      step: 2,
      title: '¿Cómo quieres que te perciban tus clientes?',
      description: 'Elige el tono que mejor representa tu marca',
      field: 'tono',
      placeholder: '',
      type: 'select',
      options: [
        { value: 'cercano', label: '👥 Cercano - Amigable y personal' },
        { value: 'profesional', label: '💼 Profesional - Formal y serio' },
        { value: 'divertido', label: '🎉 Divertido - Creativo y desenfadado' },
      ],
    },
    {
      step: 3,
      title: '¿Quiénes son tus clientes principales?',
      description: 'Ayúdanos a entender mejor a tu audiencia',
      field: 'publico_objetivo',
      placeholder: 'Ej: Jóvenes profesionales (25-40 años), familias, estudiantes universitarios',
      type: 'textarea',
    },
    {
      step: 4,
      title: '¿Cuál es tu horario de atención?',
      description: 'Y cómo pueden contactarte para pedidos',
      field: 'horario_contacto',
      placeholder: 'Ej: Lun-Viernes 9:00-21:00 | Sáb-Dom 10:00-22:00 | WhatsApp: +51987654321 | Email: pedidos@pizzeria.com',
      type: 'textarea',
    },
    {
      step: 5,
      title: '¿Cuáles son tus 2-3 competidores principales?',
      description: 'Para ayudarte a mantener competitividad',
      field: 'competidores',
      placeholder: 'Ej: Pizzería XYZ, Trattoria Don Mario, Pizza Hut',
      type: 'textarea',
    },
  ];

  const currentQuestion = questions.find((q) => q.step === currentStep)!;

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [currentQuestion.field]: value,
    }));
  };

  const handleNext = () => {
    if (currentStep < totalSteps) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleComplete = () => {
    // Guardar en localStorage
    localStorage.setItem('onboarding_data', JSON.stringify(formData));
    
    // Llamar callback si existe
    if (onComplete) {
      onComplete(formData);
    }

    // Aquí puedes redirigir a otra página si lo deseas
    console.log('Onboarding completado:', formData);
  };

  const currentValue = formData[currentQuestion.field as keyof OnboardingData];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4 py-8">
      <div className="w-full max-w-2xl bg-white rounded-lg shadow-xl p-6 md:p-10">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-2">
            ¡Bienvenido a RepuBot! 🤖
          </h1>
          <p className="text-gray-600">
            Cuéntanos sobre tu negocio para personalizar tu asistente de IA
          </p>
        </div>

        {/* Progress Bar */}
        <div className="mb-8">
          <div className="flex justify-between items-center mb-3">
            <span className="text-sm font-semibold text-gray-700">
              Paso {currentStep} de {totalSteps}
            </span>
            <span className="text-sm text-gray-500">{Math.round(progressPercentage)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2.5 overflow-hidden">
            <div
              className="bg-gradient-to-r from-blue-500 to-indigo-600 h-2.5 rounded-full transition-all duration-300"
              style={{ width: `${progressPercentage}%` }}
            />
          </div>
        </div>

        {/* Question Container */}
        <div className="mb-10">
          <h2 className="text-2xl font-bold text-gray-900 mb-3">
            {currentQuestion.title}
          </h2>
          <p className="text-gray-600 mb-6">{currentQuestion.description}</p>

          {/* Input Field */}
          <div className="space-y-4">
            {currentQuestion.type === 'textarea' && (
              <textarea
                value={currentValue}
                onChange={handleInputChange}
                placeholder={currentQuestion.placeholder}
                className="w-full h-32 p-4 border-2 border-gray-300 rounded-lg focus:border-indigo-500 focus:outline-none resize-none transition-colors"
              />
            )}

            {currentQuestion.type === 'select' && (
              <fieldset className="space-y-3">
                {currentQuestion.options?.map((option) => (
                  <label
                    key={option.value}
                    className="flex items-center p-4 border-2 border-gray-300 rounded-lg cursor-pointer hover:border-indigo-500 transition-colors"
                  >
                    <input
                      type="radio"
                      name="tono"
                      value={option.value}
                      checked={currentValue === option.value}
                      onChange={handleInputChange}
                      className="w-4 h-4 text-indigo-600 cursor-pointer"
                    />
                    <span className="ml-3 text-gray-900 font-medium">{option.label}</span>
                  </label>
                ))}
              </fieldset>
            )}
          </div>
        </div>

        {/* Navigation Buttons */}
        <div className="flex gap-4 justify-between">
          <button
            onClick={handleBack}
            disabled={currentStep === 1}
            className={`px-6 py-3 rounded-lg font-semibold transition-all ${
              currentStep === 1
                ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                : 'bg-gray-200 text-gray-900 hover:bg-gray-300'
            }`}
          >
            ← Atrás
          </button>

          {currentStep < totalSteps ? (
            <button
              onClick={handleNext}
              className="px-8 py-3 rounded-lg font-semibold bg-gradient-to-r from-blue-500 to-indigo-600 text-white hover:shadow-lg transition-shadow"
            >
              Siguiente →
            </button>
          ) : (
            <button
              onClick={handleComplete}
              className="px-8 py-3 rounded-lg font-semibold bg-gradient-to-r from-green-500 to-emerald-600 text-white hover:shadow-lg transition-shadow"
            >
              🔗 Conectar cuentas
            </button>
          )}
        </div>

        {/* Footer - Step Indicators */}
        <div className="mt-8 flex justify-center gap-2">
          {Array.from({ length: totalSteps }).map((_, index) => (
            <div
              key={index + 1}
              className={`h-2 w-8 rounded-full transition-all ${
                index + 1 <= currentStep
                  ? 'bg-indigo-600'
                  : 'bg-gray-300'
              }`}
            />
          ))}
        </div>
      </div>
    </div>
  );
};

export default OnboardingFlow;
