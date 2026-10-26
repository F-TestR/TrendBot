// Trend bot — Discord slash commands (Cloudflare Worker, free plan).
//
// Discord sends each slash command here. The worker:
//   1. checks the request really comes from Discord (Ed25519 signature),
//   2. replies straight away with "Trend bot is thinking…",
//   3. starts the bot's GitHub workflow with the question,
// and the bot edits that reply with the answer about a minute later.
//
// Worker secrets (Settings → Variables and Secrets):
//   DISCORD_PUBLIC_KEY  — Discord Developer Portal → your app → General Information → Public Key
//   GITHUB_TOKEN        — fine-grained GitHub token with "Actions: Read and write" on the bot's repo only
//   GITHUB_REPO         — e.g.  F-TestR/TrendBot
//   ALLOWED_USERS       — optional: comma-separated Discord user IDs allowed to use the commands

const WORKFLOW = "trendbot.yml";

export default {
  async fetch(request, env, ctx) {
    if (request.method !== "POST") {
      return new Response("Trend bot interactions endpoint is running.", { status: 200 });
    }
    const signature = request.headers.get("X-Signature-Ed25519");
    const timestamp = request.headers.get("X-Signature-Timestamp");
    const body = await request.text();
    if (!signature || !timestamp || !(await verify(env.DISCORD_PUBLIC_KEY, signature, timestamp, body))) {
      return new Response("invalid request signature", { status: 401 });
    }
    const interaction = JSON.parse(body);

    if (interaction.type === 1) return json({ type: 1 }); // Discord's "ping" when you save the endpoint URL

    if (interaction.type === 2) {
      const user = (interaction.member && interaction.member.user) || interaction.user || {};
      const allowed = (env.ALLOWED_USERS || "").split(",").map((s) => s.trim()).filter(Boolean);
      if (allowed.length && !allowed.includes(user.id)) {
        return json({ type: 4, data: { content: "Sorry, this bot only answers its owner.", flags: 64 } });
      }
      const question = toQuestion(interaction.data);
      if (!question) {
        return json({ type: 4, data: { content: helpText(), flags: 64 } });
      }
      ctx.waitUntil(dispatch(env, question, interaction));
      return json({ type: 5 }); // "Trend bot is thinking…"
    }
    return new Response("unsupported interaction", { status: 400 });
  },
};

function toQuestion(data) {
  const opt = Object.fromEntries((data.options || []).map((o) => [o.name, String(o.value || "").slice(0, 200)]));
  switch (data.name) {
    case "ask": return opt.question || "";
    case "game": return opt.name ? `how is ${opt.name} doing` : "";
    case "compare": return opt.first && opt.second ? `${opt.first} vs ${opt.second}` : "";
    case "theme": return opt.word ? `is ${opt.word} trending` : "";
    case "top": return "what's rising";
    case "money": return opt.topic ? `${opt.topic} money` : "which genres earn the most";
    case "longterm": return "long term games";
    case "algorithm": return "what is roblox rewarding";
    case "coming": return "what's coming up";
    default: return "";
  }
}

function helpText() {
  return "Try `/game Wash the Car`, `/compare`, `/theme chocolate`, `/top`, `/money`, `/longterm`, `/algorithm`, `/coming` or `/ask` anything.";
}

async function dispatch(env, question, interaction) {
  const res = await fetch(`https://api.github.com/repos/${env.GITHUB_REPO}/actions/workflows/${WORKFLOW}/dispatches`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${env.GITHUB_TOKEN}`,
      Accept: "application/vnd.github+json",
      "User-Agent": "trendbot-discord-worker",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      ref: "main",
      inputs: { question, reply_token: interaction.token, reply_app: interaction.application_id },
    }),
  });
  if (!res.ok) {
    const detail = (await res.text()).slice(0, 300);
    await fetch(`https://discord.com/api/v10/webhooks/${interaction.application_id}/${interaction.token}/messages/@original`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content: `⚠️ Couldn't start the bot on GitHub (${res.status}). Check the worker's GITHUB_TOKEN and GITHUB_REPO.\n\`${detail}\`` }),
    });
  }
}

async function verify(publicKeyHex, signatureHex, timestamp, body) {
  try {
    const key = await crypto.subtle.importKey("raw", hex(publicKeyHex), { name: "Ed25519" }, false, ["verify"]);
    return await crypto.subtle.verify("Ed25519", key, hex(signatureHex), new TextEncoder().encode(timestamp + body));
  } catch (e) {
    try { // older Workers runtimes name the algorithm NODE-ED25519
      const key = await crypto.subtle.importKey("raw", hex(publicKeyHex), { name: "NODE-ED25519", namedCurve: "NODE-ED25519" }, false, ["verify"]);
      return await crypto.subtle.verify("NODE-ED25519", key, hex(signatureHex), new TextEncoder().encode(timestamp + body));
    } catch (e2) {
      return false;
    }
  }
}

function hex(s) {
  const out = new Uint8Array((s || "").length / 2);
  for (let i = 0; i < out.length; i++) out[i] = parseInt(s.substr(i * 2, 2), 16);
  return out;
}

function json(obj) {
  return new Response(JSON.stringify(obj), { headers: { "Content-Type": "application/json" } });
}
