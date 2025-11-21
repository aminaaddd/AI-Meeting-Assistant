import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import HomePage from "./pages/HomePage.jsx";
import LivePage from "./pages/LivePage.jsx";
import SummaryPage from "./pages/SummaryPage.jsx";
import DownloadPdfButton from "./components/DownloadPdfButton.jsx"; // ✅ import

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-neutral-950 text-neutral-100 flex flex-col">
        {/* Top nav */}
        <header className="border-b border-neutral-800 px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="text-lg font-semibold text-white">
              Meeting Assistant
            </div>
          </div>

          <nav className="flex gap-4 text-sm text-neutral-400">
            <Link to="/" className="hover:text-white">
              Home
            </Link>
            <Link to="/live" className="hover:text-white">
              Live
            </Link>
            <Link to="/summary" className="hover:text-white">
              Summary
            </Link>
            <DownloadPdfButton className="ml-2" /> {/* ✅ added here */}

          </nav>
        </header>

        <main className="flex-1 p-6">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/live" element={<LivePage />} />
            <Route path="/summary" element={<SummaryPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
