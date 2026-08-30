import { describe, expect, it } from 'vitest';

import { isValidIpv4, isValidIpv6 } from '@/utils/ip-validation';

describe('validación de direcciones IP', () => {
  it('acepta IPv4 válidas y rechaza octetos fuera de rango', () => {
    expect(isValidIpv4('192.168.1.10')).toBe(true);
    expect(isValidIpv4('255.255.255.255')).toBe(true);
    expect(isValidIpv4('192.168.1.300')).toBe(false);
    expect(isValidIpv4('192.168.1')).toBe(false);
  });

  it('acepta IPv6 completa o comprimida', () => {
    expect(isValidIpv6('2001:0db8:0000:0000:0000:ff00:0042:8329')).toBe(true);
    expect(isValidIpv6('2001:db8::10')).toBe(true);
    expect(isValidIpv6('2001:db8:::10')).toBe(false);
    expect(isValidIpv6('2001:db8::zz')).toBe(false);
  });
});
