import { flushPromises, mount } from '@vue/test-utils';
import { createPinia, setActivePinia } from 'pinia';
import { createMemoryHistory, createRouter } from 'vue-router';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import CampusTecnologicoView from '@/views/espacios/CampusTecnologicoView.vue';
import CroquisPiso from '@/components/espacios/CroquisPiso.vue';
import BaseSelect from '@/components/selects/BaseSelect.vue';
import edificiosService from '@/services/edificios.service';
import espaciosService from '@/services/espacios.service';
import espaciosUsuariosService from '@/services/espacios-usuarios.service';
import localesService from '@/services/locales.service';
import { useAuthStore } from '@/stores/auth';

vi.mock('@/services/espacios.service', () => ({
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
    guardarCroquisPiso: vi.fn(),
  },
}));

vi.mock('@/services/locales.service', () => ({
  default: {
    listar: vi.fn(),
    crear: vi.fn(),
    actualizar: vi.fn(),
    desactivar: vi.fn(),
  },
}));

vi.mock('@/services/espacios-usuarios.service', () => ({
  default: {
    listar: vi.fn(),
    crear: vi.fn(),
    actualizar: vi.fn(),
    eliminar: vi.fn(),
    obtenerOpciones: vi.fn(),
  },
}));

const mockLocales = [
  { id: 1, codigo: 'LOC-01', nombre: 'Sede Central', ciudad: 'Huánuco', tipo: 'campus', activo: true },
];

