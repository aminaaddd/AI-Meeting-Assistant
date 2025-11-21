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
    speaker: null,
    recent_chunks: []
  });

  useEffect(() => {
    const interval = setInterval(() => {
      fetch("/api/live/state")
        .then(r => r.json())
        .then(json => setLive(json))
        .catch(() => {});
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  async function endMeeting() {
    await fetch("/api/meeting/stop", {
      method: "POST"
    });
    // si tu veux forcer le user à aller vers la page Summary à la fin :
    // window.location.href = "/summary";
  }

  return (
    <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
      {/* full width status + bouton end meeting */}
      <div className="xl:col-span-3">
        <ActionBar status={live.status} onEnd={endMeeting} />
      </div>

      {/* LEFT COLUMN */}
      <div className="space-y-6">
        <ParticipantsCard
          participants={live.participants}
          speaker={live.speaker}
        />

        <div className="bg-neutral-900/40 border border-neutral-800 rounded-2xl p-4 text-xs text-neutral-400 shadow-xl shadow-black/50 break-all">
          <div className="text-neutral-500 uppercase tracking-wide mb-2 text-[10px]">
            Lien Meet
          </div>
          {live.meet_link ? (
            <a
              className="text-emerald-400 hover:text-emerald-300 underline text-xs break-all"
              href={live.meet_link}
              target="_blank"
              rel="noreferrer"
            >
              {live.meet_link}
            </a>
          ) : (
            <div className="text-neutral-500 text-xs">
              Pas de lien
            </div>
          )}
        </div>
      </div>

      {/* MIDDLE COLUMN: traduction en direct */}
      <div className="flex flex-col gap-6">
        <LiveTranslationCard chunks={live.recent_chunks} />
      </div>

      {/* RIGHT COLUMN: chatbot */}
      <div className="flex flex-col gap-6">
        <ChatbotCard />
      </div>
    </div>
  );
}
