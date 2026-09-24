import { flushPromises, mount } from '@vue/test-utils';
import { createPinia, setActivePinia } from 'pinia';
import { createMemoryHistory, createRouter } from 'vue-router';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import EspaciosView from '@/views/espacios/EspaciosView.vue';
import edificiosService from '@/services/edificios.service';
import espaciosService from '@/services/espacios.service';
import espaciosUsuariosService from '@/services/espacios-usuarios.service';
import localesService from '@/services/locales.service';
import { useAuthStore } from '@/stores/auth';

vi.mock('@/services/locales.service', () => ({
  default: {
    listar: vi.fn(),
    crear: vi.fn(),
    actualizar: vi.fn(),
    desactivar: vi.fn(),
  },
}));

vi.mock('@/services/edificios.service', () => ({
  default: {
    listar: vi.fn(),
    crear: vi.fn(),
    actualizar: vi.fn(),
    desactivar: vi.fn(),
  },
}));

vi.mock('@/services/espacios.service', () => ({
  default: {
    listar: vi.fn(),
    obtenerEstadisticas: vi.fn(),
    crear: vi.fn(),
    actualizar: vi.fn(),
    desactivar: vi.fn(),
  },
}));

vi.mock('@/services/espacios-usuarios.service', () => ({
  default: {
    listar: vi.fn(),
    obtenerOpciones: vi.fn(),
    crear: vi.fn(),
    actualizar: vi.fn(),
    eliminar: vi.fn(),
  },
}));

const mockLocales = [
  { id: 1, codigo: 'LOC-01', nombre: 'Campus Central', ciudad: 'Huánuco', tipo: 'campus', activo: true },
  { id: 2, codigo: 'LOC-02', nombre: 'Sede Tingo María', ciudad: 'Tingo María', tipo: 'sede', activo: true },
];

const mockEdificios = [
  {
    id: 10,
    codigo: 'PAB-01',
    nombre: 'Pabellón 1 - Ciencias',
    local_id: 1,
    activo: true,
    configuracion_croquis: {
      pisos: {
        '1': { rows: 4, cols: 8, cells: {} },
        '2': { rows: 4, cols: 8, cells: {} },
      },
    },
  },
];

const mockEspacios = [
  {
    id: 101,
    codigo_espacio: 'LAB-101',
    tipo: 'laboratorio',
    tipo_display: 'Laboratorio',
    edificio_id: 10,
    pabellon: 'Pabellón 1 - Ciencias',
    piso: '1',
    cantidad_equipos: 20,
    resumen_equipos: { en_uso: 18, en_mantenimiento: 2, dañado: 0 },
    activo: true,
    updated_at: '2026-09-20T10:00:00Z',
  },
  {
    id: 102,
    codigo_espacio: 'LAB-201',
    tipo: 'sala_computo',
    tipo_display: 'Sala de cómputo',
    edificio_id: 10,
    pabellon: 'Pabellón 1 - Ciencias',
    piso: '2',
    cantidad_equipos: 15,
    resumen_equipos: { en_uso: 14, en_mantenimiento: 0, dañado: 1 },
    activo: true,
    updated_at: '2026-09-20T10:00:00Z',
  },
];

const mockAsignaciones = [
  {
    id: 301,
    ambito: 'piso',
    edificio_id: 10,
    piso: '2',
    usuario: { id: 5, nombre: 'Javier', apellido: 'Pérez', correo: 'jperez@kairos.edu', rol: 'tecnico' },
    tipo_responsabilidad: 'tecnico',
    tipo_responsabilidad_display: 'Técnico',
    activo: true,
  },
];

const createTestRouter = (initialRoute = '/espacios') => {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/espacios', component: EspaciosView },
      { path: '/espacios/:id', component: { template: '<div>Plano Espacio</div>' } },
      { path: '/espacios/mapa', component: { template: '<div>Mapa</div>' } },
      { path: '/espacios/usuarios', component: { template: '<div>Usuarios</div>' } },
    ],
  });
};

