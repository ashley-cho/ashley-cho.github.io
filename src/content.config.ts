import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const writing = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/writing' }),
  schema: z.object({
    title: z.string(),
    description: z.string().optional(),
    date: z.coerce.date(),
    series: z.string().optional(),
    seriesPart: z.number().optional(),
    draft: z.boolean().default(false),
  }),
});

export const collections = { writing };
