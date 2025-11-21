import { useState } from "react";

export default function ChatbotCard() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");

  async function ask() {
    if (!question.trim()) return;
    try {
      const res = await fetch("/api/meeting/qa", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      const json = await res.json();
      setAnswer(json.answer || "(pas de réponse)");
    } catch {
      setAnswer("Erreur lors de la requête à l'agent.");
    }
  }

  return (
    <div className="relative h-full">
      <div className="absolute -inset-0.5 rounded-3xl bg-gradient-to-b from-purple-500/40 via-sky-500/30 to-emerald-500/40 opacity-70 blur-xl" />
      <div className="relative bg-neutral-950/95 border border-neutral-800 rounded-3xl p-4 flex flex-col gap-3 shadow-[0_28px_70px_-45px_rgba(0,0,0,1)] h-full">
        <div>
          <div className="flex items-center justify-between gap-2 mb-1">
            <div className="flex items-center gap-2">
              <span className="inline-flex h-6 w-6 items-center justify-center rounded-full bg-purple-500/30 border border-purple-400/50 text-[13px]">
                🤖
              </span>
              <h2 className="text-sm font-semibold text-neutral-100">
                Ask the meeting
              </h2>
            </div>
          </div>
          <p className="text-[11px] text-neutral-500">
          </p>
        </div>

        {/* input */}
        <div className="flex items-center gap-2 text-xs">
          <input
            className="flex-1 bg-neutral-950 border border-neutral-700 text-neutral-100 rounded-2xl px-3 py-2 text-xs outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500/60 transition"
            placeholder="Ask a question ..."
            value={question}
            onChange={e => setQuestion(e.target.value)}
            onKeyDown={e => e.key === "Enter" && ask()}
          />
          <button
            className="px-3 py-2 rounded-2xl bg-emerald-600 hover:bg-emerald-500 text-xs font-semibold text-white shadow-md shadow-emerald-900/60 transition"
            onClick={ask}
          >
            Envoyer
          </button>
        </div>

        {/* answer */}
        <div className="flex-1 bg-neutral-950/80 border border-neutral-800 rounded-2xl px-3 py-3 text-xs text-neutral-100 leading-relaxed custom-scroll overflow-y-auto">
          {answer ? (
            <div className="space-y-2">
              <div className="inline-flex items-center gap-1 rounded-full bg-emerald-500/10 border border-emerald-500/40 px-2 py-0.5 text-[10px] text-emerald-200">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                Réponse de l’agent
              </div>
              <div>{answer}</div>
            </div>
          ) : (
            <div className="text-neutral-500">…</div>
          )}
        </div>
      </div>
    </div>
  );
}