describe('EspaciosView.vue', () => {
  let router;

  beforeEach(() => {
    vi.clearAllMocks();
    localesService.listar.mockResolvedValue({ results: mockLocales });
    edificiosService.listar.mockResolvedValue({ results: mockEdificios });
    espaciosService.listar.mockResolvedValue({ results: mockEspacios, count: 2 });
    espaciosService.obtenerEstadisticas.mockResolvedValue({
      total: 2,
      activos: 2,
      laboratorios: 2,
      equipos: 35,
    });
    espaciosUsuariosService.listar.mockResolvedValue({ results: mockAsignaciones });
    espaciosUsuariosService.obtenerOpciones.mockResolvedValue({
      usuarios: [{ id: 5, nombre: 'Javier', apellido: 'Pérez', rol: 'tecnico', correo: 'jperez@kairos.edu' }],
    });
  });

  const mountView = async (initialPath = '/espacios', role = 'admin') => {
    const pinia = createPinia();
    setActivePinia(pinia);
    useAuthStore().user = { id: 1, nombre: 'Admin', rol: role };

    router = createTestRouter();
    await router.push(initialPath);
    await router.isReady();

    const wrapper = mount(EspaciosView, {
      global: {
        plugins: [pinia, router],
        stubs: {
          RouterLink: false,
          BaseToast: true,
        },
      },
    });
    await flushPromises();
    return wrapper;
  };

  it('renderiza la cabecera con el alternador de Vista Dual y las tarjetas de sedes por defecto', async () => {
    const wrapper = await mountView('/espacios');
    await flushPromises();

    expect(wrapper.text()).toContain('Espacios y Sedes');
    expect(wrapper.text()).toContain('Tradicional');
    expect(wrapper.text()).toContain('Lista');

    // Nivel 1: Ciudades
    expect(wrapper.get('[aria-label="Ciudades disponibles"]').text()).toContain('Huánuco');
    expect(wrapper.get('[aria-label="Ciudades disponibles"]').text()).toContain('Tingo María');
    expect(wrapper.text()).toContain('Nuevo local');
    expect(wrapper.findAll('button').filter((button) => button.text().includes('Nuevo local'))).toHaveLength(1);
    expect(wrapper.get('#search-sedes').exists()).toBe(true);
    expect(wrapper.find('[aria-label="Ubicación actual"]').exists()).toBe(false);
  });

  it('permite alternar entre la vista Tradicional y la vista Lista', async () => {
    const wrapper = await mountView('/espacios');
    await flushPromises();

    // Cambiar a Vista Inventario
    const tabs = wrapper.findAll('[aria-label="Vista de espacios"] button');
    expect(tabs).toHaveLength(3);
    await tabs[2].trigger('click');
    await flushPromises();

    expect(router.currentRoute.value.query.vista).toBe('inventario');
    expect(wrapper.text()).toContain('LAB-101');
    expect(wrapper.text()).toContain('LAB-201');
    expect(wrapper.text()).toContain('Todos los tipos');
    expect(wrapper.get('[aria-label="Espacios disponibles"]').text()).toContain('LAB-101');
  });

  it('conserva la ciudad y el local al abrir el mapa desde Tradicional', async () => {
    const wrapper = await mountView('/espacios?ciudad=Hu%C3%A1nuco&sede=1&edificio=10');
    await flushPromises();
    await wrapper.findAll('[aria-label="Vista de espacios"] button')[0].trigger('click');
    await flushPromises();
    expect(router.currentRoute.value.path).toBe('/espacios/mapa');
    expect(router.currentRoute.value.query).toMatchObject({ ciudad: 'Huánuco', local: '1', pabellon: '10' });
  });

  it('respeta el historial al recorrer ciudades y locales', async () => {
    const wrapper = await mountView('/espacios');
    await flushPromises();
    await wrapper.get('[aria-label="Ciudades disponibles"] button').trigger('click');
    await flushPromises();
    expect(router.currentRoute.value.query.ciudad).toBe('Huánuco');
    await wrapper.get('[aria-label="Lista de locales"] [role="button"]').trigger('click');
    await flushPromises();
    expect(router.currentRoute.value.query.sede).toBe('1');
    router.back();
    await flushPromises();
    expect(router.currentRoute.value.query.ciudad).toBe('Huánuco');
    expect(router.currentRoute.value.query.sede).toBeUndefined();
  });

  it('navega en drill-down desde Sede hacia Pabellones y luego a Pisos Verticales', async () => {
    const wrapper = await mountView('/espacios');
    await flushPromises();

    // 1. Seleccionar ciudad y después el local.
    await wrapper.get('[aria-label="Ciudades disponibles"] button').trigger('click');
    await flushPromises();
    const sedeCards = wrapper.findAll('[aria-label="Lista de locales"] [role="button"]');
    expect(sedeCards.length).toBeGreaterThan(0);
    await sedeCards[0].trigger('click');
    await flushPromises();

    expect(router.currentRoute.value.query.sede).toBe('1');
    expect(wrapper.get('[aria-label="Ubicación actual"]').text()).toContain('Campus Central');
    expect(wrapper.text()).toContain('Pabellón 1 - Ciencias');
    expect(wrapper.text()).toContain('Nuevo pabellón');

    // 2. Clic en Pabellón 1 (Edificio 10)
    const buildingCards = wrapper.findAll('[aria-label="Lista de pabellones"] [role="button"]');
    expect(buildingCards.length).toBeGreaterThan(0);
    await buildingCards[0].trigger('click');
    await flushPromises();

    expect(router.currentRoute.value.query.edificio).toBe('10');

    // 3. Nivel 3: Plantas Verticales ordenadas de arriba a abajo (Piso 2, Piso 1)
    expect(wrapper.text()).toContain('Plantas verticales');
    expect(wrapper.text()).toContain('Piso 2');
    expect(wrapper.text()).toContain('Piso 1');

    // Telemetría del piso 2 (14 operativos, 1 incidencia)
    expect(wrapper.text()).toContain('14 operativos');
    expect(wrapper.text()).toContain('1 incidencias');

    // Técnico responsable asignado al piso 2
    expect(wrapper.text()).toContain('Javier Pérez');

    // El croquis aparece directamente en cada piso.
    expect(wrapper.get('[aria-label="Plantas verticales"]').text()).toContain('LAB-201');
    expect(wrapper.text()).toContain('Ambiente');
    expect(wrapper.text()).toContain('Editar distribución en Mapa');

    // 4. Regresar a ciudades desde la ruta de ubicación.
    const breadcrumbSedes = wrapper.get('[aria-label="Ubicación actual"] button');
    await breadcrumbSedes.trigger('click');
    await flushPromises();

    expect(router.currentRoute.value.query.sede).toBeUndefined();
    expect(wrapper.get('[aria-label="Ciudades disponibles"]').text()).toContain('Huánuco');
    expect(wrapper.get('[aria-label="Ciudades disponibles"]').text()).toContain('Tingo María');
  });

  it('muestra los croquis de todos los pisos sin abrir un modal', async () => {
    const wrapper = await mountView('/espacios?sede=1&edificio=10');
    await flushPromises();

    const floors = wrapper.get('[aria-label="Plantas verticales"]');
    expect(floors.findAll('section').length).toBeGreaterThanOrEqual(2);
    expect(floors.text()).toContain('LAB-101');
    expect(floors.text()).toContain('LAB-201');
    expect(document.body.querySelector('[aria-label="Croquis 2D del piso"]')).toBeNull();
  });
});
