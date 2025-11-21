import { useState } from "react";

export default function ChatbotCard() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");

  async function ask() {
    if (!question.trim()) return;
    const res = await fetch("/api/meeting/qa", {
      method: "POST",
      headers: { "Content-Type": "application/json"},
      body: JSON.stringify({ question })
    });
    const json = await res.json();
    setAnswer(json.answer || "(pas de réponse)");
  }

  return (
    <div className="bg-neutral-900/60 border border-neutral-800 rounded-2xl p-5 shadow-xl shadow-black/50 flex flex-col min-h-[200px]">
      <h2 className="text-sm font-semibold text-neutral-200 flex items-center gap-2 mb-3">
        <span role="img" aria-label="bot">🤖</span> Ask the meeting
      </h2>

      <div className="text-xs text-neutral-500 mb-3">
        Pose une question sur ce qui a été dit (tâches, décisions, deadlines…)
      </div>

      <div className="flex items-start gap-2 mb-3">
        <input
          className="flex-1 bg-neutral-800/60 border border-neutral-700 text-neutral-100 text-xs rounded-xl px-3 py-2 outline-none focus:border-emerald-500"
          placeholder="Ex: Qu'a dit John sur la deadline ?"
          value={question}
          onChange={e => setQuestion(e.target.value)}
        />
        <button
          className="px-3 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-xs font-medium text-white"
          onClick={ask}
        >
          Envoyer
        </button>
      </div>

      <div className="flex-1 bg-neutral-800/30 border border-neutral-700/50 rounded-xl p-3 text-xs text-neutral-200 whitespace-pre-line leading-relaxed custom-scroll overflow-y-auto min-h-[80px]">
        {answer || "…"}
      </div>
    </div>
  );
}
