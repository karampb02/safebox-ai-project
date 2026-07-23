import { z } from "zod";
import { publicProcedure, router } from "./_core/trpc";
import { GoogleGenAI, Type, Schema } from "@google/genai";

// Initialize Gemini client using the API key from environment variables
// It will automatically pick up process.env.GEMINI_API_KEY
const ai = new GoogleGenAI({});

export const aiRouter = router({
  checkUrl: publicProcedure
    .input(
      z.object({
        url: z.string().url("Please enter a valid URL"),
      })
    )
    .mutation(async ({ input }) => {
      const { url } = input;
      
      const prompt = `Analyze the following URL and determine if it is a spam/phishing website or a legitimate, safe website. 
Take into account common phishing patterns, typical scam keywords in the domain, and brand impersonation.
URL to check: ${url}`;

      const responseSchema: Schema = {
        type: Type.OBJECT,
        properties: {
          isSpam: {
            type: Type.BOOLEAN,
            description: "true if the URL is likely spam or phishing, false if legitimate",
          },
          reason: {
            type: Type.STRING,
            description: "A short, 1-2 sentence explanation of why the URL was classified this way",
          },
        },
        required: ["isSpam", "reason"],
      };

      try {
        const response = await ai.models.generateContent({
          model: "gemini-2.5-flash",
          contents: prompt,
          config: {
            responseMimeType: "application/json",
            responseSchema: responseSchema,
          },
        });

        const text = response.text;
        if (!text) {
          throw new Error("Empty response from AI");
        }

        const result = JSON.parse(text);
        return {
          isSpam: result.isSpam,
          reason: result.reason,
        };
      } catch (error: any) {
        console.error("AI URL Check Error:", error);
        throw new Error("Failed to check URL using AI. Please check your API key or try again.");
      }
    }),
});
