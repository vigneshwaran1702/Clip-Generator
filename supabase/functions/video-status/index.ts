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

    const { request_id } = await req.json();

    if (typeof request_id !== "string" || request_id.length > 200) {
      return json({ error: "Invalid request ID." }, 400);
    }

    // RLS ensures this job belongs to the signed-in user.
    const { data: job, error: dbError } = await supabase
      .from("video_jobs")
      .select("request_id, model, status, video_url")
      .eq("request_id", request_id)
      .maybeSingle();

    if (dbError) throw dbError;
    if (!job) return json({ error: "Job not found." }, 404);

    if (job.status === "completed" && job.video_url) {
      return json({ status: "completed", video_url: job.video_url });
    }

    const key = Deno.env.get("FAL_KEY");
    if (!key) {
      throw new Error(
        "Video provider is not configured. Please set FAL_KEY in Supabase Edge Function secrets."
      );
    }

    const base = `https://queue.fal.run/${job.model}/requests/${job.request_id}`;
    const headers = { Authorization: `Key ${key}` };

    const statusResponse = await fetch(`${base}/status`, { headers });

    if (!statusResponse.ok) {
      return json({ error: "Could not check generation status." }, 502);
    }

    const current = await statusResponse.json();

    if (current.status === "FAILED") {
      await supabase
        .from("video_jobs")
        .update({ status: "failed" })
        .eq("request_id", job.request_id);

      return json({ status: "failed", error: "Video generation failed." });
    }

    if (current.status !== "COMPLETED") {
      await supabase
        .from("video_jobs")
        .update({ status: current.status.toLowerCase() })
        .eq("request_id", job.request_id);

      return json({ status: current.status.toLowerCase() });
    }

    const resultResponse = await fetch(base, { headers });

    if (!resultResponse.ok) {
      return json({ error: "Video result is not available yet." }, 502);
    }

    const result = await resultResponse.json();
    const videoUrl = result.video?.url;

    if (!videoUrl) {
      return json({ error: "The provider returned no video URL." }, 502);
    }

    await supabase
      .from("video_jobs")
      .update({ status: "completed", video_url: videoUrl })
      .eq("request_id", job.request_id);

    return json({
      status: "completed",
      video_url: videoUrl,
      duration: result.video?.duration,
    });
  } catch (error: any) {
    console.error("Video status error:", error);
    return json(
      { error: error?.message || "Unable to check video status." },
      500
    );
  }
});
