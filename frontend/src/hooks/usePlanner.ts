import { useMutation, useQuery } from '@tanstack/react-query';
import { useCallback, useEffect, useRef, useState } from 'react';

import { computePlans, exportPlanToICS, fetchHolidays, type PlanRequestPayload } from '../api/client';
import type { Plan, PlanBlock } from '../api/types';

const DEFAULT_PARAMS: PlanRequestPayload = {
  year: new Date().getFullYear(),
  country: 'CA',
  region: 'ON',
  timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
  pto_total: 15,
  blocks_max: 3,
  weekend: ['SAT', 'SUN'],
  goal: 'max_total',
  prefs: {
    reserve_pto: 3,
    season_spread: true,
    prefer_months: [],
    avoid_months: [],
  },
  constraints: {
    blackouts: [],
    min_block_len: 3,
    max_block_len: 18,
  },
};

function parseParams(): PlanRequestPayload {
  const search = new URLSearchParams(window.location.search);
  const parsed: PlanRequestPayload = { ...DEFAULT_PARAMS };
  const num = (key: string) => {
    const value = search.get(key);
    return value ? Number.parseInt(value, 10) : undefined;
  };
  parsed.year = num('year') ?? parsed.year;
  parsed.country = search.get('country') ?? parsed.country;
  parsed.region = search.get('region') ?? parsed.region;
  parsed.timezone = search.get('timezone') ?? parsed.timezone;
  parsed.pto_total = num('pto') ?? parsed.pto_total;
  parsed.blocks_max = num('blocks') ?? parsed.blocks_max;
  parsed.goal = (search.get('goal') as 'max_total' | 'max_longest') ?? parsed.goal;
  return parsed;
}

function persistParams(params: PlanRequestPayload) {
  const search = new URLSearchParams();
  search.set('year', String(params.year));
  search.set('country', params.country);
  if (params.region) search.set('region', params.region);
  search.set('timezone', params.timezone);
  search.set('pto', String(params.pto_total));
  search.set('blocks', String(params.blocks_max));
  search.set('goal', params.goal);
  const url = `${window.location.pathname}?${search.toString()}`;
  window.history.replaceState({}, '', url);
}

export interface PlannerState {
  params: PlanRequestPayload;
  plans: Plan[];
  alternates: Plan[];
  isLoading: boolean;
  error?: string;
  holidays: string[];
  submit: (params: PlanRequestPayload) => void;
  downloadPlan: (plan: Plan, title: string) => Promise<void>;
  setParams: (params: PlanRequestPayload) => void;
}

export function usePlanner(): PlannerState {
  const [params, setParams] = useState<PlanRequestPayload>(() => parseParams());
  const initialized = useRef(false);

  useEffect(() => {
    persistParams(params);
  }, [params]);

  const holidayQuery = useQuery({
    queryKey: ['holidays', params.year, params.country, params.region],
    queryFn: async () => {
      const results = await fetchHolidays({
        year: params.year,
        country: params.country,
        region: params.region,
        timezone: params.timezone,
      });
      return results.map((holiday) => holiday.date);
    },
  });

  const planMutation = useMutation({
    mutationKey: ['plan', params],
    mutationFn: async (body: PlanRequestPayload) => computePlans(body),
  });

  useEffect(() => {
    if (!initialized.current) {
      initialized.current = true;
      planMutation.mutate(params);
    }
  }, [planMutation, params]);

  const submit = useCallback(
    (nextParams: PlanRequestPayload) => {
      setParams(nextParams);
      planMutation.mutate(nextParams);
    },
    [planMutation],
  );

  const downloadPlan = useCallback(async (plan: Plan, title: string) => {
    const blob = await exportPlanToICS({
      title,
      timezone: params.timezone,
      blocks: plan.blocks as PlanBlock[],
    });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = `${title.replace(/\s+/g, '-')}.ics`;
    anchor.click();
    URL.revokeObjectURL(url);
  }, [params.timezone]);

  const plans = planMutation.data?.plans ?? [];
  const alternates = planMutation.data?.alternates ?? [];

  return {
    params,
    plans,
    alternates,
    isLoading: planMutation.isPending,
    error: planMutation.error ? (planMutation.error as Error).message : undefined,
    holidays: holidayQuery.data ?? [],
    submit,
    downloadPlan,
    setParams,
  };
}
