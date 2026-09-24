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

  it('mantiene tarjetas uniformes y pagina las sedes sin agrandar indefinidamente el panel', async () => {
    const cards = [
      ...cityCards,
      { value: 'Ambo', label: 'Ambo', localCount: 1, buildingCount: 1 },
      { value: 'Aucayacu', label: 'Aucayacu', localCount: 1, buildingCount: 0 },
      { value: 'Panao', label: 'Panao', localCount: 1, buildingCount: 0 },
    ];
    const wrapper = mount(TerritorioSelector, { props: { cityCards: cards } });
    expect(wrapper.findAll('[aria-label="Ciudades disponibles"] button')).toHaveLength(4);
    expect(wrapper.text()).not.toContain('Pasa el cursor sobre el mapa');
    expect(wrapper.text()).not.toContain('Exploración geográfica');
    expect(wrapper.text()).not.toContain('Núcleo');
    const buttons = wrapper.findAll('[aria-label="Ciudades disponibles"] button');
    expect(buttons[0].classes()).toContain('border-slate-200');
    expect(buttons[2].classes()).toContain('border-slate-200');

    await wrapper.get('[aria-label="Páginas de ciudades"] button:last-child').trigger('click');
    expect(wrapper.get('[aria-label="Ciudades disponibles"]').text()).toContain('Panao');
    expect(wrapper.findAll('[aria-label="Ciudades disponibles"] button')).toHaveLength(1);
    await wrapper.get('[aria-label="Ciudades disponibles"] button').trigger('click');
    expect(wrapper.emitted('select-city')?.[0]).toEqual(['Panao']);
  });

  it('busca ciudades y locales con el mismo control reutilizable', async () => {
    const wrapper = mount(TerritorioSelector, { props: { cityCards, search: 'Tingo' } });
    expect(wrapper.findAll('[aria-label="Ciudades disponibles"] button')).toHaveLength(1);
    await wrapper.get('#map-city-search').setValue('Huánuco');
    expect(wrapper.emitted('update:search')?.at(-1)).toEqual(['Huánuco']);

    await wrapper.setProps({ city: 'Huánuco', localCards, search: 'Esperanza' });
    expect(wrapper.get('[aria-label="Locales disponibles"]').text()).toContain('Sede La Esperanza');
    expect(wrapper.get('[aria-label="Locales disponibles"]').text()).not.toContain('Campus Central');
  });

  it('sustituye el mapa de ciudades por los locales de la ciudad con tarjetas unificadas', async () => {
    const wrapper = mount(TerritorioSelector, {
      props: {
        city: 'Huánuco',
        cityCards,
        localCards: [
          { id: 1, codigo: 'HCO-CENTRAL', nombre: 'Campus Central', tipoLabel: 'Campus', descripcion: 'Campus principal.', buildingCount: 2 },
          { id: 2, codigo: 'LOC-HUANUCO', nombre: 'Campus Central Huánuco', tipoLabel: 'Campus', descripcion: '', buildingCount: 2 },
        ],
      },
    });

    expect(wrapper.find('[aria-label="Ciudades disponibles"]').exists()).toBe(false);
    const buttons = wrapper.findAll('[aria-label="Locales disponibles"] button');
    expect(buttons).toHaveLength(2);
    expect(buttons[0].classes()).toContain('h-full');
    expect(buttons[0].classes()).toContain('flex-1');
    expect(buttons[1].classes()).toContain('h-full');
    expect(buttons[1].classes()).toContain('flex-1');

    expect(buttons[0].text()).toContain('Campus principal.');
    expect(buttons[1].text()).toContain('Campus con infraestructura tecnológica distribuida en pabellones y pisos.');
    expect(wrapper.text()).not.toContain('Tipo de ubicación');

    await buttons[0].trigger('click');
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

  it('permite seleccionar Ambo desde el mapa cuando está disponible en las sedes', async () => {
    const cityCardsWithAmbo = [
      ...cityCards,
      { value: 'Ambo', label: 'Ambo', localCount: 1, buildingCount: 1 },
    ];
    const wrapper = mount(TerritorioSelector, { props: { cityCards: cityCardsWithAmbo } });
    const mapPaths = wrapper.findAll('svg[role="img"] path');

    // Clic en la provincia interactiva de Ambo (índice 2)
    await mapPaths[2].trigger('click');
    expect(wrapper.emitted('select-city')?.[0]).toEqual(['Ambo']);
  });

  it('no activa ni emite Huánuco si cityCards no contiene la sede de Huánuco', async () => {
    const onlyAmbo = [
      { value: 'Ambo', label: 'Ambo', localCount: 1, buildingCount: 1 },
    ];
    const wrapper = mount(TerritorioSelector, { props: { cityCards: onlyAmbo } });
    const mapPaths = wrapper.findAll('svg[role="img"] path');

    // Clic en Huánuco (índice 0): no debe emitir select-city porque Huánuco no está en las sedes
    await mapPaths[0].trigger('click');
    expect(wrapper.emitted('select-city')).toBeUndefined();
  });

  it('resalta las provincias con su paleta corporativa correspondiente al hacer hover', async () => {
    const cityCardsAll = [
      ...cityCards,
      { value: 'Ambo', label: 'Ambo', localCount: 1, buildingCount: 1 },
    ];
    const wrapper = mount(TerritorioSelector, { props: { cityCards: cityCardsAll } });
    const buttons = wrapper.findAll('[aria-label="Ciudades disponibles"] button');

    // Hover en la tarjeta de Tingo María (índice 1)
    await buttons[1].trigger('mouseenter');
    const tingoPath = wrapper.findAll('svg[role="img"] path')[1];
    expect(tingoPath.classes()).toContain('fill-sky-500/35');

    // Hover en la tarjeta de Ambo (índice 2)
    await buttons[2].trigger('mouseenter');
    const amboPath = wrapper.findAll('svg[role="img"] path')[2];
    expect(amboPath.classes()).toContain('fill-indigo-500/35');
  });

  it('identifica sedes correctamente cuando el texto de la ciudad está en label o value', async () => {
    const cardsWithLabel = [
      { value: 'LP-01', label: 'Sede Tingo María', localCount: 1, buildingCount: 1 },
    ];
    const wrapper = mount(TerritorioSelector, { props: { cityCards: cardsWithLabel } });
    const mapPaths = wrapper.findAll('svg[role="img"] path');

    // Clic en Leoncio Prado (índice 1)
    await mapPaths[1].trigger('click');
    expect(wrapper.emitted('select-city')?.[0]).toEqual(['LP-01']);
  });
});
