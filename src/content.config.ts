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
    // The field of study this note sits in. Required, so a new note has to say
    // what it is about. Add to the list when a note opens a new field.
    field: z.enum([
      'Energy',
      'Materials science',
      'Mathematics',
      'Metrology',
      'Spaceflight',
    ]),
    draft: z.boolean().default(false),
  }),
});

export const collections = { writing };
