export const isValidIpv4 = (value) => {
  const parts = String(value).trim().split('.');
  return parts.length === 4 && parts.every((part) => {
    if (!/^\d{1,3}$/.test(part)) return false;
    const number = Number(part);
    return number >= 0 && number <= 255;
  });
};

export const isValidIpv6 = (value) => {
  const normalized = String(value).trim();
  if (!normalized || normalized.includes(':::')) return false;
  const doubleCompressionCount = (normalized.match(/::/g) || []).length;
  if (doubleCompressionCount > 1) return false;

  const [head, tail] = normalized.split('::');
  const headParts = head ? head.split(':') : [];
  const tailParts = tail ? tail.split(':') : [];
  const parts = [...headParts, ...tailParts];
  if (!parts.length || parts.some((part) => !/^[0-9a-f]{1,4}$/i.test(part))) return false;
  return doubleCompressionCount === 1 ? parts.length < 8 : parts.length === 8;
};
