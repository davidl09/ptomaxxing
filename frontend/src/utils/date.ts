import { addDays, eachDayOfInterval, format, isWithinInterval, parseISO } from 'date-fns';

export function formatDateRange(start: string, end: string, locale: string): string {
  const startDate = parseISO(start);
  const endDate = parseISO(end);
  const formatter = new Intl.DateTimeFormat(locale, {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
  });
  return `${formatter.format(startDate)} – ${formatter.format(endDate)}`;
}

export function dateRangeDays(start: string, end: string): string[] {
  return eachDayOfInterval({ start: parseISO(start), end: parseISO(end) }).map((day) =>
    format(day, 'yyyy-MM-dd'),
  );
}

export function isInRange(day: string, start: string, end: string): boolean {
  return isWithinInterval(parseISO(day), { start: parseISO(start), end: parseISO(end) });
}

export function nextDay(day: string): string {
  return format(addDays(parseISO(day), 1), 'yyyy-MM-dd');
}