const mockEdificios = [
  {
    id: 10,
    codigo: 'PAB-A',
    nombre: 'Pabellón A',
    local_id: 1,
    activo: true,
    configuracion_croquis: {
      pisos: {
        '1': { filas: 2, columnas: 4, ambientes: [{ espacio_id: 101, fila: 1, columna: 1, ancho: 1, alto: 1 }], pasillos: [] },
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
    piso: '1',
    cantidad_equipos: 12,
    resumen_equipos: {},
    activo: true,
    encargados_directos: [],
    encargados_heredados: [],
  },
];

const mockUsuariosOpciones = {
  usuarios: [
    { id: 5, nombre: 'Ana', apellido: 'Técnica', rol: 'tecnico', correo: 'ana@kairos.pe' },
    { id: 8, nombre: 'Pedro', apellido: 'Supervisor', rol: 'responsable', correo: 'pedro@kairos.pe' },
    { id: 12, nombre: 'Lucía', apellido: 'Docente', rol: 'docente', correo: 'lucia@kairos.pe' },
  ],
};

describe('Adversarial View Integration: CampusTecnologicoView In-Situ Technician Modal', () => {
  let router;
  let pinia;

  beforeEach(async () => {
    vi.clearAllMocks();
    pinia = createPinia();
    setActivePinia(pinia);

    localesService.listar.mockResolvedValue({ results: structuredClone(mockLocales) });
    edificiosService.listar.mockResolvedValue({ results: structuredClone(mockEdificios) });
    espaciosService.listar.mockResolvedValue({ results: structuredClone(mockEspacios) });
    espaciosUsuariosService.listar.mockResolvedValue({ results: [] });
    espaciosUsuariosService.obtenerOpciones.mockResolvedValue(structuredClone(mockUsuariosOpciones));
    espaciosUsuariosService.crear.mockResolvedValue({ id: 99 });
    espaciosUsuariosService.actualizar.mockResolvedValue({ id: 99 });

    router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/espacios/mapa', component: CampusTecnologicoView },
        { path: '/espacios', component: { template: '<div>Tradicional</div>' } },
        { path: '/espacios/:id', component: { render: () => null } },
      ],
    });
  });

  const mountView = async (initialQuery = 'local=1&pabellon=10&piso=1', role = 'admin') => {
    useAuthStore().user = { id: 1, rol: role };
    await router.push(`/espacios/mapa?${initialQuery}`);
    await router.isReady();

    const wrapper = mount(CampusTecnologicoView, {
      global: {
        plugins: [pinia, router],
        stubs: {
          RouterLink: { template: '<a><slot /></a>' },
          Teleport: true,
        },
      },
    });

    await flushPromises();
    return wrapper;
  };

  it('oculta la ruta en el mapa inicial y mantiene el regreso desde niveles internos', async () => {
    const wrapper = await mountView('');
    expect(wrapper.find('[aria-label="Ubicación actual"]').exists()).toBe(false);

    await router.push('/espacios/mapa?ciudad=Hu%C3%A1nuco');
    await flushPromises();
    expect(wrapper.get('[aria-label="Ubicación actual"]').text()).toContain('Ciudades');
  });

  it('conserva la ubicación al cambiar del mapa a Tradicional', async () => {
    const wrapper = await mountView('local=1&pabellon=10&piso=1');
    await wrapper.findAll('[aria-label="Vista de espacios"] button')[1].trigger('click');
    await flushPromises();
    expect(router.currentRoute.value.path).toBe('/espacios');
    expect(router.currentRoute.value.query).toMatchObject({ ciudad: 'Huánuco', sede: '1', edificio: '10' });
  });

  it('renderiza CroquisPiso y abre modal de asignacion in-situ al emitir assign-technician en piso sin encargado', async () => {
    const wrapper = await mountView('local=1&pabellon=10&piso=1', 'admin');
    expect(wrapper).toBeDefined();

    const croquis = wrapper.findComponent(CroquisPiso);
    expect(croquis.exists()).toBe(true);
    expect(croquis.props('canEdit')).toBe(true);

    // El piso no tiene tecnico asignado -> muestra estado vacio
    expect(croquis.find('[data-testid="floor-technician-empty"]').exists()).toBe(true);

    // Hacemos click en Asignar dentro de CroquisPiso
    const assignBtn = croquis.find('[data-testid="assign-floor-technician"]');
    expect(assignBtn.exists()).toBe(true);
    await assignBtn.trigger('click');
    await flushPromises();

    // El modal de CampusTecnologicoView debe haberse abierto
    expect(wrapper.text()).toContain('Asignar técnico de piso');
    expect(wrapper.text()).toContain('Pabellón A · Piso 1');

    // Seleccionamos un tecnico via BaseSelect y enviamos
    const userSelect = wrapper.findAllComponents(BaseSelect).find((c) => c.props('id') === 'floor-technician-user');
    expect(userSelect).toBeDefined();
    userSelect.vm.$emit('update:modelValue', 5);
    await flushPromises();

    const form = wrapper.find('#technician-form');
    expect(form.exists()).toBe(true);
    await form.trigger('submit');
    await flushPromises();

    expect(espaciosUsuariosService.crear).toHaveBeenCalledWith({
      usuario_id: 5,
      tipo_responsabilidad: 'tecnico',
      activo: true,
      ambito: 'piso',
      local_id: 1,
      edificio_id: 10,
      piso: '1',
      espacio_id: null,
    });
  });

  it('abre modal con titulo "Cambiar técnico de piso" cuando el piso ya tiene encargado', async () => {
    // Simulamos que el piso ya tiene una asignacion activa
    espaciosUsuariosService.listar.mockResolvedValue({
      results: [
        {
          id: 50,
          usuario_id: 8,
          usuario: { id: 8, nombre: 'Pedro', apellido: 'Supervisor', nombre_completo: 'Pedro Supervisor', correo: 'pedro@kairos.pe' },
          tipo_responsabilidad: 'responsable',
          tipo_responsabilidad_display: 'Responsable',
          ambito: 'piso',
          piso: '1',
          edificio_id: 10,
          local_id: 1,
          activo: true,
          badge_texto: 'Encargado Piso 1 · Pabellón A',
        },
      ],
    });

    const wrapper = await mountView('local=1&pabellon=10&piso=1', 'admin');
    const croquis = wrapper.findComponent(CroquisPiso);

    // Verificamos badge del piso
    const badge = croquis.find('[data-testid="floor-technician-badge"]');
    expect(badge.exists()).toBe(true);
    expect(badge.text()).toContain('Pedro Supervisor');

    // Click en "Cambiar"
    const editBtn = croquis.find('[data-testid="edit-floor-technician"]');
    expect(editBtn.exists()).toBe(true);
    await editBtn.trigger('click');
    await flushPromises();

    expect(wrapper.text()).toContain('Cambiar técnico de piso');

    // Enviar cambio
    const form = wrapper.find('#technician-form');
    await form.trigger('submit');
    await flushPromises();

    expect(espaciosUsuariosService.actualizar).toHaveBeenCalledWith(50, expect.objectContaining({
      usuario_id: 8,
      tipo_responsabilidad: 'responsable',
      ambito: 'piso',
      local_id: 1,
      edificio_id: 10,
      piso: '1',
    }));
  });

  it('restringe la vista a solo lectura cuando el usuario tiene rol tecnico (canEdit: false)', async () => {
    const wrapper = await mountView('local=1&pabellon=10&piso=1', 'tecnico');
    const croquis = wrapper.findComponent(CroquisPiso);

    expect(croquis.props('canEdit')).toBe(false);
    expect(croquis.find('[data-testid="assign-floor-technician"]').exists()).toBe(false);
    expect(croquis.find('[data-testid="edit-floor-technician"]').exists()).toBe(false);
    expect(wrapper.find('button[aria-label="Editar local"]').exists()).toBe(false);
  });

  it('muestra toast de error si la API rechaza la asignacion con 403', async () => {
    espaciosUsuariosService.crear.mockRejectedValueOnce({
      response: {
        status: 403,
        data: { detail: 'No tienes autorización para asignar encargados en esta sede territorial.' },
      },
    });

    const wrapper = await mountView('local=1&pabellon=10&piso=1', 'admin');
    const croquis = wrapper.findComponent(CroquisPiso);

    await croquis.find('[data-testid="assign-floor-technician"]').trigger('click');
    await flushPromises();

    const userSelect = wrapper.findAllComponents(BaseSelect).find((c) => c.props('id') === 'floor-technician-user');
    expect(userSelect).toBeDefined();
    userSelect.vm.$emit('update:modelValue', 5);
    await flushPromises();

    const form = wrapper.find('#technician-form');
    await form.trigger('submit');
    await flushPromises();

    expect(wrapper.text()).toContain('No tienes autorización para asignar encargados en esta sede territorial.');
  });
});
