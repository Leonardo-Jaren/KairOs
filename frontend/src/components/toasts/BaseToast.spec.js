import { mount } from '@vue/test-utils';
import { afterEach, describe, expect, it, vi } from 'vitest';

import BaseToast from '@/components/toasts/BaseToast.vue';

describe('BaseToast', () => {
  afterEach(() => {
    vi.useRealTimers();
  });

  it('se cierra automaticamente al cumplir la duracion', async () => {
    vi.useFakeTimers();
    const wrapper = mount(BaseToast, {
      props: { show: true, message: 'Cambios guardados' },
      global: { stubs: { Teleport: true } },
    });

    await vi.advanceTimersByTimeAsync(5000);

    expect(wrapper.emitted('close')).toHaveLength(1);
  });

  it('reinicia el tiempo cuando cambia la notificacion', async () => {
    vi.useFakeTimers();
    const wrapper = mount(BaseToast, {
      props: { show: true, message: 'Primera notificacion', duration: 3000 },
      global: { stubs: { Teleport: true } },
    });

    await vi.advanceTimersByTimeAsync(2000);
    await wrapper.setProps({ message: 'Segunda notificacion' });
    await vi.advanceTimersByTimeAsync(2000);

    expect(wrapper.emitted('close')).toBeUndefined();

    await vi.advanceTimersByTimeAsync(1000);

    expect(wrapper.emitted('close')).toHaveLength(1);
  });

  it('permite desactivar el cierre automatico', async () => {
    vi.useFakeTimers();
    const wrapper = mount(BaseToast, {
      props: { show: true, message: 'Notificacion persistente', duration: 0 },
      global: { stubs: { Teleport: true } },
    });

    await vi.runAllTimersAsync();

    expect(wrapper.emitted('close')).toBeUndefined();
  });
});
