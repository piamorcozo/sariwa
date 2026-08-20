export function peso(value: number | string | null | undefined): string {
  const amount = Number(value || 0);
  return '₱' + amount.toLocaleString('en-PH');
}

export function num(value: number | string | null | undefined): number {
  return Number(value || 0);
}

export function sessionId(): string {
  const key = 'sariwa_session';
  let value = localStorage.getItem(key);
  if (!value) {
    value = crypto.randomUUID();
    localStorage.setItem(key, value);
  }
  return value;
}

export function manilaTodayIso(): string {
  return new Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Manila' }).format(new Date());
}

export function addIsoDays(iso: string, days: number): string {
  const [year, month, day] = iso.split('-').map(Number);
  return new Date(Date.UTC(year, month - 1, day + days)).toISOString().slice(0, 10);
}

export function isoWeekday(iso: string): string {
  const [year, month, day] = iso.split('-').map(Number);
  return new Date(Date.UTC(year, month - 1, day)).toLocaleDateString('en-US', {
    weekday: 'long',
    timeZone: 'UTC',
  });
}

export function isoMonth(iso: string): string {
  const [year, month, day] = iso.split('-').map(Number);
  return new Date(Date.UTC(year, month - 1, day))
    .toLocaleDateString('en-US', { month: 'long', timeZone: 'UTC' })
    .toUpperCase();
}

export function isoDayNum(iso: string): number {
  return Number(iso.slice(8, 10));
}

const DELIVERY_PREF = 'sariwa_delivery';

export function saveDeliveryPref(date: string, slotId: number) {
  localStorage.setItem(DELIVERY_PREF, JSON.stringify({ date, slotId }));
}

export function loadDeliveryPref(): { date: string; slotId: number } | null {
  try {
    const raw = localStorage.getItem(DELIVERY_PREF);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}
