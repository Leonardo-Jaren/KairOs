import { flushPromises, mount } from '@vue/test-utils';
import { createPinia, setActivePinia } from 'pinia';
import { defineComponent, h } from 'vue';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { useEspaciosUsuarios } from '@/composables/espacios/useEspaciosUsuarios';
import { useAuthStore } from '@/stores/auth';

const createDummyService = () => ({
  listar: vi.fn().mockResolvedValue({ count: 0, results: [] }),
  crear: vi.fn().mockResolvedValue({ id: 99 }),
  actualizar: vi.fn().mockResolvedValue({ id: 99 }),
  eliminar: vi.fn().mockResolvedValue(undefined),
  obtenerOpciones: vi.fn().mockResolvedValue({
    locales: [{ id: 1, nombre: 'Sede Central', codigo: 'SC' }, { id: 2, nombre: 'Sede Norte', codigo: 'SN' }],
    edificios: [
      { id: 10, local_id: 1, nombre: 'Pabellón 1', pisos: ['1', '2'] },
      { id: 20, local_id: 2, nombre: 'Pabellón 2', pisos: ['1'] },
    ],
    espacios: [
      { id: 100, edificio_id: 10, local_id: 1, piso: '1', codigo_espacio: 'A-101' },
      { id: 101, edificio_id: 10, local_id: 1, piso: '2', codigo_espacio: 'A-201' },
    ],
  }),
});

const mountComposable = (service = createDummyService(), role = 'admin', optionServices) => {
  let state;
  const pinia = createPinia();
  setActivePinia(pinia);
  useAuthStore().user = { id: 1, nombre: 'Admin Tester', rol: role };
  mount(defineComponent({
    setup() {
      state = optionServices
        ? useEspaciosUsuarios(service, optionServices)
        : useEspaciosUsuarios(service);
      return () => h('div');
    },
  }), { global: { plugins: [pinia] } });
  return state;
};

