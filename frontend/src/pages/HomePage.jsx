import { useState } from "react";
import MeetingInfoCard from "../components/MeetingInfoCard.jsx";

export default function HomePage() {
  const [emails, setEmails] = useState("");
  const [title, setTitle] = useState("AI Agent");
  const [inviteStatus, setInviteStatus] = useState("");
  const [startStatus, setStartStatus] = useState("");

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

    try {
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
    } catch {
      setInviteStatus("Error sending invitations ❌");
    }
  }

  async function startMeeting() {
    const body = {
      source_lang: "en",
      target_lang: "fr",
      title,
    };

    try {
      const res = await fetch("/api/meeting/start", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const json = await res.json();
      if (json.ok) {
        setStartStatus("Meeting started ✅ — audio is listening");
      } else {
        setStartStatus("Error starting meeting ❌");
      }
    } catch {
      setStartStatus("Error starting meeting ❌");
    }
  }

  return (
    <div className="space-y-10 max-w-6xl mx-auto">
      {/* HERO SECTION */}
      <section className="relative mt-2 overflow-hidden rounded-3xl border border-neutral-800 bg-gradient-to-br from-emerald-500/20 via-slate-900 to-purple-700/30 px-6 py-8 shadow-[0_40px_100px_-50px_rgba(0,0,0,1)]">
        {/* décorations */}
        <div className="pointer-events-none absolute inset-0 opacity-60">
          <div className="absolute -left-24 top-0 h-56 w-56 rounded-full bg-emerald-500/35 blur-3xl" />
          <div className="absolute right-[-40px] top-10 h-64 w-64 rounded-full bg-sky-500/40 blur-3xl" />
          <div className="absolute left-1/3 bottom-[-80px] h-64 w-64 rounded-full bg-purple-500/25 blur-3xl" />
        </div>

        <div className="relative grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
          {/* LEFT : tagline */}
          <div className="space-y-5">
            <div className="inline-flex items-center gap-2 rounded-full bg-black/50 border border-white/10 px-3 py-1 text-[11px] text-neutral-100">
              <span className="inline-flex h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
              AI Meeting Assistant
              <span className="mx-1 text-neutral-500">•</span>
              <span className="text-neutral-300">Optimized for live demos</span>
            </div>

            <h1 className="text-3xl lg:text-4xl font-semibold text-white tracking-tight leading-tight">
              Let your meeting run,
              <span className="text-emerald-300"> the agent writes everything down.</span>
            </h1>

            <p className="text-sm text-neutral-200/90 max-w-xl">
              Generate a Google Meet, invite your participants and start listening.
              The agent takes care of transcription, EN → FR translation, live summary
              and a polished PDF report for your stakeholders.
            </p>

            <div className="flex flex-wrap gap-3 text-[11px]">
              <span className="inline-flex items-center gap-1 rounded-full bg-black/50 border border-white/10 px-3 py-1 text-neutral-200">
                🎙️ Real-time speech-to-text
              </span>
              <span className="inline-flex items-center gap-1 rounded-full bg-black/50 border border-white/10 px-3 py-1 text-neutral-200">
                🌐 Auto translation to French
              </span>
              <span className="inline-flex items-center gap-1 rounded-full bg-black/50 border border-white/10 px-3 py-1 text-neutral-200">
                ✨ AI recap & chatbot
              </span>
            </div>

            <div className="flex flex-wrap gap-3 text-[11px] text-neutral-400 pt-1">
            </div>
          </div>

          {/* RIGHT : glass card with current meeting + quick controls */}
          <div className="relative">
            <div className="absolute -inset-1 rounded-3xl bg-gradient-to-tr from-emerald-400/40 via-transparent to-sky-400/40 blur-xl opacity-80" />
            <div className="relative rounded-3xl bg-black/70 border border-white/12 px-4 py-4 shadow-[0_25px_70px_-35px_rgba(0,0,0,1)] backdrop-blur-xl">
              <div className="flex items-center justify-between mb-3">
                <div>
                  <div className="text-xs font-semibold text-neutral-100 tracking-wide">
                    Current meeting
                  </div>
                  <div className="text-[11px] text-neutral-400">
                    Meet link, time window & attendees.
                  </div>
                </div>
                <div className="flex flex-col items-end gap-1 text-[11px]">
                  <span className="inline-flex items-center gap-1 rounded-full bg-emerald-500/10 border border-emerald-500/50 px-2 py-1 text-emerald-200">
                    <span className="inline-flex h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
                    Ready to record
                  </span>
                  <span className="text-neutral-400">
                    Source: EN · Target: FR
                  </span>
                </div>
              </div>

              <div className="rounded-2xl border border-white/10 bg-neutral-900/80">
                <MeetingInfoCard />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* SETUP SECTION */}
      <section className="grid grid-cols-1 xl:grid-cols-[minmax(0,2.1fr)_minmax(0,1.3fr)] gap-6">
        {/* LEFT : setup card */}
        <div className="bg-neutral-900/85 border border-neutral-800 rounded-3xl p-6 shadow-[0_24px_60px_-40px_rgba(0,0,0,1)] space-y-6">
          <div className="flex items-center justify-between gap-2">
            <div>
              <div className="text-sm font-semibold text-neutral-200">
                Setup your next session
              </div>
              <div className="text-xs text-neutral-500">
                Send invitations and define the meeting title before going live.
              </div>
            </div>
            <div className="hidden md:flex items-center gap-2 text-[11px] text-neutral-400">
              <span className="inline-flex h-6 w-6 items-center justify-center rounded-lg bg-neutral-800 border border-neutral-700">
                1
              </span>
              <span>Invite</span>
              <span className="h-px w-4 bg-neutral-700" />
              <span className="inline-flex h-6 w-6 items-center justify-center rounded-lg bg-neutral-800 border border-neutral-700">
                2
              </span>
              <span>Start</span>
              <span className="h-px w-4 bg-neutral-700" />
              <span className="inline-flex h-6 w-6 items-center justify-center rounded-lg bg-neutral-800 border border-neutral-700">
                3
              </span>
              <span>Live / Summary</span>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
            {/* Invitations */}
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-xs font-medium text-neutral-300">
                <span className="inline-flex h-5 w-5 items-center justify-center rounded-full bg-emerald-500/20 border border-emerald-500/50 text-[11px]">
                  📧
                </span>
                Invitations
              </div>
              <div className="text-[11px] text-neutral-500">
                Add one or more email addresses separated by commas or spaces.
              </div>
              <textarea
                className="w-full min-h-[90px] bg-neutral-950/80 border border-neutral-700 text-neutral-100 text-xs rounded-2xl px-3 py-2 outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500/60 transition"
                placeholder="alice@company.com, bob@company.com..."
                value={emails}
                onChange={e => setEmails(e.target.value)}
              />
              <button
                className="inline-flex items-center justify-center gap-2 px-3 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-xs font-medium text-white shadow-md shadow-emerald-900/70 transition"
                onClick={sendInvites}
              >
                Send invitations
              </button>
              <div className="text-[11px] text-neutral-400 h-4">{inviteStatus}</div>
            </div>

            {/* Title + start */}
            <div className="space-y-3">
              <div>
                <div className="text-neutral-500 uppercase tracking-wide mb-1 text-[10px]">
                  Meeting title
                </div>
                <input
                  className="w-full bg-neutral-950/80 border border-neutral-700 text-neutral-100 rounded-2xl px-3 py-2 text-xs outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500/60 transition"
                  value={title}
                  onChange={e => setTitle(e.target.value)}
                />
              </div>

              <div className="flex flex-wrap gap-2 text-[11px] text-neutral-500">
                <span className="inline-flex items-center gap-1 rounded-full bg-neutral-900 border border-neutral-700 px-2 py-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                  Source: EN
                </span>
                <span className="inline-flex items-center gap-1 rounded-full bg-neutral-900 border border-neutral-700 px-2 py-1">
                  Target: FR
                </span>
                <span className="inline-flex items-center gap-1 rounded-full bg-neutral-900 border border-neutral-700 px-2 py-1">
                  Uses default microphone
                </span>
              </div>

              <button
                className="w-full inline-flex items-center justify-center gap-2 px-3 py-2 rounded-2xl bg-emerald-600 hover:bg-emerald-500 text-xs font-semibold text-white shadow-lg shadow-emerald-900/80 transition"
                onClick={startMeeting}
              >
                <span className="text-base">▷</span>
                <span>Start meeting &amp; begin listening</span>
              </button>

              <div className="text-[11px] text-neutral-400 h-4">
                {startStatus}
              </div>
            </div>
          </div>
        </div>

        {/* RIGHT : “what the agent does” card */}
        <div className="bg-neutral-900/85 border border-neutral-800 rounded-3xl p-5 shadow-[0_24px_60px_-40px_rgba(0,0,0,1)] space-y-4">
          <div>
            <div className="text-sm font-semibold text-neutral-200">
              What happens after you click “Start”
            </div>
            <div className="text-xs text-neutral-500">
              A quick overview of the pipeline your audience will see in action.
            </div>
          </div>

          <div className="space-y-3 text-[11px] text-neutral-300">
            <div className="flex gap-3">
              <div className="mt-0.5 h-7 w-7 rounded-full bg-emerald-500/15 border border-emerald-500/60 flex items-center justify-center">
                🎙️
              </div>
              <div>
                <div className="font-medium text-neutral-100">
                  1. Audio capture & transcription
                </div>
                <div className="text-neutral-400">
                  The assistant listens to the meeting, converts speech to text and
                  streams chunks in the Live view.
                </div>
              </div>
            </div>

            <div className="flex gap-3">
              <div className="mt-0.5 h-7 w-7 rounded-full bg-sky-500/15 border border-sky-500/60 flex items-center justify-center">
                🌐
              </div>
              <div>
                <div className="font-medium text-neutral-100">
                  2. Translation to French
                </div>
                <div className="text-neutral-400">
                  Each chunk is translated so summaries, actions and chatbot answers stay
                  in French for your audience.
                </div>
              </div>
            </div>

            <div className="flex gap-3">
              <div className="mt-0.5 h-7 w-7 rounded-full bg-purple-500/15 border border-purple-500/60 flex items-center justify-center">
                ✨
              </div>
              <div>
                <div className="font-medium text-neutral-100">
                  3. Live summary & exportable report
                </div>
                <div className="text-neutral-400">
                  On the Live and Summary tabs, you can show the evolving recap, action
                  items and download a PDF styled for your demo.
                </div>
              </div>
            </div>
          </div>

          <div className="text-[11px] text-neutral-500 border-t border-neutral-800 pt-3">
            Demo tip: you can play a pre-recorded video or audio near your microphone
            and let the assistant generate the whole report automatically.
          </div>
        </div>
      </section>
    </div>
  );
}
