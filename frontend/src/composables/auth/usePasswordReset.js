import { ref } from 'vue';
import authService from '@/services/auth.service';

export function usePasswordReset() {
  const correo = ref('');
  const token = ref('');
  const password = ref('');
  const confirmPassword = ref('');
  
  const loading = ref(false);
  const error = ref('');
  const success = ref(false);
  const successMessage = ref('');

  // Valida que el formato del correo electronico sea correcto
  const validarCorreo = (email) => {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
  };

  // Envia la solicitud inicial de restablecimiento con el correo
  const handleRequestReset = async () => {
    error.value = '';
    success.value = false;
    successMessage.value = '';

    if (!correo.value.trim()) {
      error.value = 'Por favor introduzca su correo electronico.';
      return;
    }

    if (!validarCorreo(correo.value.trim())) {
      error.value = 'El formato del correo electronico no es valido.';
      return;
    }

    loading.value = true;
    try {
      await authService.requestPasswordReset(correo.value.trim());
      success.value = true;
      successMessage.value = 'Se ha enviado un enlace de recuperacion a su correo electronico.';
    } catch (err) {
      error.value = err.response?.data?.detail || 'Error al solicitar la recuperacion de contrasena.';
    } finally {
      loading.value = false;
    }
  };

  // Confirma el cambio de contrasena utilizando el token de verificacion
  const handleConfirmReset = async () => {
    error.value = '';
    success.value = false;
    successMessage.value = '';

    if (!token.value || !password.value || !confirmPassword.value) {
      error.value = 'Por favor complete todos los campos.';
      return;
    }

    if (password.value !== confirmPassword.value) {
      error.value = 'Las contrasenas no coinciden.';
      return;
    }

    if (password.value.length < 6) {
      error.value = 'La contrasena debe tener al menos 6 caracteres.';
      return;
    }

    loading.value = true;
    try {
      await authService.confirmPasswordReset(token.value, password.value);
      success.value = true;
      successMessage.value = 'Su contrasena ha sido restablecida con exito. Ya puede iniciar sesion.';
    } catch (err) {
      error.value = err.response?.data?.detail || 'El token es invalido o ha expirado.';
    } finally {
      loading.value = false;
    }
  };

  return {
    correo,
    token,
    password,
    confirmPassword,
    loading,
    error,
    success,
    successMessage,
    handleRequestReset,
    handleConfirmReset,
  };
}
export default usePasswordReset;
