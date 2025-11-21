import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import HomePage from "./pages/HomePage.jsx";
import LivePage from "./pages/LivePage.jsx";
import SummaryPage from "./pages/SummaryPage.jsx";
import DownloadPdfButton from "./components/DownloadPdfButton.jsx";

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-neutral-950 text-neutral-100 flex flex-col">
        {/* Top nav */}
        <header className="sticky top-0 z-30 backdrop-blur-xl bg-[rgba(0,0,0,0.75)] border-b border-white/10 shadow-[0_20px_60px_-20px_rgba(0,0,0,0.9)]">
          <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="h-7 w-7 rounded-xl bg-gradient-to-tr from-emerald-400 via-sky-400 to-purple-500 shadow-[0_0_20px_rgba(56,189,248,0.7)]" />
              <div className="text-lg font-semibold tracking-tight">
                <span className="bg-gradient-to-r from-emerald-300 via-sky-300 to-purple-300 bg-clip-text text-transparent">
                  Meeting Assistant
                </span>
              </div>
            </div>

            <nav className="flex items-center gap-5 text-sm">
              <Link
                to="/"
                className="text-neutral-300 hover:text-white transition"
              >
                Home
              </Link>
              <Link
                to="/live"
                className="text-neutral-300 hover:text-white transition"
              >
                Live
              </Link>
              <Link
                to="/summary"
                className="text-neutral-300 hover:text-white transition"
              >
                Summary
              </Link>

              <DownloadPdfButton className="ml-3" />
            </nav>
          </div>
        </header>

        <main className="flex-1 p-6">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/live" element={<LivePage />} />
            <Route path="/summary" element={<SummaryPage />} />
          </Routes>
        </main>
        {/* 🔹 Footer crédit */}
        <footer className="border-t border-neutral-900 bg-black/70 text-[11px] text-neutral-500">
          <div className="max-w-6xl mx-auto px-6 py-3 flex items-center justify-center text-center">
            <span>
              © {new Date().getFullYear()} AI Meeting Assistant  {" "}
              <span className="text-neutral-300 font-medium">Amina Addi & Mahek Makwana</span>.
            </span>
          </div>
        </footer>
      </div>
    </BrowserRouter>
  );
}
