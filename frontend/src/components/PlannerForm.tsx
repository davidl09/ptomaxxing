import { FormEvent, useCallback, useEffect, useState } from 'react';

import type { PlanRequestPayload } from '../api/client';

interface PlannerFormProps {
  params: PlanRequestPayload;
  onSubmit: (params: PlanRequestPayload) => void;
}

const WEEKDAYS: { label: string; value: string }[] = [
  { label: 'Mon', value: 'MON' },
  { label: 'Tue', value: 'TUE' },
  { label: 'Wed', value: 'WED' },
  { label: 'Thu', value: 'THU' },
  { label: 'Fri', value: 'FRI' },
  { label: 'Sat', value: 'SAT' },
  { label: 'Sun', value: 'SUN' },
];

function toggleValue(values: string[], value: string): string[] {
  return values.includes(value) ? values.filter((item) => item !== value) : [...values, value];
}

export default function PlannerForm({ params, onSubmit }: PlannerFormProps) {
  const [draft, setDraft] = useState<PlanRequestPayload>(params);

  useEffect(() => {
    setDraft(params);
  }, [params]);

  const handleSubmit = useCallback(
    (event: FormEvent<HTMLFormElement>) => {
      event.preventDefault();
      onSubmit(draft);
    },
    [draft, onSubmit],
  );

  const handleChange = useCallback(<K extends keyof PlanRequestPayload>(key: K, value: PlanRequestPayload[K]) => {
    setDraft((current) => ({ ...current, [key]: value }));
  }, []);

  const handleWeekendToggle = useCallback(
    (value: string) => {
      setDraft((current) => ({
        ...current,
        weekend: toggleValue(current.weekend, value).sort(),
      }));
    },
    [],
  );

  return (
    <form className="planner-form" onSubmit={handleSubmit} aria-label="Planner form">
      <div className="form-grid">
        <label>
          Year
          <input
            type="number"
            value={draft.year}
            min={1900}
            max={2100}
            onChange={(event) => handleChange('year', Number.parseInt(event.target.value, 10))}
          />
        </label>
        <label>
          Country
          <input value={draft.country} onChange={(event) => handleChange('country', event.target.value)} />
        </label>
        <label>
          Region
          <input value={draft.region ?? ''} onChange={(event) => handleChange('region', event.target.value)} />
        </label>
        <label>
          Timezone
          <input value={draft.timezone} onChange={(event) => handleChange('timezone', event.target.value)} />
        </label>
        <label>
          PTO Days
          <input
            type="number"
            min={0}
            value={draft.pto_total}
            onChange={(event) => handleChange('pto_total', Number.parseInt(event.target.value, 10))}
          />
        </label>
        <label>
          Reserve PTO
          <input
            type="number"
            min={0}
            value={(draft.prefs.reserve_pto as number) ?? 0}
            onChange={(event) =>
              handleChange('prefs', { ...draft.prefs, reserve_pto: Number.parseInt(event.target.value, 10) })
            }
          />
        </label>
        <label>
          Max Blocks
          <input
            type="number"
            min={1}
            max={5}
            value={draft.blocks_max}
            onChange={(event) => handleChange('blocks_max', Number.parseInt(event.target.value, 10))}
          />
        </label>
        <label>
          Goal
          <select value={draft.goal} onChange={(event) => handleChange('goal', event.target.value as typeof draft.goal)}>
            <option value="max_total">Maximize total days</option>
            <option value="max_longest">Maximize longest break</option>
          </select>
        </label>
      </div>

      <fieldset className="weekend-toggle">
        <legend>Weekend days</legend>
        <div className="weekdays">
          {WEEKDAYS.map((weekday) => (
            <label key={weekday.value}>
              <input
                type="checkbox"
                checked={draft.weekend.includes(weekday.value)}
                onChange={() => handleWeekendToggle(weekday.value)}
              />
              <span>{weekday.label}</span>
            </label>
          ))}
        </div>
      </fieldset>

      <button type="submit">Compute plans</button>
    </form>
  );
}
