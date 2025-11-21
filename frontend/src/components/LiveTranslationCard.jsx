import { useEffect, useRef } from "react";

export default function LiveTranslationCard({ chunks = [] }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chunks]);

  return (
    <div className="relative h-[60vh]">
      <div className="absolute -inset-0.5 rounded-3xl bg-gradient-to-b from-emerald-500/35 via-sky-500/25 to-purple-500/40 opacity-70 blur-xl" />
      <div className="relative h-full bg-neutral-950/95 border border-neutral-800 rounded-3xl p-4 flex flex-col shadow-[0_28px_70px_-45px_rgba(0,0,0,1)]">
        <div className="flex items-center justify-between mb-3">
          <div>
            <div className="text-xs font-semibold text-neutral-100">
              Live transcript & translation
            </div>
            <div className="text-[11px] text-neutral-500">
              New segments appear in real time as the meeting progresses.
            </div>
          </div>
          <span className="text-[11px] text-neutral-400">
            {chunks.length ? `${chunks.length} segments` : "Waiting for audio…"}
          </span>
        </div>

        <div className="flex-1 overflow-y-auto custom-scroll space-y-3 pr-1">
          {chunks.map((c, i) => (
            <div
              key={i}
              className="group relative rounded-2xl border border-neutral-800 bg-gradient-to-br from-neutral-900/90 via-neutral-900/80 to-neutral-950/90 px-3 py-3"
            >
              <div className="absolute left-0 top-3 bottom-3 w-1 rounded-full bg-gradient-to-b from-emerald-400 via-sky-400 to-purple-400 opacity-70" />
              <div className="ml-3 space-y-1.5">
                <div className="text-[11px] text-neutral-500 uppercase tracking-wide">
                  Recognized
                </div>
                <div className="text-sm text-neutral-100 leading-snug">
                  {c.text || "…"}
                </div>

                {c.translated && (
                  <>
                    <div className="pt-1 text-[11px] text-emerald-300 uppercase tracking-wide">
                      Translated (FR)
                    </div>
                    <div className="text-sm text-emerald-200 leading-snug">
                      {c.translated}
                    </div>
                  </>
                )}
              </div>
            </div>
          ))}

          <div ref={bottomRef} />
        </div>
      </div>
    </div>
  );
}
