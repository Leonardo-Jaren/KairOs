import { mount } from '@vue/test-utils';
import { describe, expect, it } from 'vitest';
import PabellonSelector from '@/components/espacios/PabellonSelector.vue';

const sampleLocal = {
  id: 2,
  codigo: 'HCO-ESPERANZA',
  nombre: 'Sede La Esperanza',
  tipoLabel: 'Sede Académica',
  descripcion: 'Campus de ingeniería y ciencias con alta capacidad de cómputo.',
};

const sampleBuildings = [
  {
    id: 10,
    codigo: 'PAB-ESP-A',
    nombre: 'Pabellón Académico',
    descripcion: 'Aulas y laboratorios principales.',
    pisos: ['1', '2'],
    spaces: [
      { id: 101, codigo_espacio: 'LAB-201', tipo: 'laboratorio', tipo_display: 'Laboratorio', piso: '2', cantidad_equipos: 12 },
      { id: 102, codigo_espacio: 'LAB-202', tipo: 'sala_computo', tipo_display: 'Sala de cómputo', piso: '1', cantidad_equipos: 10 },
    ],
    laboratorios: [{ id: 101 }, { id: 102 }],
    aulas: [],
    equipos: 22,
    alertas: 0,
  },
  {
    id: 20,
    codigo: 'PAB-ESP-B',
    nombre: 'Pabellón Administrativo',
    descripcion: 'Oficinas y atención.',
    pisos: ['1'],
    spaces: [
      { id: 201, codigo_espacio: 'ADM-101', tipo: 'oficina', tipo_display: 'Oficina', piso: '1', cantidad_equipos: 4 },
    ],
    laboratorios: [],
    aulas: [],
    equipos: 4,
    alertas: 0,
  },
];

describe('PabellonSelector', () => {
  it('renderiza la cabecera del local con sus métricas y bloques', () => {
    const wrapper = mount(PabellonSelector, {
      props: {
        local: sampleLocal,
        buildings: sampleBuildings,
        canEdit: true,
      },
    });

    expect(wrapper.text()).toContain('Sede La Esperanza');
    expect(wrapper.text()).toContain('HCO-ESPERANZA');
    expect(wrapper.text()).toContain('Pabellón Académico');
    expect(wrapper.text()).toContain('Pabellón Administrativo');
    expect(wrapper.text()).toContain('22 equipos');
    expect(wrapper.text()).toContain('2 pabellones disponibles');
  });

  it('emite select al pulsar el botón de recorrer pabellón', async () => {
    const wrapper = mount(PabellonSelector, {
      props: {
        local: sampleLocal,
        buildings: sampleBuildings,
      },
    });

    const recorrerButtons = wrapper.findAll('button').filter((b) => b.text().includes('Recorrer pabellón'));
    expect(recorrerButtons.length).toBe(2);

    await recorrerButtons[0].trigger('click');
    expect(wrapper.emitted('select')?.[0]).toEqual([10]);
  });

  it('emite edit y delete para administradores', async () => {
    const wrapper = mount(PabellonSelector, {
      props: {
        local: sampleLocal,
        buildings: sampleBuildings,
        canEdit: true,
      },
    });

    const editBtn = wrapper.get('button[aria-label="Editar pabellón"]');
    await editBtn.trigger('click');
    expect(wrapper.emitted('edit')?.[0]).toEqual([sampleBuildings[0]]);

    const deleteBtn = wrapper.get('button[aria-label="Desactivar pabellón"]');
    await deleteBtn.trigger('click');
    expect(wrapper.emitted('delete')?.[0]).toEqual([sampleBuildings[0]]);
  });

  it('muestra el directorio de ambientes y emite select-space al hacer clic en un espacio', async () => {
    const wrapper = mount(PabellonSelector, {
      props: {
        local: sampleLocal,
        buildings: sampleBuildings,
      },
    });

    expect(wrapper.find('[aria-label="Directorio de ambientes en el local"]').exists()).toBe(true);
    expect(wrapper.text()).toContain('LAB-201');
    expect(wrapper.text()).toContain('LAB-202');

    const spaceButton = wrapper.findAll('[aria-label="Directorio de ambientes en el local"] button')[0];
    await spaceButton.trigger('click');
    expect(wrapper.emitted('select-space')?.[0]).toEqual([sampleBuildings[0].spaces[0]]);
  });

  it('muestra estado vacío amigable e invita a agregar pabellón cuando la lista está vacía', async () => {
    const wrapper = mount(PabellonSelector, {
      props: {
        local: sampleLocal,
        buildings: [],
        canEdit: true,
      },
    });

    expect(wrapper.text()).toContain('Este local aún no tiene pabellones registrados');
    const createBtn = wrapper.findAll('button').find((b) => b.text().includes('Registrar primer pabellón'));
    expect(createBtn).toBeDefined();

    await createBtn.trigger('click');
    expect(wrapper.emitted('create-building')).toBeTruthy();
  });

  it('deshabilita los botones cuando disabled es true', () => {
    const wrapper = mount(PabellonSelector, {
      props: {
        local: sampleLocal,
        buildings: sampleBuildings,
        disabled: true,
      },
    });

    const buttons = wrapper.findAll('button');
    const disabledButtons = buttons.filter((b) => b.attributes('disabled') !== undefined);
    expect(disabledButtons.length).toBeGreaterThan(0);
  });
});
