import { useState } from "react";
import { Home } from "./pages/Home";
import { Dashboard } from "./pages/Dashboard";
import "./App.css";

export type Page = "home" | "dashboard";

function App() {
  const [page, setPage] = useState<Page>("home");
  return page === "home" ? (
    <Home onEnter={() => setPage("dashboard")} />
  ) : (
    <Dashboard onExit={() => setPage("home")} />
  );
}

export default App;