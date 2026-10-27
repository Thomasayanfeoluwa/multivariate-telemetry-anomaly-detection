import { useEffect, useState } from "react";
import { Home } from "./pages/Home";
import { Dashboard } from "./pages/Dashboard";
import "./App.css";

export type Page = "home" | "dashboard";

function pageFromHash(): Page {
  return window.location.hash.replace(/^#\/?/, "") === "dashboard"
    ? "dashboard"
    : "home";
}

function hashFor(page: Page): string {
  return page === "dashboard" ? "#/dashboard" : "#/";
}

function App() {
  const [page, setPage] = useState<Page>(() => pageFromHash());

  useEffect(() => {
    const onHashChange = () => setPage(pageFromHash());
    window.addEventListener("hashchange", onHashChange);
    return () => window.removeEventListener("hashchange", onHashChange);
  }, []);

  // Ensure a hash exists on first load so a hard-refresh is deterministic.
  useEffect(() => {
    if (!window.location.hash) {
      window.history.replaceState(null, "", hashFor(page));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const navigate = (next: Page) => {
    // Fires hashchange, which triggers setPage via the listener above.
    window.location.hash = hashFor(next);
  };

  return page === "home" ? (
    <Home onEnter={() => navigate("dashboard")} />
  ) : (
    <Dashboard onExit={() => navigate("home")} />
  );
}

export default App;