import { mount } from '@vue/test-utils';
import { describe, expect, it } from 'vitest';
import TerritorioSelector from '@/components/espacios/TerritorioSelector.vue';

const cityCards = [
  { value: 'Huánuco', label: 'Huánuco', localCount: 2, buildingCount: 4 },
  { value: 'Tingo María', label: 'Tingo María', localCount: 1, buildingCount: 2 },
];
const localCards = [
  { id: 1, codigo: 'HCO-CENTRAL', nombre: 'Campus Central', tipoLabel: 'Campus', buildingCount: 2 },
  { id: 2, codigo: 'HCO-ESPERANZA', nombre: 'Sede La Esperanza', tipoLabel: 'Sede', buildingCount: 2 },
];

describe('TerritorioSelector', () => {
  it('muestra solamente ciudades en la raíz y emite la ciudad elegida', async () => {
    const wrapper = mount(TerritorioSelector, { props: { cityCards } });

    expect(wrapper.get('[aria-label="Ciudades disponibles"]')).toBeTruthy();
    expect(wrapper.find('[aria-label="Locales disponibles"]').exists()).toBe(false);
    expect(wrapper.text()).not.toContain('Paso 1');

    await wrapper.get('button').trigger('click');
    expect(wrapper.emitted('select-city')?.[0]).toEqual(['Huánuco']);
  });

  it('sustituye el mapa de ciudades por los locales de la ciudad', async () => {
    const wrapper = mount(TerritorioSelector, {
      props: { city: 'Huánuco', cityCards, localCards },
    });

    expect(wrapper.find('[aria-label="Ciudades disponibles"]').exists()).toBe(false);
    expect(wrapper.get('[aria-label="Locales disponibles"]').text()).toContain('Campus Central');
    expect(wrapper.text()).toContain('Sede La Esperanza');
    expect(wrapper.text()).not.toContain('Tipo de ubicación');

    await wrapper.get('[aria-label="Locales disponibles"] button').trigger('click');
    expect(wrapper.emitted('select-local')?.[0]).toEqual([1]);
  });

  it('bloquea las opciones cuando el croquis está en edición', () => {
    const wrapper = mount(TerritorioSelector, { props: { cityCards, disabled: true } });
    expect(wrapper.get('button').attributes('disabled')).toBeDefined();
    expect(wrapper.text()).toContain('Guarda o cancela');
  });

  it('permite seleccionar una sede al hacer clic en el mapa territorial', async () => {
    const wrapper = mount(TerritorioSelector, { props: { cityCards } });
    const mapPaths = wrapper.findAll('svg[role="img"] path');
    expect(mapPaths.length).toBe(11);

    // Clic en la provincia interactiva de Huánuco
    await mapPaths[0].trigger('click');
    expect(wrapper.emitted('select-city')?.[0]).toEqual(['Huánuco']);
  });
});
