import { mount } from '@vue/test-utils';
import { describe, expect, it } from 'vitest';

import BaseExportExcelButton from './BaseExportExcelButton.vue';

describe('BaseExportExcelButton', () => {
  it('mantiene compatibilidad con los eventos click y export', async () => {
    const wrapper = mount(BaseExportExcelButton);

    await wrapper.get('button').trigger('click');

    expect(wrapper.emitted('click')).toHaveLength(1);
    expect(wrapper.emitted('export')).toHaveLength(1);
  });
});
