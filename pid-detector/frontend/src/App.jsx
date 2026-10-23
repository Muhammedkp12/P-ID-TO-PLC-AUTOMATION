import { Routes, Route } from "react-router-dom";
import Layout from "./components/Layout.jsx";
import Home from "./pages/Home.jsx";
import Features from "./pages/Features.jsx";
import HowItWorks from "./pages/HowItWorks.jsx";
import Detect from "./pages/Detect.jsx";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Home />} />
        <Route path="/features" element={<Features />} />
        <Route path="/how-it-works" element={<HowItWorks />} />
        <Route path="/detect" element={<Detect />} />
      </Route>
    </Routes>
  );
}