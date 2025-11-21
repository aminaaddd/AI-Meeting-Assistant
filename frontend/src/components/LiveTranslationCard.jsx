/// File: src/components/LiveTranslationCard.jsx
import { useEffect, useRef } from "react";


export default function LiveTranslationCard({ chunks = [] }){
const bottomRef = useRef(null);
useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: "smooth" }); }, [chunks]);


return (
<div className="bg-neutral-900/60 border border-neutral-800 rounded-2xl p-4 h-[60vh] overflow-auto custom-scroll">
{chunks.map((c, i) => (
<div key={i}
className="mb-3 p-3 rounded-xl border border-neutral-700 bg-neutral-800/60 animate-[fadein_0.6s_ease]">
<div className="text-xs text-neutral-400">Recognized</div>
<div className="text-sm">{c.text}</div>
{c.translated && (
<>
<div className="text-xs text-neutral-400 mt-2">Translated</div>
<div className="text-sm text-emerald-300">{c.translated}</div>
</>
)}
</div>
))}
<div ref={bottomRef} />
<style>{`@keyframes fadein{from{background:rgba(34,197,94,.08)}to{background:transparent}}`}</style>
</div>
);
}