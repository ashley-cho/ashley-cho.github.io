import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const writing = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/writing' }),
  schema: z.object({
    title: z.string(),
    subtitle: z.string().optional(),
    description: z.string().optional(),
    date: z.coerce.date(),
    series: z.string().optional(),
    seriesPart: z.number().optional(),
    // Set when the piece lives at its own path instead of /writing/<id>/
    url: z.string().optional(),
    // Defaults to essay, or reference when the piece has its own path
    kind: z.enum(['essay', 'reference']).optional(),
    draft: z.boolean().default(false),
  }),
});

export const collections = { writing };
