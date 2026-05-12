import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  timeout: 3000, // Timeout corto para caer rápido al mock si BD no está
  headers: { 'Content-Type': 'application/json' },
});

// Inyectar token JWT en cada request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Redirigir al login si la suscripción expiró o el token es inválido
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;

// Función para enviar datos de onboarding al backend
export async function submitOnboarding(onboardingData) {
  try {
    const response = await api.post('/businesses/onboarding', {
      razon_social: onboardingData.businessName,
      tono: onboardingData.perception,
      audiencia_objetivo: onboardingData.targetAudience,
      horario_atencion: onboardingData.scheduleHours,
      whatsapp_numero: onboardingData.contactWhatsapp,
      competidores: onboardingData.competitors,
      principal_desafio: onboardingData.mainChallenge,
      frecuencia_publicacion: onboardingData.postFrequency,
      responde_comentarios: onboardingData.respondComments === 'Sí',
      seguidores_facebook: parseInt(onboardingData.followersFb) || 0,
      seguidores_instagram: parseInt(onboardingData.followersIg) || 0,
      plataforma_importante: onboardingData.importantPlatform,
      impacto_ventas: onboardingData.salesImpact,
    });
    return response.data;
  } catch (error) {
    throw error.response?.data || error.message;
  }
}
