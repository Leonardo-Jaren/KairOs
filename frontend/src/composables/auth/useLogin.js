import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { renderGoogleButton } from '@/services/google-identity.service';

export function useLogin() {
  const router = useRouter();
  const authStore = useAuthStore();

  const correo = ref('');
  const password = ref('');
  const validationError = ref('');
  const googleButtonElement = ref(null);
  const googleLoading = ref(true);
  const googleError = ref('');

  // Estados reactivos mapeados desde el store de Pinia
  const loading = computed(() => authStore.loading);
  const apiError = computed(() => authStore.error);
  
  // Combina errores de validacion local y respuestas de la API
  const error = computed(() => validationError.value || apiError.value || googleError.value);

  // Valida que el formato del correo electronico sea correcto
  const validarCorreo = (email) => {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
  };

  // Metodo para procesar el inicio de sesion local
  const handleLogin = async () => {
    validationError.value = '';
    
    // Validacion de campos vacios
    if (!correo.value.trim() || !password.value) {
      validationError.value = 'Por favor complete todos los campos.';
      return;
    }

    // Validacion de formato de correo
    if (!validarCorreo(correo.value.trim())) {
      validationError.value = 'El formato del correo electronico no es valido.';
      return;
    }

    try {
      const success = await authStore.login(correo.value.trim(), password.value);
      if (success) {
        // Redirigir al dashboard si las credenciales son correctas
        router.push('/dashboard');
      }
    } catch (err) {
      // El error ya es manejado y expuesto por el Pinia Store
    }
  };

  // Metodo para procesar el inicio de sesion federado con Google
  const handleGoogleLogin = async (token) => {
    validationError.value = '';
    try {
      const success = await authStore.loginGoogle(token);
      if (success) {
        router.push('/dashboard');
      }
    } catch (err) {
      // El error ya es manejado por el store
    }
  };

  // Espera la carga del SDK antes de inicializar el boton de Google.
  const initializeGoogleLogin = async () => {
    googleError.value = '';
    googleLoading.value = true;

    try {
      await renderGoogleButton(googleButtonElement.value, handleGoogleLogin);
    } catch (err) {
      googleError.value = err.message || 'No se pudo inicializar el inicio de sesion con Google.';
    } finally {
      googleLoading.value = false;
    }
  };

  onMounted(initializeGoogleLogin);

  return {
    correo,
    password,
    loading,
    googleButtonElement,
    googleLoading,
    error,
    handleLogin,
    handleGoogleLogin,
    initializeGoogleLogin,
  };
}
export default useLogin;
