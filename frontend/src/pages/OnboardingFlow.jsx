import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { submitOnboarding } from '../api/client';
import * as mockAuth from '../utils/mockAuth';

export default function OnboardingFlow() {
  const navigate = useNavigate();
  const [currentSection, setCurrentSection] = useState(0);
  const [formData, setFormData] = useState({
    businessName: '',
    perception: '',
    targetAudience: '',
    scheduleHours: '',
    contactWhatsapp: '',
    competitors: '',
    mainChallenge: '',
    postFrequency: '',
    respondComments: '',
    followersFb: '',
    followersIg: '',
    importantPlatform: '',
    salesImpact: '',
    facebookConnected: false,
    instagramConnected: false,
  });

  const [errors, setErrors] = useState({});
  const [showOAuthSuccess, setShowOAuthSuccess] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState('');

  // Definir las secciones
  const sections = [
    {
      title: 'Información del negocio',
      description: 'Cuéntanos sobre tu negocio',
      questions: [
        {
          id: 'businessName',
          label: '¿Cuál es el nombre de tu negocio?',
          type: 'text',
          required: true,
          placeholder: 'Ej: Cevichería El Mar',
        },
        {
          id: 'perception',
          label: '¿Cómo quieres que te perciban?',
          type: 'radio',
          required: true,
          options: [
            { value: 'cercano', label: '🤝 Cercano y amigable' },
            { value: 'profesional', label: '💼 Profesional y formal' },
            { value: 'divertido', label: '🎉 Divertido y dinámico' },
          ],
        },
        {
          id: 'targetAudience',
          label: '¿Quién es tu público objetivo?',
          type: 'text',
          required: true,
          placeholder: 'Ej: Familias, jóvenes 18-35, turistas',
        },
      ],
    },
    {
      title: 'Información de contacto',
      description: 'Cómo tus clientes pueden comunicarse contigo',
      questions: [
        {
          id: 'scheduleHours',
          label: '¿Cuál es tu horario de atención?',
          type: 'text',
          required: true,
          placeholder: 'Ej: Lun-Dom 11am-10pm',
        },
        {
          id: 'contactWhatsapp',
          label: '¿Cuál es tu WhatsApp?',
          type: 'text',
          required: true,
          placeholder: 'Ej: +51 999 888 777',
        },
        {
          id: 'competitors',
          label: '¿Quiénes son tus principales competidores?',
          type: 'text',
          required: true,
          placeholder: 'Ej: Cevichería X, Restaurante Y',
        },
      ],
    },
    {
      title: 'Estado actual',
      description: 'Cómo está tu presencia digital hoy',
      questions: [
        {
          id: 'mainChallenge',
          label: '¿Cuál es tu principal desafío en redes?',
          type: 'radio',
          required: true,
          options: [
            { value: 'no-time', label: '⏰ No tengo tiempo para publicar' },
            { value: 'no-respond', label: '💬 No puedo responder comentarios' },
            { value: 'no-ideas', label: '💡 Me faltan ideas de contenido' },
            { value: 'low-engagement', label: '📉 Bajo engagement' },
          ],
        },
        {
          id: 'postFrequency',
          label: '¿Con qué frecuencia publicas?',
          type: 'radio',
          required: true,
          options: [
            { value: 'daily', label: '📱 Diariamente' },
            { value: 'weekly', label: '📅 Semanalmente' },
            { value: 'few-times', label: '🔔 Pocas veces al mes' },
            { value: 'rarely', label: '😴 Muy raramente' },
          ],
        },
        {
          id: 'respondComments',
          label: '¿Qué tan rápido respondes comentarios?',
          type: 'radio',
          required: true,
          options: [
            { value: 'minutes', label: '⚡ Minutos' },
            { value: 'hours', label: '⏱️ Horas' },
            { value: 'days', label: '📍 Días' },
            { value: 'weeks', label: '🐢 Semanas o nunca' },
          ],
        },
      ],
    },
    {
      title: 'Tus métricas',
      description: 'Datos sobre tu presencia en redes',
      questions: [
        {
          id: 'followersFb',
          label: '¿Cuántos seguidores tienes en Facebook?',
          type: 'number',
          required: true,
          placeholder: '0',
        },
        {
          id: 'followersIg',
          label: '¿Cuántos seguidores tienes en Instagram?',
          type: 'number',
          required: true,
          placeholder: '0',
        },
        {
          id: 'importantPlatform',
          label: '¿Cuál es tu plataforma más importante?',
          type: 'radio',
          required: true,
          options: [
            { value: 'facebook', label: '👍 Facebook' },
            { value: 'instagram', label: '📸 Instagram' },
            { value: 'google', label: '⭐ Google Maps' },
            { value: 'all-equal', label: '⚖️ Todas igual' },
          ],
        },
      ],
    },
  ];

  // Validar sección actual
  const validateSection = () => {
    const currentSectionQuestions = sections[currentSection].questions;
    const newErrors = {};

    currentSectionQuestions.forEach((question) => {
      if (question.required && !formData[question.id]) {
        newErrors[question.id] = 'Este campo es requerido';
      }
    });

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Manejo de cambios en inputs
  const handleInputChange = (e) => {
    const { name, value, type } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'number' ? (value === '' ? '' : Number(value)) : value,
    }));
    // Limpiar error del campo
    if (errors[name]) {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
  };

  // Manejo de cambios en radio buttons
  const handleRadioChange = (questionId, value) => {
    setFormData((prev) => ({
      ...prev,
      [questionId]: value,
    }));
    if (errors[questionId]) {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[questionId];
        return newErrors;
      });
    }
  };

  // Siguiente sección
  const handleNext = () => {
    if (validateSection()) {
      if (currentSection < sections.length) {
        setCurrentSection(currentSection + 1);
        window.scrollTo(0, 0);
      }
    }
  };

  // Sección anterior
  const handlePrevious = () => {
    if (currentSection > 0) {
      setCurrentSection(currentSection - 1);
      window.scrollTo(0, 0);
    }
  };

  // Simular conexión OAuth
  const handleConnectFacebook = () => {
    setFormData((prev) => ({
      ...prev,
      facebookConnected: !prev.facebookConnected,
    }));
    setShowOAuthSuccess(true);
    setTimeout(() => setShowOAuthSuccess(false), 2000);
  };

  const handleConnectInstagram = () => {
    setFormData((prev) => ({
      ...prev,
      instagramConnected: !prev.instagramConnected,
    }));
    setShowOAuthSuccess(true);
    setTimeout(() => setShowOAuthSuccess(false), 2000);
  };

  // Submit final
  const handleSubmit = async () => {
    if (!validateSection()) {
      return;
    }

    setIsSubmitting(true);
    setSubmitError('');

    try {
      // Obtener token y userId
      const token = localStorage.getItem('token');
      const mockMode = localStorage.getItem('mockMode') === 'true';

      if (mockMode) {
        // Usar mock auth (BD no disponible)
        const user = mockAuth.getUserByToken(token);
        if (!user) {
          throw new Error('Usuario no autenticado');
        }

        // Guardar onboarding en mock
        const result = mockAuth.saveOnboarding(user.id, {
          razonSocial: formData.businessName,
          ruc: 'RUC-' + Math.random().toString(36).substr(2, 9),
          pais: 'PE',
          ciudad: formData.targetAudience,
          direccion: formData.mainChallenge,
          sector: 'otros',
          pagina: formData.competitors,
          instagram: formData.followersIg,
          facebook: formData.followersFb,
        });

        if (result.success) {
          alert('¡Bienvenido! Tu onboarding ha sido completado. 🎉\n\n📝 Modo: Almacenamiento Local (BD no disponible)');
          navigate('/dashboard', { replace: true });
        } else {
          throw new Error(result.error);
        }
      } else {
        // Usar API real (BD disponible)
        const result = await submitOnboarding(formData);
        alert('¡Bienvenido! Tu onboarding ha sido completado. 🎉');
        navigate('/dashboard', { replace: true });
      }
    } catch (error) {
      console.error('Error al enviar onboarding:', error);

      // Mostrar error
      const errorMsg =
        typeof error === 'string'
          ? error
          : error?.message ||
            'Error al guardar los datos. Por favor intenta de nuevo.';

      setSubmitError(errorMsg);

      // Scroll al error
      window.scrollTo(0, 0);
    } finally {
      setIsSubmitting(false);
    }
  };

  // Renderizar campo de entrada
  const renderField = (question) => {
    if (question.type === 'text' || question.type === 'number') {
      return (
        <div key={question.id} className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {question.label}
            {question.required && <span className="text-red-500"> *</span>}
          </label>
          <input
            type={question.type}
            name={question.id}
            value={formData[question.id]}
            onChange={handleInputChange}
            placeholder={question.placeholder}
            className={`w-full px-4 py-2.5 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all ${
              errors[question.id]
                ? 'border-red-500 bg-red-50'
                : 'border-gray-300 bg-white'
            }`}
          />
          {errors[question.id] && (
            <p className="text-red-500 text-xs mt-1">{errors[question.id]}</p>
          )}
        </div>
      );
    }

    if (question.type === 'radio') {
      return (
        <div key={question.id} className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-3">
            {question.label}
            {question.required && <span className="text-red-500"> *</span>}
          </label>
          <div className="space-y-2">
            {question.options.map((option) => (
              <label
                key={option.value}
                className="flex items-center cursor-pointer p-3 border rounded-lg hover:bg-blue-50 transition-colors"
                style={{
                  borderColor:
                    formData[question.id] === option.value ? '#2563EB' : '#E5E7EB',
                  backgroundColor:
                    formData[question.id] === option.value ? '#EFF6FF' : 'white',
                }}
              >
                <input
                  type="radio"
                  name={question.id}
                  value={option.value}
                  checked={formData[question.id] === option.value}
                  onChange={() => handleRadioChange(question.id, option.value)}
                  className="w-4 h-4 text-blue-600 cursor-pointer"
                />
                <span className="ml-3 text-sm text-gray-700">{option.label}</span>
              </label>
            ))}
          </div>
          {errors[question.id] && (
            <p className="text-red-500 text-xs mt-2">{errors[question.id]}</p>
          )}
        </div>
      );
    }

    return null;
  };

  // Pantalla actual
  const isOAuthScreen = currentSection === sections.length;
  const progress = ((currentSection + 1) / (sections.length + 1)) * 100;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-white">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-2xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">¡Bienvenido a RepuBot! 🤖</h1>
              <p className="text-gray-600 text-sm mt-1">
                {isOAuthScreen
                  ? 'Conecta tus redes sociales para comenzar'
                  : `Paso ${currentSection + 1} de ${sections.length}`}
              </p>
            </div>
            <div className="text-right">
              <span className="text-3xl font-bold text-blue-600">
                {Math.round(progress)}%
              </span>
            </div>
          </div>

          {/* Barra de progreso */}
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-500"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
        </div>
      </div>

      {/* Error Banner */}
      {submitError && (
        <div className="max-w-2xl mx-auto px-4 py-2">
          <div className="mb-6 p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg">
            <p className="font-semibold">❌ Error</p>
            <p className="text-sm mt-1">{submitError}</p>
          </div>
        </div>
      )}

      {/* Contenido principal */}
      <div className="max-w-2xl mx-auto px-4 py-8">
        {!isOAuthScreen ? (
          // Sección del formulario
          <div className="bg-white rounded-xl shadow-sm p-8 border border-gray-100">
            {/* Título de sección */}
            <div className="mb-8">
              <h2 className="text-2xl font-bold text-gray-900">
                {sections[currentSection].title}
              </h2>
              <p className="text-gray-600 mt-1">
                {sections[currentSection].description}
              </p>
            </div>

            {/* Campos de la sección */}
            <div className="mb-8">
              {sections[currentSection].questions.map((question) =>
                renderField(question)
              )}
            </div>

            {/* Botones de navegación */}
            <div className="flex gap-3 pt-6 border-t border-gray-200">
              <button
                onClick={handlePrevious}
                disabled={currentSection === 0 || isSubmitting}
                className={`flex-1 px-4 py-3 rounded-lg font-medium transition-all ${
                  currentSection === 0 || isSubmitting
                    ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                ← Atrás
              </button>
              <button
                onClick={handleNext}
                disabled={isSubmitting}
                className={`flex-1 px-4 py-3 rounded-lg font-medium transition-all ${
                  isSubmitting
                    ? 'bg-blue-300 text-white cursor-not-allowed'
                    : 'bg-blue-600 text-white hover:bg-blue-700'
                }`}
              >
                {isSubmitting ? 'Enviando...' : 'Siguiente →'}
              </button>
            </div>
          </div>
        ) : (
          // Pantalla OAuth
          <div className="bg-white rounded-xl shadow-sm p-8 border border-gray-100">
            <div className="text-center mb-8">
              <div className="text-5xl mb-4">🔗</div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                Conecta tus redes sociales
              </h2>
              <p className="text-gray-600">
                Para que RepuBot pueda gestionar tus comentarios y mensajes
              </p>
            </div>

            {/* Mensaje de éxito */}
            {showOAuthSuccess && (
              <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
                <p className="text-green-700 text-sm font-medium">
                  ✅ Conexión establecida exitosamente
                </p>
              </div>
            )}

            {/* Conexiones OAuth */}
            <div className="space-y-4 mb-8">
              {/* Facebook */}
              <div className="border border-gray-200 rounded-lg p-6 hover:border-blue-300 transition-all">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="text-4xl">👍</div>
                    <div>
                      <h3 className="font-semibold text-gray-900">Facebook</h3>
                      <p className="text-sm text-gray-600">
                        {formData.facebookConnected
                          ? '✅ Conectado'
                          : 'Conecta tu página de Facebook'}
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={handleConnectFacebook}
                    className={`px-6 py-2.5 rounded-lg font-medium transition-all ${
                      formData.facebookConnected
                        ? 'bg-green-100 text-green-700 hover:bg-green-200'
                        : 'bg-blue-600 text-white hover:bg-blue-700'
                    }`}
                  >
                    {formData.facebookConnected ? 'Desconectar' : 'Conectar'}
                  </button>
                </div>
              </div>

              {/* Instagram */}
              <div className="border border-gray-200 rounded-lg p-6 hover:border-pink-300 transition-all">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="text-4xl">📸</div>
                    <div>
                      <h3 className="font-semibold text-gray-900">Instagram</h3>
                      <p className="text-sm text-gray-600">
                        {formData.instagramConnected
                          ? '✅ Conectado'
                          : 'Conecta tu cuenta de Instagram'}
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={handleConnectInstagram}
                    className={`px-6 py-2.5 rounded-lg font-medium transition-all ${
                      formData.instagramConnected
                        ? 'bg-green-100 text-green-700 hover:bg-green-200'
                        : 'bg-blue-600 text-white hover:bg-blue-700'
                    }`}
                  >
                    {formData.instagramConnected ? 'Desconectar' : 'Conectar'}
                  </button>
                </div>
              </div>
            </div>

            {/* Información adicional */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-8">
              <p className="text-sm text-blue-900">
                <strong>ℹ️ Nota:</strong> Puedes conectar estas plataformas ahora o
                hacerlo después desde tu dashboard de configuración.
              </p>
            </div>

            {/* Botones finales */}
            <div className="flex gap-3">
              <button
                onClick={handlePrevious}
                disabled={isSubmitting}
                className={`flex-1 px-4 py-3 rounded-lg font-medium transition-all ${
                  isSubmitting
                    ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                ← Atrás
              </button>
              <button
                onClick={handleSubmit}
                disabled={isSubmitting}
                className={`flex-1 px-4 py-3 rounded-lg font-medium transition-all ${
                  isSubmitting
                    ? 'bg-blue-300 text-white cursor-not-allowed'
                    : 'bg-blue-600 text-white hover:bg-blue-700'
                }`}
              >
                {isSubmitting ? '⏳ Enviando...' : '✅ Completar onboarding'}
              </button>
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="text-center mt-8 text-sm text-gray-600">
          <p>
            Al continuar, aceptas nuestros{' '}
            <a href="/terms" className="text-blue-600 hover:underline">
              términos de servicio
            </a>{' '}
            y{' '}
            <a href="/privacy" className="text-blue-600 hover:underline">
              política de privacidad
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}
