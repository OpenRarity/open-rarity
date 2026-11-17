/** Identical binary64 operations in both runtimes, avoiding platform libm drift. */
export function log2(value: number): number {
  let exponent = 0;
  while (value < 1) {
    value *= 2;
    exponent--;
  }
  while (value >= 2) {
    value /= 2;
    exponent++;
  }
  const z = (value - 1) / (value + 1),
    square = z * z;
  let term = z,
    sum = z;
  for (let denominator = 3; denominator < 61; denominator += 2) {
    term *= square;
    sum += term / denominator;
  }
  return exponent + (2 * sum) / 0.6931471805599453;
}
