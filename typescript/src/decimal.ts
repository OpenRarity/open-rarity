/** Preserve JSON decimal spelling before binary64 conversion. */
export class ExactDecimal {
  constructor(readonly source: string) {
    if (decimal(source) === null)
      throw new TypeError("Invalid or oversized decimal");
  }
}
export interface DecimalParts {
  sign: number;
  digits: string;
  exponent: number;
}
export function decimal(value: string): DecimalParts | null {
  if (value.length > 1024) return null;
  const m =
    /^([+-]?)([0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE]([+-]?[0-9]+))?$/.exec(value);
  if (!m) return null;
  let exponent = Number(m[3] ?? 0) - (m[2].split(".")[1]?.length ?? 0);
  if (!Number.isSafeInteger(exponent) || Math.abs(exponent) > 10000)
    return null;
  let digits = m[2].replace(".", "").replace(/^0+/, "");
  if (!digits) return { sign: 0, digits: "0", exponent: 0 };
  while (digits.endsWith("0")) {
    digits = digits.slice(0, -1);
    exponent++;
  }
  return { sign: m[1] === "-" ? -1 : 1, digits, exponent };
}
export function compareDecimals(a: DecimalParts, b: DecimalParts): number {
  if (a.sign !== b.sign) return a.sign - b.sign;
  if (!a.sign) return 0;
  const magnitude = a.digits.length + a.exponent - b.digits.length - b.exponent;
  if (magnitude) return Math.sign(magnitude) * a.sign;
  const length = Math.max(a.digits.length, b.digits.length);
  const left = a.digits.padEnd(length, "0"),
    right = b.digits.padEnd(length, "0");
  return (left < right ? -1 : left > right ? 1 : 0) * a.sign;
}
export function decimalText(value: string): string {
  const d = decimal(value);
  if (!d) throw new TypeError("Invalid or oversized decimal");
  if (!d.sign) return "0";
  const point = d.digits.length + d.exponent;
  const text =
    point <= 0
      ? "0." + "0".repeat(-point) + d.digits
      : point >= d.digits.length
        ? d.digits + "0".repeat(point - d.digits.length)
        : d.digits.slice(0, point) + "." + d.digits.slice(point);
  return (d.sign < 0 ? "-" : "") + text;
}
