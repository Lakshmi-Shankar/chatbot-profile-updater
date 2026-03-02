import { useState, useEffect, useRef } from "react";

const API = "https://chatbot-profile-updater.onrender.com";

const getToken = () => localStorage.getItem("token");
const authHeaders = () => ({
  "Content-Type": "application/json",
  Authorization: `Bearer ${getToken()}`,
});

async function apiFetch(path, options = {}) {
  const res = await fetch(`${API}${path}`, {
    ...options,
    headers: { ...authHeaders(), ...(options.headers || {}) },
  });
  const data = await res.json();
  if (!res.ok) {
    const msg =
      typeof data.detail === "string"
        ? data.detail
        : Array.isArray(data.detail)
        ? data.detail.map((e) => e.msg).join(", ")
        : "Request failed";
    throw new Error(msg);
  }
  return data;
}

function EditableField({ value, onSave, placeholder = "—", className = "" }) {
  const [editing, setEditing] = useState(false);
  const [val, setVal] = useState(value || "");
  const inputRef = useRef(null);

  useEffect(() => { setVal(value || ""); }, [value]);
  useEffect(() => { if (editing) inputRef.current?.focus(); }, [editing]);

  const commit = () => {
    setEditing(false);
    if (val !== value) onSave(val);
  };

  if (editing) {
    return (
      <input
        ref={inputRef}
        value={val}
        onChange={(e) => setVal(e.target.value)}
        onBlur={commit}
        onKeyDown={(e) => e.key === "Enter" && commit()}
        className={`bg-transparent border-b-2 border-amber-400 outline-none ${className}`}
      />
    );
  }
  return (
    <span
      onClick={() => setEditing(true)}
      className={`cursor-text group relative ${className}`}
      title="Click to edit"
    >
      {value || <span className="opacity-30 italic">{placeholder}</span>}
      <span className="absolute -right-5 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-60 transition-opacity text-amber-500">
        <svg className="w-3 h-3" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" d="M15.232 5.232l3.536 3.536M9 13l6.586-6.586a2 2 0 112.828 2.828L11.828 15.828a2 2 0 01-1.414.586H9v-2.414A2 2 0 019.586 13z" />
        </svg>
      </span>
    </span>
  );
}

const STATUS_CONFIG = {
  submitted:    { label: "Submitted",    dot: "bg-sky-400",    text: "text-sky-600",    bg: "bg-sky-50 border-sky-200" },
  under_review: { label: "Under Review", dot: "bg-amber-400",  text: "text-amber-600",  bg: "bg-amber-50 border-amber-200" },
  accepted:     { label: "Accepted",     dot: "bg-emerald-400",text: "text-emerald-600",bg: "bg-emerald-50 border-emerald-200" },
  rejected:     { label: "Rejected",     dot: "bg-red-400",    text: "text-red-600",    bg: "bg-red-50 border-red-200" },
};

const NAV_ITEMS = [
  { id: "overview", label: "Overview", icon: "M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" },
  { id: "courses",  label: "Courses",  icon: "M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.746 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" },
  { id: "applications", label: "My Applications", icon: "M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" },
];

