/**
 * Mock Authentication System
 * Almacena usuarios y datos temporalmente en localStorage
 * Permite probar el flujo sin conexión a BD
 */

// ============================================
// USUARIOS DEMO PRECARGADOS
// ============================================
const DEMO_USERS = [
  {
    id: 'user-1',
    email: 'demo@example.com',
    password: 'demo123',
    nombre: 'Usuario Demo',
    apellido: 'Prueba',
    token: 'demo-token-1',
    onboardingCompleted: true,
  },
  {
    id: 'user-2',
    email: 'test@example.com',
    password: 'test123',
    nombre: 'Test',
    apellido: 'Usuario',
    token: 'demo-token-2',
    onboardingCompleted: false,
  },
];

// ============================================
// NEGOCIOS DEMO PRECARGADOS
// ============================================
const DEMO_BUSINESSES = [
  {
    id: 'biz-1',
    userId: 'user-1',
    razonSocial: 'Tech Solutions S.A.',
    ruc: '20123456789',
    pais: 'PE',
    ciudad: 'Lima',
    direccion: 'Av. Principal 123',
    sector: 'tecnologia',
    pagina: 'https://techsolutions.com',
    instagram: '@techsolutions',
    facebook: 'techsolutions',
    createdAt: new Date('2026-05-01'),
  },
];

// ============================================
// INICIALIZAR DATOS EN LOCALSTORAGE
// ============================================
function initializeMockData() {
  const users = localStorage.getItem('mock_users');
  const businesses = localStorage.getItem('mock_businesses');

  if (!users) {
    localStorage.setItem('mock_users', JSON.stringify(DEMO_USERS));
  }

  if (!businesses) {
    localStorage.setItem('mock_businesses', JSON.stringify(DEMO_BUSINESSES));
  }
}

// Inicializar al cargar
initializeMockData();

// ============================================
// FUNCIONES DE AUTENTICACIÓN
// ============================================

/**
 * Registrar nuevo usuario
 */
export const registerUser = (email, password, nombre, apellido) => {
  const users = JSON.parse(localStorage.getItem('mock_users') || '[]');

  // Verificar si usuario ya existe
  if (users.some((u) => u.email === email)) {
    return {
      success: false,
      error: 'El email ya está registrado',
    };
  }

  // Crear nuevo usuario
  const newUser = {
    id: `user-${Date.now()}`,
    email,
    password,
    nombre,
    apellido,
    token: `token-${Math.random().toString(36).substr(2, 9)}`,
    onboardingCompleted: false,
    createdAt: new Date().toISOString(),
  };

  users.push(newUser);
  localStorage.setItem('mock_users', JSON.stringify(users));

  return {
    success: true,
    user: {
      id: newUser.id,
      email: newUser.email,
      nombre: newUser.nombre,
      apellido: newUser.apellido,
    },
    token: newUser.token,
  };
};

/**
 * Iniciar sesión
 */
export const loginUser = (email, password) => {
  const users = JSON.parse(localStorage.getItem('mock_users') || '[]');

  const user = users.find((u) => u.email === email && u.password === password);

  if (!user) {
    return {
      success: false,
      error: 'Email o contraseña incorrectos',
    };
  }

  return {
    success: true,
    user: {
      id: user.id,
      email: user.email,
      nombre: user.nombre,
      apellido: user.apellido,
      onboardingCompleted: user.onboardingCompleted,
    },
    token: user.token,
  };
};

/**
 * Guardar datos del onboarding
 */
export const saveOnboarding = (userId, formData) => {
  const users = JSON.parse(localStorage.getItem('mock_users') || '[]');
  const businesses = JSON.parse(
    localStorage.getItem('mock_businesses') || '[]'
  );

  // Encontrar usuario
  const userIndex = users.findIndex((u) => u.id === userId);
  if (userIndex === -1) {
    return {
      success: false,
      error: 'Usuario no encontrado',
    };
  }

  // Marcar onboarding como completado
  users[userIndex].onboardingCompleted = true;
  localStorage.setItem('mock_users', JSON.stringify(users));

  // Crear negocio
  const newBusiness = {
    id: `biz-${Date.now()}`,
    userId,
    razonSocial: formData.razonSocial,
    ruc: formData.ruc,
    pais: formData.pais,
    ciudad: formData.ciudad,
    direccion: formData.direccion,
    sector: formData.sector,
    pagina: formData.pagina,
    instagram: formData.instagram,
    facebook: formData.facebook,
    createdAt: new Date().toISOString(),
  };

  businesses.push(newBusiness);
  localStorage.setItem('mock_businesses', JSON.stringify(businesses));

  return {
    success: true,
    business: newBusiness,
    message: 'Onboarding completado exitosamente',
  };
};

/**
 * Obtener usuario por token
 */
export const getUserByToken = (token) => {
  const users = JSON.parse(localStorage.getItem('mock_users') || '[]');
  const user = users.find((u) => u.token === token);

  if (!user) {
    return null;
  }

  return {
    id: user.id,
    email: user.email,
    nombre: user.nombre,
    apellido: user.apellido,
    onboardingCompleted: user.onboardingCompleted,
  };
};

/**
 * Obtener negocios del usuario
 */
export const getUserBusinesses = (userId) => {
  const businesses = JSON.parse(
    localStorage.getItem('mock_businesses') || '[]'
  );
  return businesses.filter((b) => b.userId === userId);
};

/**
 * Obtener todos los usuarios (para debug)
 */
export const getAllUsers = () => {
  return JSON.parse(localStorage.getItem('mock_users') || '[]');
};

/**
 * Obtener todos los negocios (para debug)
 */
export const getAllBusinesses = () => {
  return JSON.parse(localStorage.getItem('mock_businesses') || '[]');
};

/**
 * Limpiar todos los datos (RESET)
 */
export const clearAllMockData = () => {
  localStorage.removeItem('mock_users');
  localStorage.removeItem('mock_businesses');
  localStorage.removeItem('token');
  initializeMockData();
  return { success: true, message: 'Datos reseteados' };
};

/**
 * Obtener estado de mock (para debug)
 */
export const getMockStatus = () => {
  const users = JSON.parse(localStorage.getItem('mock_users') || '[]');
  const businesses = JSON.parse(
    localStorage.getItem('mock_businesses') || '[]'
  );

  return {
    usersCount: users.length,
    businessesCount: businesses.length,
    users: users.map((u) => ({
      id: u.id,
      email: u.email,
      nombre: u.nombre,
      onboardingCompleted: u.onboardingCompleted,
    })),
    businesses: businesses.map((b) => ({
      id: b.id,
      razonSocial: b.razonSocial,
      userId: b.userId,
    })),
  };
};

export default {
  registerUser,
  loginUser,
  saveOnboarding,
  getUserByToken,
  getUserBusinesses,
  getAllUsers,
  getAllBusinesses,
  clearAllMockData,
  getMockStatus,
};
