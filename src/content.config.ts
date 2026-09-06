import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

const articles = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/articles' }),
  schema: z.object({
    title: z.string().min(1),
    description: z.string().min(1),
    date: z.coerce.date(),
    category: z.string().min(1),
    tags: z.array(z.string()).default([]),
    slug: z.string().regex(/^[a-z0-9]+(?:-[a-z0-9]+)*$/),
    draft: z.boolean().default(false),
    featured: z.boolean().default(false),
    readTime: z.string().optional(),
  }),
});

export const collections = { articles };
