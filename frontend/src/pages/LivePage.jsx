import { useEffect, useState } from "react";
import ActionBar from "../components/ActionBar.jsx";
import ParticipantsCard from "../components/ParticipantsCard.jsx";
import LiveTranslationCard from "../components/LiveTranslationCard.jsx";
import ChatbotCard from "../components/ChatbotCard.jsx";

export default function LivePage() {
  const [live, setLive] = useState({
    status: "stopped",
    meet_link: null,
    participants: [],
    recent_chunks: [],
  });

  // Polling de l'état live
  useEffect(() => {
    let cancelled = false;

    async function fetchState() {
      try {
        const res = await fetch("/api/live/state");
        const json = await res.json();
        if (!cancelled) {
          setLive(json);
        }
      } catch {
        // on ignore les erreurs réseau pour la démo
      }
    }

    fetchState();
    const id = setInterval(fetchState, 1500);
    return () => {
      cancelled = true;
      clearInterval(id);
    };
  }, []);

  async function handleEndMeeting() {
    try {
      await fetch("/api/meeting/stop", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });
      setLive(prev => ({ ...prev, status: "stopped" }));
    } catch {
      // rien de spécial pour la démo
    }
  }

  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      {/* HERO / STATUS */}
      <section className="relative overflow-hidden rounded-3xl border border-neutral-800 bg-[radial-gradient(circle_at_top,_#22c55e33,_transparent_55%),radial-gradient(circle_at_bottom_left,_#0ea5e933,_transparent_55%),radial-gradient(circle_at_bottom_right,_#a855f733,_transparent_55%),#020617] px-6 py-5 shadow-[0_30px_80px_-40px_rgba(0,0,0,1)]">
        {/* décorations */}
        <div className="pointer-events-none absolute inset-0 opacity-60">
          <div className="absolute -left-24 -top-16 h-40 w-40 rounded-full bg-emerald-400/40 blur-3xl" />
          <div className="absolute right-0 top-0 h-44 w-44 rounded-full bg-sky-400/40 blur-3xl" />
          <div className="absolute left-1/3 bottom-[-80px] h-48 w-48 rounded-full bg-purple-500/35 blur-3xl" />
        </div>

        <div className="relative flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <div className="inline-flex items-center gap-2 rounded-full bg-black/40 border border-white/10 px-3 py-1 text-[11px] text-neutral-100">
              <span className="inline-flex h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
              Live workspace
              <span className="mx-1 text-neutral-500">•</span>
            </div>
            <h2 className="mt-2 text-lg md:text-xl font-semibold text-white tracking-tight">
              Follow the meeting in real time.
            </h2>
            <p className="mt-1 text-xs text-neutral-300 max-w-md">
              Audio, transcription, EN → FR translation and the AI chatbot are updated
              continuously while you speak — perfect for your demo.
            </p>
          </div>

          <div className="w-full lg:w-auto">
            <div className="rounded-2xl bg-black/60 border border-white/10 px-3 py-3 backdrop-blur-xl shadow-[0_20px_50px_-35px_rgba(0,0,0,1)]">
              <ActionBar status={live.status} onEnd={handleEndMeeting} />
            </div>
          </div>
        </div>
      </section>

      {/* MAIN GRID */}
      <section className="grid grid-cols-1 xl:grid-cols-[minmax(0,1.05fr)_minmax(0,1.8fr)_minmax(0,1.1fr)] gap-6">
        {/* LEFT COLUMN : participants + lien */}
        <div className="space-y-4">
          <ParticipantsCard participants={live.participants} />

          <div className="relative">
            <div className="absolute -inset-0.5 rounded-2xl bg-gradient-to-r from-emerald-500/40 via-sky-500/40 to-purple-500/40 opacity-60 blur-xl" />
            <div className="relative bg-neutral-950/90 border border-neutral-800 rounded-2xl p-4 shadow-[0_24px_60px_-40px_rgba(0,0,0,1)]">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2 text-xs font-semibold text-neutral-200">
                  <span className="inline-flex h-5 w-5 items-center justify-center rounded-full bg-neutral-900 border border-neutral-700">
                    🔗
                  </span>
                  Lien Meet
                </div>
                <span className="text-[11px] text-neutral-500">Read-only</span>
              </div>

              {live.meet_link ? (
                <a
                  href={live.meet_link}
                  target="_blank"
                  rel="noreferrer"
                  className="text-xs text-emerald-400 hover:text-emerald-300 underline underline-offset-2 break-all"
                >
                  {live.meet_link}
                </a>
              ) : (
                <div className="text-xs text-neutral-500">
                  Aucun lien détecté pour le moment.
                </div>
              )}

              <div className="mt-3 flex flex-wrap gap-2 text-[11px] text-neutral-400">
                <span className="inline-flex items-center gap-1 rounded-full bg-neutral-900 border border-neutral-700 px-2 py-1">
                  🎙️ Audio → text
                </span>
                <span className="inline-flex items-center gap-1 rounded-full bg-neutral-900 border border-neutral-700 px-2 py-1">
                  🌐 EN → FR
                </span>
                <span className="inline-flex items-center gap-1 rounded-full bg-neutral-900 border border-neutral-700 px-2 py-1">
                  ✨ Summary + chatbot
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* MIDDLE COLUMN : transcription / traduction */}
        <div className="flex flex-col gap-4">
          <LiveTranslationCard chunks={live.recent_chunks} />
        </div>

        {/* RIGHT COLUMN : chatbot */}
        <div className="flex flex-col gap-4">
          <ChatbotCard />
        </div>
      </section>
    </div>
  );
}
