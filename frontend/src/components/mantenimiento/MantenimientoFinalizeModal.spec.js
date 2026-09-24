import { mount } from '@vue/test-utils';
import { nextTick, reactive } from 'vue';
import { describe, expect, it } from 'vitest';

import MantenimientoFinalizeModal from '@/components/mantenimiento/MantenimientoFinalizeModal.vue';

describe('MantenimientoFinalizeModal', () => {
  const ticket = {
    id: 12,
    incidencia_origen_id: 7,
    tipo_mantenimiento: 'correctivo',
    tipo_mantenimiento_display: 'Correctivo',
    tecnico_responsable: 'Ada Lovelace',
    equipo: {
      codigo: 'LAB-01-PC-01',
      marca: 'Dell',
      modelo: 'OptiPlex',
      espacio_nombre: 'LAB-01 - Pabellón A',
    },
  };

  const resultadoOptions = [
    { value: 'en_uso', label: 'Funcional / en uso' },
    { value: 'dañado', label: 'Dañado' },
    { value: 'de_baja', label: 'De baja' },
  ];

  it('muestra el contexto de la orden y comunica el cierre de la incidencia', () => {
    const form = reactive({
      diagnostico: '',
      trabajo_realizado: '',
      prueba_realizada: false,
      observacion_prueba: '',
      resultado_equipo: 'en_uso',
    });

    const wrapper = mount(MantenimientoFinalizeModal, {
      attachTo: document.body,
      props: {
        open: true,
        ticket,
        form,
        errors: {},
        resultadoOptions,
      },
    });

    expect(document.body.textContent).toContain('Finalizar mantenimiento #12');
    expect(document.body.textContent).toContain('LAB-01-PC-01');
    expect(document.body.textContent).toContain('INC-7');
    expect(document.body.textContent).toContain('Finalizar y cerrar incidencia');
    expect(document.body.textContent).toContain('El equipo quedará funcional');

    wrapper.unmount();
  });

  it('advierte que la incidencia seguirá abierta si el resultado es dañado', async () => {
    const form = reactive({
      diagnostico: '',
      trabajo_realizado: '',
      prueba_realizada: true,
      observacion_prueba: '',
      resultado_equipo: 'dañado',
    });

    const wrapper = mount(MantenimientoFinalizeModal, {
      attachTo: document.body,
      props: {
        open: true,
        ticket,
        form,
        errors: {},
        resultadoOptions,
      },
    });

    await nextTick();
    expect(document.body.textContent).toContain('La orden terminará, pero la incidencia permanecerá abierta');
    expect(document.body.textContent).toContain('Finalizar como equipo dañado');

    wrapper.unmount();
  });
});
