const GOOGLE_SCRIPT_ID = 'google-identity-services';
const GOOGLE_SCRIPT_URL = 'https://accounts.google.com/gsi/client';
let googleLoaderPromise;

const getGoogleIdentityApi = () => window.google?.accounts?.id;

// Carga una sola vez el SDK y espera hasta que la API este disponible.
export function loadGoogleIdentity() {
  const loadedApi = getGoogleIdentityApi();
  if (loadedApi) return Promise.resolve(loadedApi);
  if (googleLoaderPromise) return googleLoaderPromise;

  googleLoaderPromise = new Promise((resolve, reject) => {
    let script = document.getElementById(GOOGLE_SCRIPT_ID);

    const handleLoad = () => {
      const googleApi = getGoogleIdentityApi();
      if (googleApi) {
        googleLoaderPromise = undefined;
        resolve(googleApi);
        return;
      }

      googleLoaderPromise = undefined;
      script.remove();
      reject(new Error('Google Identity Services no se inicializo correctamente.'));
    };

    const handleError = () => {
      googleLoaderPromise = undefined;
      script.remove();
      reject(new Error('No se pudo cargar Google Identity Services. Verifique su conexion.'));
    };

    if (!script) {
      script = document.createElement('script');
      script.id = GOOGLE_SCRIPT_ID;
      script.src = GOOGLE_SCRIPT_URL;
      script.async = true;
      script.defer = true;
    }

    script.addEventListener('load', handleLoad, { once: true });
    script.addEventListener('error', handleError, { once: true });

    if (!script.isConnected) document.head.appendChild(script);
  });

  return googleLoaderPromise;
}

// Inicializa el cliente y renderiza el boton oficial de Google.
export async function renderGoogleButton(
  element,
  onCredential,
  clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID,
) {
  if (!clientId) {
    throw new Error('El inicio con Google no esta configurado en este entorno.');
  }

  if (!element) {
    throw new Error('No se encontro el contenedor del boton de Google.');
  }

  const googleApi = await loadGoogleIdentity();
  googleApi.initialize({
    client_id: clientId,
    callback: ({ credential }) => {
      if (credential) onCredential(credential);
    },
  });

  element.replaceChildren();
  googleApi.renderButton(element, {
    theme: 'outline',
    size: 'large',
    width: Math.min(element.clientWidth || 380, 380),
    text: 'continue_with',
    shape: 'rectangular',
    logo_alignment: 'center',
  });
}
