import { useState, useEffect } from "react";
import MeetingInfoCard from "../components/MeetingInfoCard.jsx";

export default function HomePage() {
  const [emails, setEmails] = useState("");
  const [sourceLang, setSourceLang] = useState("en");
  const [targetLang, setTargetLang] = useState("fr");
  const [title, setTitle] = useState("AI Agent Sync");

  const [inviteStatus, setInviteStatus] = useState("");
  const [startStatus, setStartStatus] = useState("");
  const [meetLinkStatus, setMeetLinkStatus] = useState("");

  async function sendInvites() {
    const list = emails
      .split(/[,\s;]/)
      .map(e => e.trim())
      .filter(Boolean);

    const body = {
      emails: list,
      title,
      start_time: new Date().toISOString(),
      duration_minutes: 30,
      description: "Meeting scheduled via Meeting Assistant",
    };

    const res = await fetch("/api/meeting/invite", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const json = await res.json();
    if (json.ok) {
      setInviteStatus("Invitations sent ✅");
    } else {
      setInviteStatus("Error sending invitations ❌");
    }
  }

  async function startMeeting() {
    const body = {
      source_lang: sourceLang,
      target_lang: targetLang,
      title,
    };

    const res = await fetch("/api/meeting/start", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const json = await res.json();
    if (json.ok) {
      setStartStatus("Meeting started ✅ (audio is listening)");
    } else {
      setStartStatus("Error starting meeting ❌");
    }
  }
  async function createMeetLink() {
    try {
      const res = await fetch("/api/meeting/create_link", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });

      const json = await res.json();
      if (json.ok) {
        setMeetLinkStatus("Meet link created ✅");
      } else {
        setMeetLinkStatus("Error creating Meet link ❌");
      }
    } catch (err) {
      console.error(err);
      setMeetLinkStatus("Error creating Meet link ❌");
    }
  }


  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* left */}
      <div className="space-y-6">
        <MeetingInfoCard />

        <div className="bg-neutral-900/60 border border-neutral-800 rounded-2xl p-5 shadow-xl shadow-black/50 text-sm space-y-4">
          <div>
            <div className="text-sm font-semibold text-neutral-200 flex items-center gap-2 mb-2">
              📧 Invitations
            </div>
            <div className="text-xs text-neutral-500 mb-2">
              Enter multiple emails separated by commas or spaces.
            </div>
            <textarea
              className="w-full min-h-[60px] bg-neutral-800/60 border border-neutral-700 text-neutral-100 text-xs rounded-xl px-3 py-2 outline-none focus:border-emerald-500"
              placeholder="alice@company.com, bob@company.com..."
              value={emails}
              onChange={e => setEmails(e.target.value)}
            />
            <div className="mt-2 flex flex-wrap gap-2">
              <button
                className="px-3 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-xs font-medium text-white"
                onClick={sendInvites}
              >
                Send invitations
              </button>

            </div>

            <div className="text-xs text-neutral-400 mt-2 h-4">
              {inviteStatus}
            </div>
            <div className="text-xs text-neutral-400 mt-1 h-4">
              {meetLinkStatus} {/* NEW */}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4 text-xs">
            <div>
              <div className="text-neutral-500 uppercase tracking-wide mb-1 text-[10px]">
                Source language
              </div>
              <input
                className="w-full bg-neutral-800/60 border border-neutral-700 text-neutral-100 rounded-xl px-3 py-2 outline-none focus:border-emerald-500"
                value={sourceLang}
                onChange={e => setSourceLang(e.target.value)}
              />
            </div>
            <div>
              <div className="text-neutral-500 uppercase tracking-wide mb-1 text-[10px]">
                Target language
              </div>
              <input
                className="w-full bg-neutral-800/60 border border-neutral-700 text-neutral-100 rounded-xl px-3 py-2 outline-none focus:border-emerald-500"
                value={targetLang}
                onChange={e => setTargetLang(e.target.value)}
              />
            </div>
          </div>

          <div>
            <div className="text-neutral-500 uppercase tracking-wide mb-1 text-[10px]">
              Meeting title
            </div>
            <input
              className="w-full bg-neutral-800/60 border border-neutral-700 text-neutral-100 rounded-xl px-3 py-2 text-xs outline-none focus:border-emerald-500"
              value={title}
              onChange={e => setTitle(e.target.value)}
            />
          </div>

          <button
            className="w-full px-3 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-xs font-medium text-white"
            onClick={startMeeting}
          >
            ▶️ Start meeting (audio ON)
          </button>

          <div className="text-xs text-neutral-400 mt-2 h-4">{startStatus}</div>
        </div>
      </div>

      {/* right */}
      <div className="text-sm text-neutral-400 leading-relaxed bg-neutral-900/40 border border-neutral-800 rounded-2xl p-5 shadow-xl shadow-black/50">
        <div className="text-neutral-200 font-semibold text-base mb-2">
          How does it work?
        </div>
        <ol className="list-decimal list-inside space-y-2 text-xs text-neutral-300">
          <li>Add emails and send the Meet invitations.</li>
          <li>Select the language people speak and your target language.</li>
          <li>Start the meeting — the microphone begins listening and translating.</li>
          <li>Go to the Live tab to view the real-time summary.</li>
          <li>At the end, click End meeting, then go to Summary to download the report.</li>
        </ol>
      </div>
    </div>
  );
}
