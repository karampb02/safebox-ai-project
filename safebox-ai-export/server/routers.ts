import { aiRouter } from "./aiRouter";
import { systemRouter } from "./_core/systemRouter";
import { router } from "./_core/trpc";

export const appRouter = router({
  system: systemRouter,
  ai: aiRouter,
});

export type AppRouter = typeof appRouter;
