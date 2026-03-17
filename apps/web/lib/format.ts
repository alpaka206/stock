const numberFormatters = {
  integer: new Intl.NumberFormat("ko-KR"),
  compact: new Intl.NumberFormat("ko-KR", {
    notation: "compact",
    maximumFractionDigits: 1,
  }),
};

export function formatPrice(value: number, digits = 2) {
  return new Intl.NumberFormat("ko-KR", {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  }).format(value);
}

export function formatPercent(value: number, digits = 2) {
  return `${formatPrice(value, digits)}%`;
}

export function formatSignedPercent(value: number, digits = 2) {
  const sign = value > 0 ? "+" : "";
  return `${sign}${formatPercent(value, digits)}`;
}

export function formatSignedNumber(value: number, digits = 2) {
  const sign = value > 0 ? "+" : "";
  return `${sign}${formatPrice(value, digits)}`;
}

export function formatInteger(value: number) {
  return numberFormatters.integer.format(value);
}

export function formatCompactNumber(value: number) {
  return numberFormatters.compact.format(value);
}

export function formatDateLabel(value: string) {
  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat("ko-KR", {
    month: "short",
    day: "numeric",
  }).format(date);
}
