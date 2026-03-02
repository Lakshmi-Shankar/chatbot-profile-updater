import { useState } from "react";
import { useNavigate } from "react-router-dom";

const API_BASE = "https://chatbot-profile-updater.onrender.com/auth";

export default function AuthPage() {
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({ full_name: "", email: "", password: "" });
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const isLogin = mode === "login";

  const handleChange = (e) =>
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setStatus(null);

    const endpoint = isLogin ? `${API_BASE}/login` : `${API_BASE}/register`;
    const body = isLogin
      ? { email: form.email, password: form.password }
      : { full_name: form.full_name, email: form.email, password: form.password };

    try {
      const res = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      const data = await res.json();

      if (!res.ok) {
        const msg =
          typeof data.detail === "string"
            ? data.detail
            : Array.isArray(data.detail)
            ? data.detail.map((e) => e.msg).join(", ")
            : "Something went wrong.";
        setStatus({ type: "error", message: msg });
      } else {
        // ── Auto-login after register ──────────────────────
        if (!isLogin) {
          const loginRes = await fetch(`${API_BASE}/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email: form.email, password: form.password }),
          });
          const loginData = await loginRes.json();
          if (loginData.token) localStorage.setItem("token", loginData.token);
        } else {
          if (data.token) localStorage.setItem("token", data.token);
        }
        // ──────────────────────────────────────────────────
        navigate("/dashboard");
      }
    } catch {
      setStatus({ type: "error", message: "Could not reach server." });
    } finally {
      setLoading(false);
    }
  };

  const switchMode = () => {
    setMode(isLogin ? "register" : "login");
    setStatus(null);
    setForm({ full_name: "", email: "", password: "" });
  };

  return (
    <div
      className="min-h-screen bg-stone-100 flex items-center justify-center px-4"
      style={{ fontFamily: "'Syne', 'DM Sans', sans-serif" }}
    >
      <div className="w-full max-w-sm">

        {/* Card */}
        <div className="bg-white border border-stone-200 rounded-2xl shadow-sm overflow-hidden">

          {/* Top accent bar */}
          <div className="h-1.5 w-full bg-stone-900" />

          <div className="px-7 py-8">

            {/* Brand */}
            <div className="flex items-center gap-3 mb-8">
              <div className="w-9 h-9 bg-stone-900 rounded-xl flex items-center justify-center flex-shrink-0">
                <svg className="w-4 h-4 text-amber-400" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M10.394 2.08a1 1 0 00-.788 0l-7 3a1 1 0 000 1.84L5.25 8.051a.999.999 0 01.356-.257l4-1.714a1 1 0 11.788 1.838L7.667 9.088l1.94.831a1 1 0 00.787 0l7-3a1 1 0 000-1.838l-7-3zM3.31 9.397L5 10.12v4.102a8.969 8.969 0 00-1.05-.174 1 1 0 01-.89-.89 11.115 11.115 0 01.25-3.762zM9.3 16.573A9.026 9.026 0 007 14.935v-3.957l1.818.78a3 3 0 002.364 0l5.508-2.361a11.026 11.026 0 01.25 3.762 1 1 0 01-.89.89 8.968 8.968 0 00-5.35 2.524 1 1 0 01-1.4 0zM6 18a1 1 0 001-1v-2.065a8.935 8.935 0 00-2-.712V17a1 1 0 001 1z" />
                </svg>
              </div>
              <div>
                <p className="text-xs text-stone-400 leading-none">LMS Portal</p>
                <p className="text-sm font-bold text-stone-900 leading-tight">
                  {isLogin ? "Welcome back" : "Create account"}
                </p>
              </div>
            </div>

            {/* Tab switcher */}
            <div className="flex bg-stone-100 rounded-xl p-1 mb-6">
              {["login", "register"].map((m) => (
                <button
                  key={m}
                  onClick={() => { setMode(m); setStatus(null); setForm({ full_name: "", email: "", password: "" }); }}
                  className={`flex-1 text-xs font-semibold py-2 rounded-lg transition-all duration-200 ${
                    mode === m
                      ? "bg-stone-900 text-white shadow-sm"
                      : "text-stone-500 hover:text-stone-700"
                  }`}
                >
                  {m === "login" ? "Sign In" : "Sign Up"}
                </button>
              ))}
            </div>

            {/* Form */}
            <form onSubmit={handleSubmit} className="space-y-4">

              {!isLogin && (
                <div>
                  <label className="block text-xs font-semibold text-stone-500 mb-1.5 uppercase tracking-wide">
                    Full Name
                  </label>
                  <input
                    name="full_name"
                    type="text"
                    required
                    autoComplete="name"
                    value={form.full_name}
                    onChange={handleChange}
                    placeholder="Jane Doe"
                    className="w-full bg-stone-50 border border-stone-200 text-stone-900 text-sm rounded-xl px-3.5 py-2.5 placeholder-stone-400 focus:outline-none focus:border-amber-400 focus:ring-2 focus:ring-amber-100 transition-all"
                  />
                </div>
              )}

              <div>
                <label className="block text-xs font-semibold text-stone-500 mb-1.5 uppercase tracking-wide">
                  Email
                </label>
                <input
                  name="email"
                  type="email"
                  required
                  autoComplete="email"
                  value={form.email}
                  onChange={handleChange}
                  placeholder="you@example.com"
                  className="w-full bg-stone-50 border border-stone-200 text-stone-900 text-sm rounded-xl px-3.5 py-2.5 placeholder-stone-400 focus:outline-none focus:border-amber-400 focus:ring-2 focus:ring-amber-100 transition-all"
                />
              </div>

              <div>
                <div className="flex justify-between items-center mb-1.5">
                  <label className="block text-xs font-semibold text-stone-500 uppercase tracking-wide">
                    Password
                  </label>
                  {isLogin && (
                    <button
                      type="button"
                      className="text-xs text-stone-400 hover:text-amber-500 transition-colors font-medium"
                    >
                      Forgot?
                    </button>
                  )}
                </div>
                <input
                  name="password"
                  type="password"
                  required
                  minLength={6}
                  autoComplete={isLogin ? "current-password" : "new-password"}
                  value={form.password}
                  onChange={handleChange}
                  placeholder="••••••••"
                  className="w-full bg-stone-50 border border-stone-200 text-stone-900 text-sm rounded-xl px-3.5 py-2.5 placeholder-stone-400 focus:outline-none focus:border-amber-400 focus:ring-2 focus:ring-amber-100 transition-all"
                />
                {!isLogin && (
                  <p className="text-stone-400 text-xs mt-1.5">Minimum 6 characters</p>
                )}
              </div>

              {/* Status */}
              {status && (
                <div className={`flex items-start gap-2.5 text-xs px-3.5 py-3 rounded-xl border ${
                  status.type === "success"
                    ? "bg-emerald-50 text-emerald-700 border-emerald-200"
                    : "bg-red-50 text-red-600 border-red-200"
                }`}>
                  <svg className="w-3.5 h-3.5 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
                    {status.type === "success"
                      ? <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                      : <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01M12 3a9 9 0 110 18A9 9 0 0112 3z" />
                    }
                  </svg>
                  {status.message}
                </div>
              )}

              {/* Submit */}
              <button
                type="submit"
                disabled={loading}
                className="w-full bg-stone-900 text-white text-sm font-bold py-3 rounded-xl hover:bg-stone-700 active:bg-stone-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 mt-2"
              >
                {loading ? (
                  <>
                    <span className="w-1.5 h-1.5 bg-white rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                    <span className="w-1.5 h-1.5 bg-white rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                    <span className="w-1.5 h-1.5 bg-white rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                  </>
                ) : (
                  <>
                    {isLogin ? "Sign In" : "Create Account"}
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth={2.5} viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6" />
                    </svg>
                  </>
                )}
              </button>
            </form>
          </div>
        </div>

        {/* Footer note */}
        <p className="text-center text-xs text-stone-400 mt-5">
          {isLogin ? "Don't have an account?" : "Already have an account?"}{" "}
          <button
            onClick={switchMode}
            className="text-stone-700 hover:text-amber-600 transition-colors font-semibold"
          >
            {isLogin ? "Sign up" : "Sign in"}
          </button>
        </p>
      </div>
    </div>
  );
}