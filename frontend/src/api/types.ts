import { z } from 'zod';

export const holidaySchema = z.object({
  date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/),
  name: z.string(),
  observed: z.boolean(),
});

export const planBlockSchema = z.object({
  start: z.string(),
  end: z.string(),
  days_off: z.number(),
  pto: z.array(z.string()),
  holidays: z.array(z.string()),
  weekends: z.array(z.string()),
  explain: z.string(),
});

export const planSchema = z.object({
  score: z.number(),
  pto_used: z.number(),
  blocks: z.array(planBlockSchema),
});

export const planResponseSchema = z.object({
  params: z.record(z.any()),
  plans: z.array(planSchema),
  alternates: z.array(planSchema),
});

export type Holiday = z.infer<typeof holidaySchema>;
export type PlanBlock = z.infer<typeof planBlockSchema>;
export type Plan = z.infer<typeof planSchema>;
export type PlanResponse = z.infer<typeof planResponseSchema>;
