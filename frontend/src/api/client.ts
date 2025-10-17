import { z } from 'zod';

import { holidaySchema, planResponseSchema, type PlanBlock, type PlanResponse, type Holiday } from './types';

const baseUrl = '/api/max-days-off';

const errorSchema = z.object({
  error: z.object({
    code: z.string(),
    message: z.string(),
    hint: z.string().optional(),
  }),
});

async function handleResponse<T>(response: Response, schema: z.ZodSchema<T>): Promise<T> {
  const text = await response.text();
  const json = text ? JSON.parse(text) : {};
  if (!response.ok) {
    const parsedError = errorSchema.safeParse(json);
    if (parsedError.success) {
      throw new Error(parsedError.data.error.message);
    }
    throw new Error('Request failed');
  }
  const parseResult = schema.safeParse(json);
  if (!parseResult.success) {
    throw new Error('Unexpected response format');
  }
  return parseResult.data;
}

export interface PlanRequestPayload {
  year: number;
  country: string;
  region?: string;
  timezone: string;
  pto_total: number;
  blocks_max: number;
  weekend: string[];
  goal: 'max_total' | 'max_longest';
  prefs: Record<string, unknown>;
  constraints: Record<string, unknown>;
}

export async function fetchHolidays(params: {
  year: number;
  country: string;
  region?: string;
  timezone?: string;
}): Promise<Holiday[]> {
  const query = new URLSearchParams({
    year: params.year.toString(),
    country: params.country,
  });
  if (params.region) query.set('region', params.region);
  if (params.timezone) query.set('timezone', params.timezone);
  const response = await fetch(`${baseUrl}/holidays?${query.toString()}`);
  const data = await handleResponse(
    response,
    z.object({
      holidays: z.array(holidaySchema),
      year: z.number(),
      country: z.string(),
      region: z.string().nullable().optional(),
      timezone: z.string().nullable().optional(),
    }),
  );
  return data.holidays;
}

export async function computePlans(payload: PlanRequestPayload): Promise<PlanResponse> {
  const response = await fetch(`${baseUrl}/plan`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  return handleResponse(response, planResponseSchema);
}

export async function exportPlanToICS(payload: {
  title: string;
  timezone: string;
  blocks: PlanBlock[];
}): Promise<Blob> {
  const response = await fetch(`${baseUrl}/export/ics`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error('Failed to export calendar');
  }
  return response.blob();
}
