import api from '@/services/api';

const authService = {
  // Realiza el inicio de sesion local con correo y contrasena
  async login(correo, password) {
    const response = await api.post('/api/v1/auth/login/', { correo, password });
    return response.data;
  },

  // Realiza el inicio de sesion federado con el ID Token de Google
  async loginGoogle(token) {
    const response = await api.post('/api/v1/auth/google/', { token });
    return response.data;
  },

  // Solicita el restablecimiento de contrasena enviando el correo electronico
  async requestPasswordReset(correo) {
    const response = await api.post('/api/v1/auth/password-reset/', { correo });
    return response.data;
  },

  // Confirma el cambio de contrasena utilizando el token recibido y la nueva contrasena
  async confirmPasswordReset(token, password) {
    const response = await api.post('/api/v1/auth/password-reset-confirm/', { token, password });
    return response.data;
  }
};

export default authService;
