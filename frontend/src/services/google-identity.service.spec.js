import { afterEach, describe, expect, it, vi } from 'vitest';
import {
  loadGoogleIdentity,
  renderGoogleButton,
} from '@/services/google-identity.service';

const createGoogleApi = () => ({
  initialize: vi.fn(),
  renderButton: vi.fn(),
});

afterEach(() => {
  delete window.google;
  document.getElementById('google-identity-services')?.remove();
  vi.restoreAllMocks();
});

describe('google-identity.service', () => {
  it('rechaza la inicializacion cuando falta el ID de cliente', async () => {
    const element = document.createElement('div');

    await expect(renderGoogleButton(element, vi.fn(), '')).rejects.toThrow(
      'El inicio con Google no esta configurado',
    );
  });

  it('reutiliza la API cuando Google Identity Services ya esta cargado', async () => {
    const googleApi = createGoogleApi();
    window.google = { accounts: { id: googleApi } };

    await expect(loadGoogleIdentity()).resolves.toBe(googleApi);
    expect(document.getElementById('google-identity-services')).toBeNull();
  });

  it('espera el evento load antes de resolver el SDK', async () => {
    const promise = loadGoogleIdentity();
    const script = document.getElementById('google-identity-services');
    const googleApi = createGoogleApi();

    expect(script?.src).toBe('https://accounts.google.com/gsi/client');
    window.google = { accounts: { id: googleApi } };
    script.dispatchEvent(new Event('load'));

    await expect(promise).resolves.toBe(googleApi);
  });

  it('informa un error y permite reintentar cuando el SDK no carga', async () => {
    const promise = loadGoogleIdentity();
    const script = document.getElementById('google-identity-services');

    script.dispatchEvent(new Event('error'));

    await expect(promise).rejects.toThrow('No se pudo cargar Google Identity Services');
    expect(document.getElementById('google-identity-services')).toBeNull();
  });

  it('configura el cliente, renderiza el boton y entrega la credencial', async () => {
    const googleApi = createGoogleApi();
    const onCredential = vi.fn();
    const element = document.createElement('div');
    window.google = { accounts: { id: googleApi } };

    await renderGoogleButton(element, onCredential, 'client-id-de-prueba');

    expect(googleApi.initialize).toHaveBeenCalledWith(expect.objectContaining({
      client_id: 'client-id-de-prueba',
      callback: expect.any(Function),
    }));
    expect(googleApi.renderButton).toHaveBeenCalledWith(
      element,
      expect.objectContaining({ width: 380, text: 'continue_with' }),
    );

    const callback = googleApi.initialize.mock.calls[0][0].callback;
    callback({ credential: 'id-token-de-prueba' });
    expect(onCredential).toHaveBeenCalledWith('id-token-de-prueba');
  });
});