describe('Adversarial Stress Test: useEspaciosUsuarios (Milestone 3)', () => {
  let service;
  let state;

  beforeEach(async () => {
    service = createDummyService();
    state = mountComposable(service);
    await flushPromises();
  });

  const getLastCreatedPayload = () => {
    const calls = service.crear.mock.calls;
    return calls.length > 0 ? calls[calls.length - 1][0] : null;
  };

  describe('1. Rapid switching of tipo_ambito & Payload Leakage Prevention', () => {
    it('switches espacio -> sede -> edificio -> piso -> sede without leaking subordinate keys in buildPayload', async () => {
      state.openCreate();

      // Step 1: Start in 'espacio' with full data
      state.form.usuario_id = 5;
      state.form.tipo_responsabilidad = 'tecnico';
      state.form.activo = true;
      state.form.local_id = 1;
      state.form.edificio_id = 10;
      state.form.piso = '2';
      state.form.espacio_id = 100;

      let submitResult = await state.submit();
      expect(submitResult).toBe(true);
      let payload = getLastCreatedPayload();
      expect(payload.ambito).toBe('espacio');
      expect(payload.espacio_id).toBe(100);
      expect(payload.local_id).toBeUndefined();
      expect(payload.edificio_id).toBeUndefined();
      expect(payload.piso).toBeUndefined();

      // Step 2: Switch to 'sede'
      state.openCreate();
      state.onAmbitoChange('sede');
      state.form.usuario_id = 5;
      state.form.local_id = 1;
      expect(state.form.tipo_ambito).toBe('sede');
      expect(state.form.edificio_id).toBe('');
      expect(state.form.piso).toBe('');
      expect(state.form.espacio_id).toBe('');

      submitResult = await state.submit();
      expect(submitResult).toBe(true);
      payload = getLastCreatedPayload();
      expect(payload.ambito).toBe('sede');
      expect(payload.local_id).toBe(1);
      expect(payload.edificio_id).toBeNull();
      expect(payload.piso).toBeNull();
      expect(payload.espacio_id).toBeNull();

      // Step 3: Switch to 'edificio'
      state.openCreate();
      state.onAmbitoChange('edificio');
      state.form.usuario_id = 5;
      state.form.local_id = 1;
      state.form.edificio_id = 10;
      expect(state.form.piso).toBe('');
      expect(state.form.espacio_id).toBe('');

      submitResult = await state.submit();
      expect(submitResult).toBe(true);
      payload = getLastCreatedPayload();
      expect(payload.ambito).toBe('edificio');
      expect(payload.local_id).toBe(1);
      expect(payload.edificio_id).toBe(10);
      expect(payload.piso).toBeNull();
      expect(payload.espacio_id).toBeNull();

      // Step 4: Switch to 'piso'
      state.openCreate();
      state.onAmbitoChange('piso');
      state.form.usuario_id = 5;
      state.form.local_id = 1;
      state.form.edificio_id = 10;
      state.form.piso = '2';
      expect(state.form.espacio_id).toBe('');

      submitResult = await state.submit();
      expect(submitResult).toBe(true);
      payload = getLastCreatedPayload();
      expect(payload.ambito).toBe('piso');
      expect(payload.local_id).toBe(1);
      expect(payload.edificio_id).toBe(10);
      expect(payload.piso).toBe('2');
      expect(payload.espacio_id).toBeNull();

      // Step 5: Switch back to 'sede'
      state.openCreate();
      state.onAmbitoChange('sede');
      state.form.usuario_id = 5;
      state.form.local_id = 1;
      expect(state.form.tipo_ambito).toBe('sede');
      expect(state.form.edificio_id).toBe('');
      expect(state.form.piso).toBe('');
      expect(state.form.espacio_id).toBe('');

      submitResult = await state.submit();
      expect(submitResult).toBe(true);
      payload = getLastCreatedPayload();
      expect(payload.ambito).toBe('sede');
      expect(payload.local_id).toBe(1);
      expect(payload.edificio_id).toBeNull();
      expect(payload.piso).toBeNull();
      expect(payload.espacio_id).toBeNull();
    });

    it('defends against payload leakage even if form fields are forcefully dirty without onAmbitoChange', async () => {
      // Test dirty sede
      state.openCreate();
      state.form.usuario_id = 5;
      state.form.local_id = 1;
      state.form.edificio_id = 10;
      state.form.piso = '2';
      state.form.espacio_id = 100;
      state.form.tipo_ambito = 'sede';
      state.form.ambito = 'sede';

      let success = await state.submit();
      expect(success).toBe(true);
      let payload = getLastCreatedPayload();
      expect(payload.ambito).toBe('sede');
      expect(payload.local_id).toBe(1);
      expect(payload.edificio_id).toBeNull();
      expect(payload.piso).toBeNull();
      expect(payload.espacio_id).toBeNull();

      // Test dirty edificio
      state.openCreate();
      state.form.usuario_id = 5;
      state.form.local_id = 1;
      state.form.edificio_id = 10;
      state.form.piso = 'Dirty Piso';
      state.form.espacio_id = 999;
      state.form.tipo_ambito = 'edificio';
      state.form.ambito = 'edificio';

      success = await state.submit();
      expect(success).toBe(true);
      payload = getLastCreatedPayload();
      expect(payload.ambito).toBe('edificio');
      expect(payload.local_id).toBe(1);
      expect(payload.edificio_id).toBe(10);
      expect(payload.piso).toBeNull();
      expect(payload.espacio_id).toBeNull();

      // Test dirty piso
      state.openCreate();
      state.form.usuario_id = 5;
      state.form.local_id = 1;
      state.form.edificio_id = 10;
      state.form.piso = '3';
      state.form.espacio_id = 999;
      state.form.tipo_ambito = 'piso';
      state.form.ambito = 'piso';

      success = await state.submit();
      expect(success).toBe(true);
      payload = getLastCreatedPayload();
      expect(payload.ambito).toBe('piso');
      expect(payload.local_id).toBe(1);
      expect(payload.edificio_id).toBe(10);
      expect(payload.piso).toBe('3');
      expect(payload.espacio_id).toBeNull();
    });

    it('oscillates between all scopes 50 times without any state bleed', async () => {
      const scopes = ['espacio', 'sede', 'edificio', 'piso'];
      for (let i = 0; i < 50; i++) {
        const targetScope = scopes[i % scopes.length];
        state.onAmbitoChange(targetScope);
        expect(state.form.tipo_ambito).toBe(targetScope);

        if (targetScope === 'sede') {
          expect(state.form.edificio_id).toBe('');
          expect(state.form.piso).toBe('');
          expect(state.form.espacio_id).toBe('');
        } else if (targetScope === 'edificio') {
          expect(state.form.piso).toBe('');
          expect(state.form.espacio_id).toBe('');
        } else if (targetScope === 'piso') {
          expect(state.form.espacio_id).toBe('');
        }
      }
    });
  });

  describe('2. Cascading reset when modifying parent entities', () => {
    it('resets edificio_id, piso and espacio_id immediately when parent local changes', async () => {
      state.form.tipo_ambito = 'piso';
      state.form.local_id = 1;
      state.form.edificio_id = 10;
      state.form.piso = '3';
      state.form.espacio_id = 99;
      state.formErrors.edificio_id = 'error edificio';
      state.formErrors.piso = 'error piso';
      state.formErrors.espacio_id = 'error espacio';

      state.onLocalChange(2);

      expect(state.form.local_id).toBe(2);
      expect(state.form.edificio_id).toBe('');
      expect(state.form.piso).toBe('');
      expect(state.form.espacio_id).toBe('');
      expect(state.formErrors.edificio_id).toBeUndefined();
      expect(state.formErrors.piso).toBeUndefined();
      expect(state.formErrors.espacio_id).toBeUndefined();
    });

    it('handles onLocalChange with undefined or empty string safely', async () => {
      state.form.local_id = 1;
      state.form.edificio_id = 10;
      state.form.piso = '3';

      state.onLocalChange(undefined);
      expect(state.form.local_id).toBe(1);
      expect(state.form.edificio_id).toBe('');
      expect(state.form.piso).toBe('');

      state.onLocalChange('');
      expect(state.form.local_id).toBe('');
      expect(state.form.edificio_id).toBe('');
      expect(state.form.piso).toBe('');
    });

    it('resets piso and espacio_id immediately when edificio changes', async () => {
      state.form.tipo_ambito = 'piso';
      state.form.local_id = 1;
      state.form.edificio_id = 10;
      state.form.piso = '3';
      state.form.espacio_id = 99;
      state.formErrors.piso = 'error piso';
      state.formErrors.espacio_id = 'error espacio';

      state.onEdificioChange(11);

      expect(state.form.edificio_id).toBe(11);
      expect(state.form.piso).toBe('');
      expect(state.form.espacio_id).toBe('');
      expect(state.formErrors.piso).toBeUndefined();
      expect(state.formErrors.espacio_id).toBeUndefined();
    });

    it('resets espacio_id immediately when piso changes', async () => {
      state.form.tipo_ambito = 'espacio';
      state.form.piso = '1';
      state.form.espacio_id = 99;
      state.formErrors.espacio_id = 'error espacio';

      state.onPisoChange('2');

      expect(state.form.piso).toBe('2');
      expect(state.form.espacio_id).toBe('');
      expect(state.formErrors.espacio_id).toBeUndefined();
    });
  });

  describe('3. String floor edge cases in validateForm', () => {
    const setupPisoForm = () => {
      state.openCreate();
      state.onAmbitoChange('piso');
      state.form.usuario_id = 2;
      state.form.local_id = 1;
      state.form.edificio_id = 10;
      state.form.tipo_responsabilidad = 'tecnico';
    };

    it('rejects empty string floor', async () => {
      setupPisoForm();

      state.form.piso = '';
      const isValid = await state.submit();
      expect(isValid).toBe(false);
      expect(state.formErrors.piso).toBe('Selecciona o ingresa un piso.');
    });

    it('rejects whitespace-only floor strings', async () => {
      const whitespaceCases = ['   ', ' ', '\t', '\n', '   \t  \n '];
      for (const str of whitespaceCases) {
        setupPisoForm();
        state.form.piso = str;
        const isValid = await state.submit();
        expect(isValid).toBe(false);
        expect(state.formErrors.piso).toBe('Selecciona o ingresa un piso.');
      }
    });

    it('accepts special valid floor names: Sótano -1, PB, Piso 14, Mezzanine', async () => {
      const validPisos = ['Sótano -1', 'PB', 'Piso 14', 'Mezzanine', 'SS-2', 'Nivel 0'];
      for (const pisoName of validPisos) {
        setupPisoForm();
        state.form.piso = pisoName;
        const isValid = await state.submit();
        expect(isValid).toBe(true);
        expect(state.formErrors.piso).toBeUndefined();

        const payload = getLastCreatedPayload();
        expect(payload.piso).toBe(pisoName.trim());
      }
    });

    it('adversarial check: validates floor strings exceeding 20 characters (Django model max_length=20)', async () => {
      setupPisoForm();
      const over20Chars = 'Piso 14 Ala Norte Extrema'; // 25 characters
      state.form.piso = over20Chars;

      const isValid = await state.submit();

      // CHALLENGE / ADVERSARIAL OBSERVATION:
      // In backend migration 0010 & DRF Serializer, piso has max_length=20.
      // If client-side validateForm() does not enforce max_length <= 20,
      // it submits a payload that backend rejects with HTTP 400.
      expect({
        length: over20Chars.length,
        clientSideValid: isValid,
        formError: state.formErrors.piso,
      }).toMatchInlineSnapshot(`
        {
          "clientSideValid": true,
          "formError": undefined,
          "length": 25,
        }
      `);
    });
  });

  describe('4. Null or undefined catalog data tolerance', () => {
    it('evaluates localOptions, filteredEdificios, availablePisos when catalogs are null/undefined', async () => {
      const nullService = createDummyService();
      nullService.obtenerOpciones = vi.fn().mockResolvedValue({
        locales: null,
        edificios: null,
        espacios: null,
      });

      const nullState = mountComposable(nullService);
      await flushPromises();

      expect(() => {
        const _ = nullState.localOptions.value;
      }).not.toThrow();
      expect(nullState.localOptions.value).toEqual([]);

      nullState.form.local_id = 1;
      expect(() => {
        const _ = nullState.filteredEdificios.value;
      }).not.toThrow();
      expect(nullState.filteredEdificios.value).toEqual([]);

      nullState.form.edificio_id = 10;
      expect(() => {
        const _ = nullState.availablePisos.value;
      }).not.toThrow();
      expect(nullState.availablePisos.value).toEqual([]);

      expect(() => {
        const _ = nullState.filteredEspacios.value;
      }).not.toThrow();
      expect(nullState.filteredEspacios.value).toEqual([]);
    });

    it('evaluates localOptions, filteredEdificios, availablePisos when service returns null or undefined completely', async () => {
      const nullService = createDummyService();
      nullService.obtenerOpciones = vi.fn().mockResolvedValue(null);

      const nullState = mountComposable(nullService);
      await flushPromises();

      expect(() => {
        const _ = nullState.localOptions.value;
      }).not.toThrow();
      expect(() => {
        const _ = nullState.filteredEdificios.value;
      }).not.toThrow();
      expect(() => {
        const _ = nullState.availablePisos.value;
      }).not.toThrow();
    });

    it('empirically records failure modes when catalog items contain null or undefined elements', async () => {
      const dirtyService = createDummyService();
      dirtyService.obtenerOpciones = vi.fn().mockResolvedValue({
        locales: [null, undefined, { id: 1, nombre: 'Sede Central', codigo: 'SC' }],
        edificios: [null, undefined, { id: 10, local_id: 1, nombre: 'Pabellón 1', pisos: [null, '1', '2', ''] }],
        espacios: [null, undefined, { id: 100, edificio_id: 10, local_id: 1, piso: '1', codigo_espacio: 'A-101' }],
      });

      const dirtyState = mountComposable(dirtyService);
      await flushPromises();

      let localOptionsError = null;
      try {
        const _ = dirtyState.localOptions.value;
      } catch (e) {
        localOptionsError = e.message;
      }

      dirtyState.form.local_id = 1;
      let filteredEdificiosError = null;
      try {
        const _ = dirtyState.filteredEdificios.value;
      } catch (e) {
        filteredEdificiosError = e.message;
      }

      dirtyState.form.edificio_id = 10;
      let availablePisosError = null;
      try {
        const _ = dirtyState.availablePisos.value;
      } catch (e) {
        availablePisosError = e.message;
      }

      expect({
        localOptionsError,
        filteredEdificiosError,
        availablePisosError,
      }).toEqual({
        localOptionsError: "Cannot read properties of null (reading 'id')",
        filteredEdificiosError: "Cannot read properties of null (reading 'local_id')",
        availablePisosError: "Cannot read properties of null (reading 'id')",
      });
    });

    it('empirically tests fallback optionServices when results is null', async () => {
      const serviceWithoutOpciones = {
        listar: vi.fn().mockResolvedValue({ count: 0, results: [] }),
        crear: vi.fn(),
        actualizar: vi.fn(),
        eliminar: vi.fn(),
        // No obtenerOpciones -> triggers fallback
      };

      const optionServicesNull = {
        locales: { listar: vi.fn().mockResolvedValue({ results: null }) },
        edificios: { listar: vi.fn().mockResolvedValue({ results: null }) },
      };

      const fallbackState = mountComposable(serviceWithoutOpciones, 'admin', optionServicesNull);
      await flushPromises();

      let localOptionsError = null;
      try {
        const _ = fallbackState.localOptions.value;
      } catch (e) {
        localOptionsError = e.message;
      }

      expect(localOptionsError).toContain('is not a function');
    });
  });
});
