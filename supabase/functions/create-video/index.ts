import { createClient } from "npm:@supabase/supabase-js@2";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, apikey, content-type, x-client-info",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};

const json = (data: unknown, status = 200) =>
  new Response(JSON.stringify(data), {
    status,
    headers: { ...corsHeaders, "Content-Type": "application/json" },
  });

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }

  try {
    const authHeader = req.headers.get("Authorization");
    if (!authHeader) return json({ error: "Sign in first." }, 401);

    const supabase = createClient(
      Deno.env.get("SUPABASE_URL")!,
      Deno.env.get("SUPABASE_ANON_KEY")!,
      { global: { headers: { Authorization: authHeader } } }
    );

    const {
      data: { user },
      error: authError,
    } = await supabase.auth.getUser();

    if (authError || !user) {
      return json({ error: "Invalid session." }, 401);
    }

    const { prompt, mode, image_url, duration = 5 } = await req.json();

    if (typeof prompt !== "string" || !prompt.trim() || prompt.length > 5000) {
      return json({ error: "Enter a prompt under 5000 characters." }, 400);
    }

    if (mode !== "text" && mode !== "image") {
      return json({ error: "Invalid generation mode." }, 400);
    }

    if (![5, 10].includes(Number(duration))) {
      return json({ error: "Choose 5 or 10 seconds." }, 400);
    }

    if (mode === "image" && (typeof image_url !== "string" || !image_url.startsWith("https://"))) {
      return json({ error: "A valid uploaded image URL is required." }, 400);
    }

    const model =
      mode === "image"
        ? "fal-ai/wan/v2.7/image-to-video"
        : "fal-ai/wan/v2.7/text-to-video";

    const input: Record<string, unknown> = {
      prompt: prompt.trim(),
      duration: Number(duration),
      resolution: "720p",
      enable_safety_checker: true,
    };

    if (mode === "image") input.image_url = image_url;

    const apiKey = Deno.env.get("FAL_KEY");
    if (!apiKey) {
      throw new Error(
        "Video provider is not configured. Please set FAL_KEY in Supabase Edge Function secrets."
      );
    }

    const response = await fetch(`https://queue.fal.run/${model}`, {
      method: "POST",
      headers: {
        Authorization: `Key ${apiKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(input),
    });

    const result = await response.json();

    if (!response.ok) {
      console.error("Provider submission failed:", response.status, result);
      return json(
        { error: result?.detail || "Video provider rejected the request." },
        502
      );
    }

    const requestId = result.request_id;
    if (!requestId) {
      return json({ error: "No generation job was returned." }, 502);
    }

    const { error: dbError } = await supabase.from("video_jobs").insert({
      user_id: user.id,
      request_id: requestId,
      model,
      mode,
      status: "queued",
    });

    if (dbError) {
      console.error("Could not save job:", dbError.message);
      return json({ error: "Could not save generation job." }, 500);
    }

    return json({ request_id: requestId, status: "queued" });
  } catch (error: any) {
    console.error("Create video error:", error);
    return json(
      { error: error?.message || "Unable to start video generation." },
      500
    );
  }
});
