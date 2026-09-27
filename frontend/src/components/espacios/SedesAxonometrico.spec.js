import { mount } from '@vue/test-utils';
import { describe, expect, it } from 'vitest';
import SedesAxonometrico from '@/components/espacios/SedesAxonometrico.vue';

const localCards = [
  { id: 1, codigo: 'HCO-CENTRAL', nombre: 'Campus Central', buildingCount: 2 },
  { id: 2, codigo: 'HCO-ESPERANZA', nombre: 'Sede La Esperanza', buildingCount: 1 },
];

describe('SedesAxonometrico', () => {
  it('presenta la ciudad como origen y las sedes como nodos accionables', () => {
    const wrapper = mount(SedesAxonometrico, {
      props: {
        city: 'Huánuco',
        localCards,
        totalLocalCount: 2,
        totalBuildingCount: 3,
      },
    });

    expect(wrapper.text()).toContain('Huánuco');
    expect(wrapper.text()).toContain('2 sedes · 3 pabellones');
    expect(wrapper.text()).toContain('no representa distancias');
    expect(wrapper.findAll('[aria-label="Locales disponibles"] button')).toHaveLength(2);
    expect(wrapper.find('svg[role="img"]').exists()).toBe(false);
  });

  it('abre el croquis de la sede elegida', async () => {
    const wrapper = mount(SedesAxonometrico, {
      props: { city: 'Huánuco', localCards, totalLocalCount: 2, totalBuildingCount: 3 },
    });

    await wrapper.get('[aria-label="Abrir croquis de Campus Central. 2 pabellones"]').trigger('click');

    expect(wrapper.emitted('select-local')?.[0]).toEqual([1]);
  });

  it('bloquea nodos y paginación mientras el croquis está en edición', async () => {
    const wrapper = mount(SedesAxonometrico, {
      props: {
        city: 'Huánuco',
        localCards: [...localCards, { id: 3, codigo: 'HCO-ANEXO', nombre: 'Anexo', buildingCount: 1 }, { id: 4, codigo: 'HCO-OTRO', nombre: 'Otra sede', buildingCount: 1 }],
        totalLocalCount: 4,
        totalBuildingCount: 5,
        disabled: true,
      },
    });

    expect(wrapper.get('[aria-label="Abrir croquis de Campus Central. 2 pabellones"]').attributes('disabled')).toBeDefined();
    expect(wrapper.get('[aria-label="Página siguiente"]').attributes('disabled')).toBeDefined();
    await wrapper.get('[aria-label="Abrir croquis de Campus Central. 2 pabellones"]').trigger('click');
    expect(wrapper.emitted('select-local')).toBeUndefined();
  });

  it('distingue entre búsqueda vacía y ciudad sin sedes registradas', () => {
    const noMatches = mount(SedesAxonometrico, {
      props: {
        city: 'Huánuco',
        localCards: [],
        totalLocalCount: 2,
        totalBuildingCount: 3,
        search: 'Sin coincidencias',
      },
    });
    expect(noMatches.text()).toContain('No hay sedes que coincidan con la búsqueda.');

    const noLocations = mount(SedesAxonometrico, { props: { city: 'Ambo' } });
    expect(noLocations.text()).toContain('Esta ciudad todavía no tiene sedes registradas.');
  });
});