export default function Dashboard() {
  const [profile, setProfile] = useState(null);
  const [education, setEducation] = useState(null);
  const [applications, setApplications] = useState([]);
  const [courses, setCourses] = useState([]);
  const [activeTab, setActiveTab] = useState("overview");
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [chatLoading, setChatLoading] = useState(false);
  const [applyingId, setApplyingId] = useState(null);
  const [chatOpen, setChatOpen] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const bottomRef = useRef(null);

  const loadAll = async () => {
    try {
      const p = await apiFetch("/profile/");
      setProfile(p.student);
      setEducation(p.education);
    } catch {}
    try { setApplications(await apiFetch("/application/")); } catch {}
    try { setCourses(await apiFetch("/courses/")); } catch {}
  };

  useEffect(() => { loadAll(); }, []);
  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages]);

  const patchProfile = async (field, value) => {
    try {
      await apiFetch("/profile/", { method: "PATCH", body: JSON.stringify({ [field]: value }) });
      setProfile((p) => ({ ...p, [field]: value }));
    } catch (e) { alert(e.message); }
  };

  const applyToCourse = async (courseId) => {
    setApplyingId(courseId);
    try {
      await apiFetch("/application/", { method: "POST", body: JSON.stringify({ course_id: courseId }) });
      await loadAll();
    } catch (e) { alert(e.message); }
    finally { setApplyingId(null); }
  };

  const sendChat = async () => {
    const text = input.trim();
    if (!text || chatLoading) return;
    setMessages((p) => [...p, { role: "user", content: text }]);
    setInput("");
    setChatLoading(true);
    try {
      const history = messages.map((m) => ({ role: m.role, content: m.content }));
      const data = await apiFetch("/chatbot/chat", {
        method: "POST",
        body: JSON.stringify({ message: text, chat_history: history }),
      });
      setMessages((p) => [...p, { role: "assistant", content: data.response }]);
      loadAll();
    } catch (e) {
      setMessages((p) => [...p, { role: "assistant", content: `Error: ${e.message}` }]);
    } finally { setChatLoading(false); }
  };

  const enrolledIds = new Set(applications.map((a) => a.course_id));
  const unapplied = courses.filter((c) => !enrolledIds.has(c.id));

  const initials = profile?.full_name
    ? profile.full_name.split(" ").map((w) => w[0]).join("").toUpperCase().slice(0, 2)
    : "?";

  return (
    <div className="min-h-screen bg-stone-100 flex" style={{ fontFamily: "'Syne', 'DM Sans', sans-serif" }}>

      {/* ── Sidebar ── */}
      <aside className={`
        fixed inset-y-0 left-0 z-40 w-56 bg-stone-900 text-stone-100 flex flex-col
        transform transition-transform duration-300
        ${sidebarOpen ? "translate-x-0" : "-translate-x-full"}
        lg:relative lg:translate-x-0 lg:flex
      `}>
        {/* Logo */}
        <div className="px-5 py-5 border-b border-stone-800">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 bg-amber-400 rounded-lg flex items-center justify-center flex-shrink-0">
              <svg className="w-4 h-4 text-stone-900" fill="currentColor" viewBox="0 0 20 20">
                <path d="M10.394 2.08a1 1 0 00-.788 0l-7 3a1 1 0 000 1.84L5.25 8.051a.999.999 0 01.356-.257l4-1.714a1 1 0 11.788 1.838L7.667 9.088l1.94.831a1 1 0 00.787 0l7-3a1 1 0 000-1.838l-7-3zM3.31 9.397L5 10.12v4.102a8.969 8.969 0 00-1.05-.174 1 1 0 01-.89-.89 11.115 11.115 0 01.25-3.762zM9.3 16.573A9.026 9.026 0 007 14.935v-3.957l1.818.78a3 3 0 002.364 0l5.508-2.361a11.026 11.026 0 01.25 3.762 1 1 0 01-.89.89 8.968 8.968 0 00-5.35 2.524 1 1 0 01-1.4 0zM6 18a1 1 0 001-1v-2.065a8.935 8.935 0 00-2-.712V17a1 1 0 001 1z"/>
              </svg>
            </div>
            <span className="font-bold text-sm tracking-wide">LMS Portal</span>
          </div>
        </div>

        {/* Avatar */}
        <div className="px-5 py-5 border-b border-stone-800">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-amber-400 flex items-center justify-center font-bold text-sm text-stone-900 flex-shrink-0">
              {initials}
            </div>
            <div className="min-w-0">
              <p className="text-xs font-semibold text-stone-100 truncate">{profile?.full_name || "Student"}</p>
              <p className="text-xs text-stone-500 truncate">{profile?.email || ""}</p>
            </div>
          </div>
        </div>

        {/* Nav */}
        <nav className="flex-1 px-3 py-4 space-y-1">
          {NAV_ITEMS.map((item) => (
            <button
              key={item.id}
              onClick={() => { setActiveTab(item.id); setSidebarOpen(false); }}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-medium transition-all duration-150 ${
                activeTab === item.id
                  ? "bg-amber-400 text-stone-900"
                  : "text-stone-400 hover:text-stone-100 hover:bg-stone-800"
              }`}
            >
              <svg className="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" strokeWidth={1.8} viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" d={item.icon} />
              </svg>
              {item.label}
            </button>
          ))}
        </nav>

        {/* Logout */}
        <div className="px-3 py-4 border-t border-stone-800">
          <button
            onClick={() => { localStorage.removeItem("token"); window.location.href = "/"; }}
            className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs text-stone-500 hover:text-red-400 hover:bg-stone-800 transition-all"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth={1.8} viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
            Logout
          </button>
        </div>
      </aside>

      {/* Sidebar overlay for mobile */}
      {sidebarOpen && (
        <div className="fixed inset-0 z-30 bg-black/50 lg:hidden" onClick={() => setSidebarOpen(false)} />
      )}

      {/* ── Main ── */}
      <div className="flex-1 flex flex-col min-w-0">

        {/* Topbar */}
        <header className="bg-white border-b border-stone-200 px-5 py-3 flex items-center justify-between sticky top-0 z-20">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setSidebarOpen(true)}
              className="lg:hidden p-1.5 rounded-lg hover:bg-stone-100 transition-colors"
            >
              <svg className="w-5 h-5 text-stone-600" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
            <div>
              <p className="text-xs text-stone-400 leading-none">Welcome back,</p>
              <p className="text-sm font-bold text-stone-800 leading-tight">{profile?.full_name || "Student"}</p>
            </div>
          </div>
          <button
            onClick={() => setChatOpen(true)}
            className="flex items-center gap-2 bg-stone-900 text-white text-xs px-3.5 py-2 rounded-xl hover:bg-stone-700 transition-colors"
          >
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
            Ask AI
          </button>
        </header>

        {/* Content */}
        <main className="flex-1 overflow-y-auto p-5">

          {/* ── OVERVIEW TAB ── */}
          {activeTab === "overview" && (
            <div className="max-w-3xl mx-auto space-y-5">

              {/* Stats row */}
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                {[
                  { label: "Enrolled", value: applications.length, color: "text-amber-500" },
                  { label: "Accepted", value: applications.filter(a => a.status === "accepted").length, color: "text-emerald-500" },
                  { label: "Pending", value: applications.filter(a => a.status === "submitted" || a.status === "under_review").length, color: "text-sky-500" },
                ].map((s) => (
                  <div key={s.label} className="bg-white rounded-2xl border border-stone-200 p-4">
                    <p className={`text-2xl font-black ${s.color}`}>{s.value}</p>
                    <p className="text-xs text-stone-500 font-medium mt-0.5">{s.label}</p>
                  </div>
                ))}
              </div>

              {/* Profile card */}
              <div className="bg-white rounded-2xl border border-stone-200 p-5">
                <p className="text-xs font-bold text-stone-400 uppercase tracking-widest mb-4">Profile</p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {[
                    { icon: "M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z", label: "Full Name", field: "full_name", value: profile?.full_name, editable: true },
                    { icon: "M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z", label: "Email", field: "email", value: profile?.email, editable: false },
                    { icon: "M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z", label: "Phone", field: "phone", value: profile?.phone, editable: true },
                    { icon: "M8 7V3m8 4V3M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z", label: "Date of Birth", field: "date_of_birth", value: profile?.date_of_birth, editable: true },
                    { icon: "M17.657 16.657L13.414 20.9a2 2 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0zM15 11a3 3 0 11-6 0 3 3 0 016 0z", label: "City", field: "city", value: profile?.city, editable: true },
                  ].map((f) => (
                    <div key={f.field} className="flex items-center gap-3 bg-stone-50 border border-stone-200 rounded-xl px-3.5 py-2.5">
                      <svg className="w-4 h-4 text-stone-400 flex-shrink-0" fill="none" stroke="currentColor" strokeWidth={1.8} viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" d={f.icon} />
                      </svg>
                      <div className="min-w-0">
                        <p className="text-xs text-stone-400">{f.label}</p>
                        {f.editable ? (
                          <EditableField
                            value={f.value}
                            onSave={(v) => patchProfile(f.field, v)}
                            placeholder="Click to set"
                            className="text-sm font-medium text-stone-800"
                          />
                        ) : (
                          <p className="text-sm font-medium text-stone-800 truncate">{f.value || "—"}</p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Education card */}
              <div className="bg-white rounded-2xl border border-stone-200 p-5">
                <p className="text-xs font-bold text-stone-400 uppercase tracking-widest mb-4">Education</p>
                {education ? (
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {[
                      { label: "10th Board", value: education.tenth_board, pct: education.tenth_percentage },
                      { label: "12th Board", value: education.twelfth_board, pct: education.twelfth_percentage },
                    ].map((e) => (
                      <div key={e.label} className="bg-stone-50 border border-stone-200 rounded-xl p-3.5">
                        <p className="text-xs text-stone-400 mb-1">{e.label}</p>
                        <p className="text-sm font-bold text-stone-800">{e.value || "—"}</p>
                        <div className="mt-2 flex items-center gap-2">
                          <div className="flex-1 bg-stone-200 rounded-full h-1.5">
                            <div
                              className="bg-amber-400 h-1.5 rounded-full transition-all duration-500"
                              style={{ width: `${Math.min(e.pct, 100)}%` }}
                            />
                          </div>
                          <span className="text-xs font-bold text-stone-700">{e.pct}%</span>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-6">
                    <p className="text-sm text-stone-400 italic">No education details yet.</p>
                    <p className="text-xs text-stone-400 mt-1">Ask the AI assistant to add them.</p>
                  </div>
                )}
              </div>

              {/* Recent applications */}
              <div className="bg-white rounded-2xl border border-stone-200 p-5">
                <div className="flex items-center justify-between mb-4">
                  <p className="text-xs font-bold text-stone-400 uppercase tracking-widest">Recent Applications</p>
                  <button onClick={() => setActiveTab("applications")} className="text-xs text-amber-500 hover:text-amber-600 font-medium">View all →</button>
                </div>
                {applications.length === 0 ? (
                  <p className="text-sm text-stone-400 italic text-center py-4">No applications yet.</p>
                ) : (
                  <div className="space-y-2">
                    {applications.slice(0, 3).map((a) => {
                      const s = STATUS_CONFIG[a.status] || STATUS_CONFIG.submitted;
                      return (
                        <div key={a.id} className="flex items-center justify-between bg-stone-50 border border-stone-200 rounded-xl px-3.5 py-2.5">
                          <div>
                            <p className="text-sm font-semibold text-stone-800">{a.title}</p>
                            <p className="text-xs text-stone-400">{a.duration_months} months · ₹{a.fee?.toLocaleString()}</p>
                          </div>
                          <span className={`flex items-center gap-1.5 text-xs font-medium px-2.5 py-1 rounded-full border ${s.bg} ${s.text}`}>
                            <span className={`w-1.5 h-1.5 rounded-full ${s.dot}`} />
                            {s.label}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* ── COURSES TAB ── */}
          {activeTab === "courses" && (
            <div className="max-w-3xl mx-auto space-y-5">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-lg font-black text-stone-900">All Courses</h2>
                  <p className="text-xs text-stone-400">{courses.length} courses available</p>
                </div>
              </div>

              {courses.length === 0 ? (
                <div className="bg-white rounded-2xl border border-stone-200 p-10 text-center">
                  <p className="text-stone-400 text-sm">No courses available yet.</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  {courses.map((c) => {
                    const applied = enrolledIds.has(c.id);
                    const app = applications.find((a) => a.course_id === c.id);
                    const s = app ? (STATUS_CONFIG[app.status] || STATUS_CONFIG.submitted) : null;
                    return (
                      <div key={c.id} className="bg-white rounded-2xl border border-stone-200 p-5 flex flex-col gap-3 hover:border-amber-300 hover:shadow-sm transition-all duration-200">
                        <div className="flex items-start justify-between gap-2">
                          <div className="w-10 h-10 bg-amber-50 border border-amber-200 rounded-xl flex items-center justify-center flex-shrink-0">
                            <svg className="w-5 h-5 text-amber-500" fill="none" stroke="currentColor" strokeWidth={1.8} viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.746 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                            </svg>
                          </div>
                          {applied && s && (
                            <span className={`flex items-center gap-1.5 text-xs font-medium px-2.5 py-1 rounded-full border ${s.bg} ${s.text}`}>
                              <span className={`w-1.5 h-1.5 rounded-full ${s.dot}`} />
                              {s.label}
                            </span>
                          )}
                        </div>
                        <div>
                          <p className="text-sm font-bold text-stone-900">{c.title}</p>
                          <div className="flex items-center gap-3 mt-1.5">
                            <span className="flex items-center gap-1 text-xs text-stone-500">
                              <svg className="w-3 h-3" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                              </svg>
                              {c.duration_months} months
                            </span>
                            <span className="flex items-center gap-1 text-xs text-stone-500">
                              <svg className="w-3 h-3" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                              </svg>
                              ₹{c.fee?.toLocaleString()}
                            </span>
                          </div>
                        </div>
                        {!applied ? (
                          <button
                            onClick={() => applyToCourse(c.id)}
                            disabled={applyingId === c.id}
                            className="mt-auto w-full bg-stone-900 text-white text-xs font-semibold py-2 rounded-xl hover:bg-stone-700 transition-colors disabled:opacity-40"
                          >
                            {applyingId === c.id ? "Applying…" : "Apply Now"}
                          </button>
                        ) : (
                          <div className="mt-auto w-full bg-stone-100 text-stone-400 text-xs font-semibold py-2 rounded-xl text-center">
                            Applied
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          )}

          {/* ── APPLICATIONS TAB ── */}
          {activeTab === "applications" && (
            <div className="max-w-3xl mx-auto space-y-5">
              <div>
                <h2 className="text-lg font-black text-stone-900">My Applications</h2>
                <p className="text-xs text-stone-400">{applications.length} total applications</p>
              </div>

              {applications.length === 0 ? (
                <div className="bg-white rounded-2xl border border-stone-200 p-10 text-center">
                  <p className="text-stone-400 text-sm">No applications yet.</p>
                  <button
                    onClick={() => setActiveTab("courses")}
                    className="mt-3 text-xs text-amber-500 hover:text-amber-600 font-medium"
                  >
                    Browse courses →
                  </button>
                </div>
              ) : (
                <div className="space-y-3">
                  {applications.map((a) => {
                    const s = STATUS_CONFIG[a.status] || STATUS_CONFIG.submitted;
                    return (
                      <div key={a.id} className={`bg-white rounded-2xl border p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4 ${s.bg}`}>
                        <div className="flex items-center gap-4">
                          <div className={`w-10 h-10 rounded-xl border flex items-center justify-center flex-shrink-0 ${s.bg}`}>
                            <span className={`w-3 h-3 rounded-full ${s.dot}`} />
                          </div>
                          <div>
                            <p className="text-sm font-bold text-stone-900">{a.title}</p>
                            <p className="text-xs text-stone-500">{a.duration_months} months · ₹{a.fee?.toLocaleString()} · App #{a.id}</p>
                            {a.applied_at && (
                              <p className="text-xs text-stone-400 mt-0.5">Applied: {new Date(a.applied_at).toLocaleDateString()}</p>
                            )}
                          </div>
                        </div>
                        <span className={`self-start sm:self-auto flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-full border ${s.bg} ${s.text}`}>
                          <span className={`w-1.5 h-1.5 rounded-full ${s.dot}`} />
                          {s.label}
                        </span>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          )}
        </main>
      </div>

      {/* ── Chat Drawer ── */}
      {chatOpen && (
        <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center sm:justify-end p-4 sm:pr-6">
          <div className="absolute inset-0 bg-black/30" onClick={() => setChatOpen(false)} />
          <div className="relative w-full sm:w-80 h-[70vh] sm:h-[560px] bg-white rounded-2xl border border-stone-200 shadow-2xl flex flex-col overflow-hidden">

            {/* Chat header */}
            <div className="flex items-center justify-between px-4 py-3 border-b border-stone-100 bg-stone-900">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse" />
                <span className="text-xs font-semibold text-white">AI Assistant</span>
              </div>
              <button onClick={() => setChatOpen(false)} className="text-stone-400 hover:text-white transition-colors">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-3">
              {messages.length === 0 && (
                <div className="h-full flex flex-col items-center justify-center gap-3 pb-4">
                  <div className="w-10 h-10 bg-amber-50 border border-amber-200 rounded-2xl flex items-center justify-center">
                    <svg className="w-5 h-5 text-amber-500" fill="none" stroke="currentColor" strokeWidth={1.8} viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                    </svg>
                  </div>
                  <p className="text-xs text-stone-400 text-center leading-relaxed px-4">
                    Ask me anything about your profile, education, or courses.
                  </p>
                  <div className="space-y-1.5 w-full px-2">
                    {["Show my profile", "What courses am I enrolled in?", "Update my city"].map((s) => (
                      <button
                        key={s}
                        onClick={() => setInput(s)}
                        className="w-full text-left text-xs text-stone-500 border border-stone-200 rounded-xl px-3 py-2 hover:bg-stone-50 hover:text-stone-700 hover:border-stone-300 transition-all"
                      >
                        {s}
                      </button>
                    ))}
                  </div>
                </div>
              )}
              {messages.map((m, i) => (
                <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
                  <div className={`max-w-[85%] text-xs px-3.5 py-2.5 rounded-2xl leading-relaxed whitespace-pre-wrap ${
                    m.role === "user"
                      ? "bg-stone-900 text-white rounded-br-sm"
                      : "bg-stone-100 text-stone-700 border border-stone-200 rounded-bl-sm"
                  }`}>
                    {m.content}
                  </div>
                </div>
              ))}
              {chatLoading && (
                <div className="flex justify-start">
                  <div className="bg-stone-100 border border-stone-200 text-stone-400 text-xs px-3.5 py-2.5 rounded-2xl rounded-bl-sm flex items-center gap-1.5">
                    <span className="w-1.5 h-1.5 bg-stone-400 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                    <span className="w-1.5 h-1.5 bg-stone-400 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                    <span className="w-1.5 h-1.5 bg-stone-400 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                  </div>
                </div>
              )}
              <div ref={bottomRef} />
            </div>

            {/* Input */}
            <div className="border-t border-stone-100 px-3 py-2.5 flex items-center gap-2">
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && sendChat()}
                placeholder="Type a message…"
                className="flex-1 text-xs bg-transparent outline-none text-stone-800 placeholder-stone-400"
              />
              <button
                onClick={sendChat}
                disabled={chatLoading || !input.trim()}
                className="w-7 h-7 bg-stone-900 rounded-full flex items-center justify-center disabled:opacity-30 hover:bg-amber-500 transition-colors flex-shrink-0"
              >
                <svg className="w-3 h-3 text-white translate-x-px" fill="none" stroke="currentColor" strokeWidth={2.5} viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}