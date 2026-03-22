import { useState, useEffect, useRef } from "react";

// ─── Theme ───────────────────────────────────────────────────────────────────
const THEMES = {
  dark: {
    bg: "#0a0a0f",
    surface: "#111118",
    surfaceAlt: "#16161f",
    border: "#1e1e2e",
    borderLight: "#2a2a3e",
    text: "#e8e8f0",
    textMuted: "#6b6b8a",
    textDim: "#3a3a5c",
    accent: "#7c6af7",
    accentHover: "#9580ff",
    accentSoft: "rgba(124,106,247,0.12)",
    accentSofter: "rgba(124,106,247,0.06)",
    green: "#34d399",
    greenSoft: "rgba(52,211,153,0.1)",
    red: "#f87171",
    redSoft: "rgba(248,113,113,0.1)",
    amber: "#fbbf24",
    amberSoft: "rgba(251,191,36,0.1)",
    blue: "#60a5fa",
    blueSoft: "rgba(96,165,250,0.1)",
    shadow: "0 0 0 1px rgba(124,106,247,0.15), 0 8px 32px rgba(0,0,0,0.4)",
  },
  light: {
    bg: "#f4f3ff",
    surface: "#ffffff",
    surfaceAlt: "#faf9ff",
    border: "#e4e2f5",
    borderLight: "#ece9ff",
    text: "#1a1830",
    textMuted: "#7269a4",
    textDim: "#b8b2d8",
    accent: "#6c5ce7",
    accentHover: "#5a4bd1",
    accentSoft: "rgba(108,92,231,0.1)",
    accentSofter: "rgba(108,92,231,0.05)",
    green: "#10b981",
    greenSoft: "rgba(16,185,129,0.08)",
    red: "#ef4444",
    redSoft: "rgba(239,68,68,0.08)",
    amber: "#f59e0b",
    amberSoft: "rgba(245,158,11,0.08)",
    blue: "#3b82f6",
    blueSoft: "rgba(59,130,246,0.08)",
    shadow: "0 0 0 1px rgba(108,92,231,0.12), 0 8px 32px rgba(108,92,231,0.08)",
  },
};


const API = "https://ai-interviewer-simulator.onrender.com";


// ─── Helpers ─────────────────────────────────────────────────────────────────
const clamp = (v, min, max) => Math.min(Math.max(v, min), max);
const scoreColor = (score, t) => {
  if (score >= 80) return t.green;
  if (score >= 60) return t.amber;
  return t.red;
};
const difficultyColor = (d, t) => {
  if (d === "easy") return t.green;
  if (d === "medium") return t.amber;
  return t.red;
};

// ─── Spinner ─────────────────────────────────────────────────────────────────
function Spinner({ t }) {
  return (
    <span style={{
      display: "inline-block", width: 16, height: 16,
      border: `2px solid ${t.accentSoft}`,
      borderTop: `2px solid ${t.accent}`,
      borderRadius: "50%",
      animation: "spin 0.7s linear infinite",
    }} />
  );
}

// ─── Badge ────────────────────────────────────────────────────────────────────
function Badge({ children, color, bg, t }) {
  return (
    <span style={{
      display: "inline-flex", alignItems: "center",
      padding: "2px 10px", borderRadius: 999,
      fontSize: 11, fontWeight: 600, letterSpacing: "0.04em",
      textTransform: "uppercase",
      color: color || t.accent,
      background: bg || t.accentSoft,
      border: `1px solid ${color || t.accent}22`,
    }}>{children}</span>
  );
}

// ─── Card ─────────────────────────────────────────────────────────────────────
function Card({ children, t, style = {} }) {
  return (
    <div style={{
      background: t.surface,
      border: `1px solid ${t.border}`,
      borderRadius: 16,
      padding: 24,
      ...style,
    }}>{children}</div>
  );
}

// ─── Score Ring ───────────────────────────────────────────────────────────────
function ScoreRing({ score, t, size = 100 }) {
  const r = (size - 12) / 2;
  const circ = 2 * Math.PI * r;
  const offset = circ - (clamp(score, 0, 100) / 100) * circ;
  const color = scoreColor(score, t);
  return (
    <div style={{ position: "relative", width: size, height: size, flexShrink: 0 }}>
      <svg width={size} height={size} style={{ transform: "rotate(-90deg)" }}>
        <circle cx={size / 2} cy={size / 2} r={r}
          fill="none" stroke={t.border} strokeWidth={6} />
        <circle cx={size / 2} cy={size / 2} r={r}
          fill="none" stroke={color} strokeWidth={6}
          strokeDasharray={circ} strokeDashoffset={offset}
          strokeLinecap="round"
          style={{ transition: "stroke-dashoffset 1s cubic-bezier(.4,0,.2,1)" }} />
      </svg>
      <div style={{
        position: "absolute", inset: 0,
        display: "flex", flexDirection: "column",
        alignItems: "center", justifyContent: "center",
      }}>
        <span style={{ fontSize: size * 0.24, fontWeight: 700, color, fontFamily: "'DM Mono', monospace", lineHeight: 1 }}>{score}</span>
        <span style={{ fontSize: size * 0.1, color: t.textMuted, fontWeight: 500, marginTop: 2 }}>/ 100</span>
      </div>
    </div>
  );
}

// ─── Metric Row ───────────────────────────────────────────────────────────────
function MetricRow({ label, value, color, t }) {
  return (
    <div style={{
      display: "flex", justifyContent: "space-between", alignItems: "center",
      padding: "10px 0",
      borderBottom: `1px solid ${t.border}`,
    }}>
      <span style={{ fontSize: 13, color: t.textMuted, fontWeight: 500 }}>{label}</span>
      <span style={{ fontSize: 13, fontWeight: 700, color: color || t.text, fontFamily: "'DM Mono', monospace" }}>{value}</span>
    </div>
  );
}

// ─── Toggle ───────────────────────────────────────────────────────────────────
function ThemeToggle({ isDark, onToggle, t }) {
  return (
    <button onClick={onToggle} style={{
      display: "flex", alignItems: "center", gap: 8,
      background: t.surfaceAlt, border: `1px solid ${t.border}`,
      borderRadius: 999, padding: "6px 14px",
      cursor: "pointer", color: t.textMuted,
      fontSize: 12, fontWeight: 600, letterSpacing: "0.03em",
      transition: "all 0.2s",
    }}>
      <span style={{ fontSize: 14 }}>{isDark ? "☀️" : "🌙"}</span>
      {isDark ? "Light" : "Dark"}
    </button>
  );
}

// ─── Tab Bar ─────────────────────────────────────────────────────────────────
function TabBar({ tabs, active, onChange, t }) {
  return (
    <div style={{
      display: "flex", gap: 4,
      background: t.surfaceAlt,
      border: `1px solid ${t.border}`,
      borderRadius: 12, padding: 4,
    }}>
      {tabs.map(tab => (
        <button key={tab.id} onClick={() => onChange(tab.id)} style={{
          flex: 1, padding: "8px 20px",
          borderRadius: 8, border: "none",
          cursor: "pointer", fontSize: 13, fontWeight: 600,
          letterSpacing: "0.02em",
          background: active === tab.id ? t.accent : "transparent",
          color: active === tab.id ? "#fff" : t.textMuted,
          transition: "all 0.2s",
        }}>{tab.label}</button>
      ))}
    </div>
  );
}

// ─── Code Editor ─────────────────────────────────────────────────────────────
function CodeEditor({ value, onChange, t }) {
  return (
    <div style={{
      position: "relative",
      background: t.bg,
      border: `1px solid ${t.border}`,
      borderRadius: 12, overflow: "hidden",
    }}>
      <div style={{
        display: "flex", alignItems: "center", gap: 8,
        padding: "10px 16px",
        background: t.surfaceAlt,
        borderBottom: `1px solid ${t.border}`,
      }}>
        <div style={{ display: "flex", gap: 6 }}>
          {["#ff5f57", "#febc2e", "#28c840"].map((c, i) => (
            <div key={i} style={{ width: 10, height: 10, borderRadius: "50%", background: c }} />
          ))}
        </div>
        <span style={{ fontSize: 11, color: t.textMuted, fontFamily: "'DM Mono', monospace", marginLeft: 4 }}>solution.py</span>
      </div>
      <textarea
        value={value}
        onChange={e => onChange(e.target.value)}
        spellCheck={false}
        style={{
          width: "100%", minHeight: 280,
          background: "transparent",
          color: t.text,
          fontFamily: "'DM Mono', monospace",
          fontSize: 13, lineHeight: 1.7,
          border: "none", outline: "none",
          padding: "16px 20px",
          resize: "vertical",
          boxSizing: "border-box",
          caretColor: t.accent,
        }}
        placeholder="# Write your solution here..."
      />
    </div>
  );
}

// ─── Interview View ──────────────────────────────────────────────────────────
function InterviewView({ t }) {
  const [sessionId, setSessionId] = useState(null);
  const [question, setQuestion] = useState(null);
  const [difficulty, setDifficulty] = useState("medium");
  const [round, setRound] = useState(1);
  const [code, setCode] = useState("");
  const [result, setResult] = useState(null);
  const [hint, setHint] = useState(null);
  const [loading, setLoading] = useState(false);
  const [hintLoading, setHintLoading] = useState(false);
  const [starting, setStarting] = useState(false);
  const [phase, setPhase] = useState("idle"); // idle | interview | result
  const [topic, setTopic] = useState(null);
  const [subtopic, setSubtopic] = useState(null);


  async function startInterview() {
    setStarting(true);
    try {
      const res = await fetch(`${API}/start`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({}),
      });
      const data = await res.json();
      setSessionId(data.session_id);
      setQuestion(data.question);
      setTopic(data.topic || null);
      setSubtopic(data.subtopic || null);
      setDifficulty(data.difficulty || "medium");
      setRound(data.round || 1);
      setCode("");
      setResult(null);
      setHint(null);
      setPhase("interview");
    } catch (e) {
      alert("Could not connect to server. Make sure uvicorn is running.");
    }
    setStarting(false);
  }

  async function submitCode() {
    if (!code.trim()) return;
    setLoading(true);
    try {
      const res = await fetch(`${API}/submit`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId, code, language: "python" }),
      });
      const data = await res.json();
      setResult(data);
      setPhase("result");
    } catch (e) {
      alert("Submission failed.");
    }
    setLoading(false);
  }

  async function getHint() {
    setHintLoading(true);
    try {
      const res = await fetch(`${API}/hint`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId }),
      });
      const data = await res.json();
      setHint(data.hint);
    } catch (e) {
      alert("Could not get hint.");
    }
    setHintLoading(false);
  }

  async function nextQuestion() {
    if (!result?.next_question) return;
    setLoading(true);
    try {
      const res = await fetch(`${API}/next`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId }),
      });
      const data = await res.json();
      if (data.error) { alert(data.error); return; }

      setQuestion(data.question);
      setDifficulty(data.difficulty);
      setTopic(data.topic || null);
      setSubtopic(data.subtopic || null);
      setRound(data.round);
      setCode("");
      setResult(null);
      setHint(null);
      setPhase("interview");
    } catch (e) {
      alert("Failed to load next question.");
    }
    setLoading(false);
  }

  if (phase === "idle") return (
    <div style={{
      display: "flex", flexDirection: "column",
      alignItems: "center", justifyContent: "center",
      minHeight: "60vh", gap: 32, textAlign: "center",
    }}>
      <div>
        <div style={{
          width: 72, height: 72, borderRadius: 20,
          background: t.accentSoft,
          border: `1px solid ${t.accent}44`,
          display: "flex", alignItems: "center", justifyContent: "center",
          fontSize: 32, margin: "0 auto 24px",
        }}>⚡</div>
        <h2 style={{ fontSize: 28, fontWeight: 700, color: t.text, margin: "0 0 8px" }}>
          Ready to be assessed?
        </h2>
        <p style={{ color: t.textMuted, fontSize: 15, maxWidth: 400, margin: "0 auto" }}>
          An adaptive AI interviewer will evaluate your code, complexity, quality, and thinking in real time.
        </p>
      </div>
      <button onClick={startInterview} disabled={starting} style={{
        padding: "14px 40px", borderRadius: 12,
        background: t.accent, color: "#fff",
        border: "none", cursor: "pointer",
        fontSize: 15, fontWeight: 700,
        display: "flex", alignItems: "center", gap: 10,
        opacity: starting ? 0.7 : 1,
        transition: "all 0.2s",
        boxShadow: `0 4px 20px ${t.accent}44`,
      }}>
        {starting ? <Spinner t={t} /> : null}
        {starting ? "Starting..." : "Start Interview"}
      </button>
    </div>
  );

  if (phase === "interview") return (
    <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
      {/* Question header */}
      <Card t={t}>
        <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: 16 }}>
          <div style={{ flex: 1 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 12, flexWrap: "wrap" }}>
              <Badge color={difficultyColor(difficulty, t)} bg={`${difficultyColor(difficulty, t)}18`} t={t}>
                {difficulty}
              </Badge>
              <Badge t={t}>Round {round}</Badge>
              {topic && (
                <Badge color={t.blue} bg={t.blueSoft} t={t}>
                  {topic}
                </Badge>
              )}
              {subtopic && (
                <Badge color={t.textMuted} bg={t.surfaceAlt} t={t}>
                  {subtopic}
                </Badge>
              )}
            </div>
            <p style={{ fontSize: 16, color: t.text, fontWeight: 500, margin: 0, lineHeight: 1.6 }}>
              {question}
            </p>
          </div>
        </div>
      </Card>
      {sessionId && (
        <div style={{
          display: "flex", alignItems: "center", gap: 10,
          padding: "8px 14px",
          background: t.surfaceAlt,
          border: `1px solid ${t.border}`,
          borderRadius: 8, fontSize: 12,
        }}>
          <span style={{ color: t.textMuted }}>Session ID:</span>
          <code style={{ color: t.accent, fontFamily: "'DM Mono', monospace" }}>{sessionId}</code>
          <button onClick={() => navigator.clipboard.writeText(sessionId)} style={{
            background: t.accentSoft, border: "none",
            color: t.accent, borderRadius: 6,
            padding: "2px 10px", cursor: "pointer",
            fontSize: 11, fontWeight: 600,
          }}>Copy</button>
        </div>
      )}

      {/* Hint */}
      {hint && (
        <div style={{
          padding: "14px 18px", borderRadius: 12,
          background: t.amberSoft,
          border: `1px solid ${t.amber}33`,
          display: "flex", gap: 12, alignItems: "flex-start",
        }}>
          <span style={{ fontSize: 16 }}>💡</span>
          <p style={{ margin: 0, fontSize: 13, color: t.text, lineHeight: 1.6 }}>{hint}</p>
        </div>
      )}

      {/* Editor */}
      <CodeEditor value={code} onChange={setCode} t={t} />

      {/* Actions */}
      <div style={{ display: "flex", gap: 12 }}>
        <button onClick={getHint} disabled={hintLoading} style={{
          padding: "12px 24px", borderRadius: 10,
          background: t.amberSoft, color: t.amber,
          border: `1px solid ${t.amber}33`,
          cursor: "pointer", fontSize: 13, fontWeight: 600,
          display: "flex", alignItems: "center", gap: 8,
          opacity: hintLoading ? 0.7 : 1,
        }}>
          {hintLoading ? <Spinner t={{ ...t, accent: t.amber }} /> : "💡"}
          {hintLoading ? "Getting hint..." : "Request Hint"}
        </button>

        <button onClick={submitCode} disabled={loading || !code.trim()} style={{
          flex: 1, padding: "12px 24px", borderRadius: 10,
          background: t.accent, color: "#fff",
          border: "none", cursor: "pointer",
          fontSize: 13, fontWeight: 700,
          display: "flex", alignItems: "center", justifyContent: "center", gap: 8,
          opacity: (loading || !code.trim()) ? 0.6 : 1,
          boxShadow: code.trim() ? `0 4px 16px ${t.accent}44` : "none",
          transition: "all 0.2s",
        }}>
          {loading ? <Spinner t={t} /> : null}
          {loading ? "Evaluating..." : "Submit Solution →"}
        </button>
      </div>
    </div>
  );

  if (phase === "result" && result) return (
    <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
      {/* Score header */}
      <Card t={t}>
        <div style={{ display: "flex", alignItems: "center", gap: 24 }}>
          <ScoreRing score={result.score} t={t} size={110} />
          <div style={{ flex: 1 }}>
            <div style={{ display: "flex", gap: 8, marginBottom: 10, flexWrap: "wrap" }}>
              <Badge color={scoreColor(result.score, t)} bg={`${scoreColor(result.score, t)}18`} t={t}>
                {result.report?.performance?.performance_label || "Evaluated"}
              </Badge>
              <Badge color={t.blue} bg={t.blueSoft} t={t}>
                {result.report?.verdict?.hire_recommendation || "—"}
              </Badge>
              <Badge color={difficultyColor(difficulty, t)} bg={`${difficultyColor(difficulty, t)}18`} t={t}>
                {difficulty}
              </Badge>
            </div>
            <p style={{ margin: "0 0 8px", fontSize: 14, color: t.text, lineHeight: 1.6 }}>
              {result.feedback}
            </p>
            {result.followup && (
              <p style={{
                margin: 0, fontSize: 13, color: t.accent,
                fontStyle: "italic", lineHeight: 1.5,
                borderLeft: `2px solid ${t.accent}`,
                paddingLeft: 12,
              }}>
                💬 {result.followup}
              </p>
            )}
          </div>
        </div>
      </Card>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
        {/* Complexity */}
        <Card t={t} style={{ padding: 20 }}>
          <h4 style={{ margin: "0 0 14px", fontSize: 13, fontWeight: 700, color: t.textMuted, textTransform: "uppercase", letterSpacing: "0.06em" }}>
            Complexity
          </h4>
          <MetricRow label="Time" value={result.complexity?.time_complexity} color={t.accent} t={t} />
          <MetricRow label="Space" value={result.complexity?.space_complexity} color={t.blue} t={t} />
          <MetricRow label="Nested Loops" value={result.complexity?.nested_loops ?? "—"} t={t} />
          <MetricRow label="Recursion" value={result.complexity?.recursion ? "Yes" : "No"} t={t} />
          <p style={{ margin: "12px 0 0", fontSize: 12, color: t.textMuted, lineHeight: 1.5 }}>
            {result.complexity?.reasoning}
          </p>
        </Card>

        {/* Code Quality */}
        <Card t={t} style={{ padding: 20 }}>
          <h4 style={{ margin: "0 0 14px", fontSize: 13, fontWeight: 700, color: t.textMuted, textTransform: "uppercase", letterSpacing: "0.06em" }}>
            Code Quality
          </h4>
          <MetricRow label="Quality Score" value={`${result.quality?.quality_score}/100`}
            color={scoreColor(result.quality?.quality_score || 0, t)} t={t} />
          <MetricRow label="PEP 8 Violations" value={result.quality?.pep8_violations ?? 0} t={t} />
          <MetricRow label="Has Docstrings" value={result.quality?.has_docstrings ? "✓ Yes" : "✗ No"} t={t} />
          {result.quality?.issues?.length > 0 && (
            <div style={{ marginTop: 12 }}>
              {result.quality.issues.slice(0, 3).map((iss, i) => (
                <div key={i} style={{
                  fontSize: 11, color: t.amber,
                  padding: "3px 0", display: "flex", gap: 6,
                }}>
                  <span>⚠</span><span>{iss}</span>
                </div>
              ))}
            </div>
          )}
        </Card>
      </div>

      {/* Execution */}
      <Card t={t} style={{ padding: 20 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 12 }}>
          <h4 style={{ margin: 0, fontSize: 13, fontWeight: 700, color: t.textMuted, textTransform: "uppercase", letterSpacing: "0.06em" }}>
            Execution
          </h4>
          <Badge
            color={result.run?.success ? t.green : t.red}
            bg={result.run?.success ? t.greenSoft : t.redSoft}
            t={t}
          >
            {result.run?.success ? "Passed" : "Failed"}
          </Badge>
        </div>
        {result.run?.output && (
          <pre style={{
            margin: 0, padding: "12px 16px",
            background: t.bg, borderRadius: 8,
            fontSize: 12, fontFamily: "'DM Mono', monospace",
            color: t.green, border: `1px solid ${t.border}`,
            whiteSpace: "pre-wrap", wordBreak: "break-all",
          }}>{result.run.output}</pre>
        )}
        {result.run?.error && (
          <pre style={{
            margin: "8px 0 0", padding: "12px 16px",
            background: t.redSoft, borderRadius: 8,
            fontSize: 12, fontFamily: "'DM Mono', monospace",
            color: t.red, border: `1px solid ${t.red}22`,
            whiteSpace: "pre-wrap", wordBreak: "break-all",
          }}>{result.run.error}</pre>
        )}
      </Card>

      {/* Strengths & Improvements */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
        <Card t={t} style={{ padding: 20 }}>
          <h4 style={{ margin: "0 0 14px", fontSize: 13, fontWeight: 700, color: t.green, textTransform: "uppercase", letterSpacing: "0.06em" }}>
            ✓ Strengths
          </h4>
          {result.report?.verdict?.strengths?.map((s, i) => (
            <div key={i} style={{
              display: "flex", gap: 8, padding: "5px 0",
              fontSize: 13, color: t.text, alignItems: "flex-start",
            }}>
              <span style={{ color: t.green, flexShrink: 0 }}>→</span>
              <span>{s}</span>
            </div>
          ))}
        </Card>
        <Card t={t} style={{ padding: 20 }}>
          <h4 style={{ margin: "0 0 14px", fontSize: 13, fontWeight: 700, color: t.amber, textTransform: "uppercase", letterSpacing: "0.06em" }}>
            ↑ Improvements
          </h4>
          {result.report?.verdict?.improvements?.map((s, i) => (
            <div key={i} style={{
              display: "flex", gap: 8, padding: "5px 0",
              fontSize: 13, color: t.text, alignItems: "flex-start",
            }}>
              <span style={{ color: t.amber, flexShrink: 0 }}>→</span>
              <span>{s}</span>
            </div>
          ))}
        </Card>
      </div>

      {/* Next question */}
      {result.next_question && (
        <Card t={t} style={{ padding: 20, background: t.accentSofter, border: `1px solid ${t.accent}33` }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 16 }}>
            <div>
              <p style={{ margin: "0 0 4px", fontSize: 12, color: t.accent, fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.06em" }}>
                {result.next_question.message}
              </p>
              <p style={{ margin: 0, fontSize: 14, color: t.text }}>{result.next_question.question}</p>
            </div>
            <button onClick={nextQuestion} style={{
              padding: "10px 24px", borderRadius: 10,
              background: t.accent, color: "#fff",
              border: "none", cursor: "pointer",
              fontSize: 13, fontWeight: 700, flexShrink: 0,
              boxShadow: `0 4px 16px ${t.accent}44`,
            }}>
              Next →
            </button>
          </div>
        </Card>
      )}
    </div>
  );

  return null;
}

// ─── Dashboard View ──────────────────────────────────────────────────────────
function DashboardView({ t }) {
  const [sessionId, setSessionId] = useState("");
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function fetchReport() {
    if (!sessionId.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API}/report/${sessionId.trim()}`);
      const data = await res.json();
      if (data.error) { setError(data.error); setReport(null); }
      else setReport(data.report || data);
    } catch (e) {
      setError("Failed to fetch report.");
    }
    setLoading(false);
  }

  const r = report;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
      {/* Search */}
      <Card t={t} style={{ padding: 20 }}>
        <h3 style={{ margin: "0 0 16px", fontSize: 15, fontWeight: 700, color: t.text }}>
          Load Candidate Report
        </h3>
        <div style={{ display: "flex", gap: 12 }}>
          <input
            value={sessionId}
            onChange={e => setSessionId(e.target.value)}
            onKeyDown={e => e.key === "Enter" && fetchReport()}
            placeholder="Enter session ID..."
            style={{
              flex: 1, padding: "10px 16px",
              background: t.bg, border: `1px solid ${t.border}`,
              borderRadius: 10, color: t.text,
              fontSize: 13, fontFamily: "'DM Mono', monospace",
              outline: "none",
            }}
          />
          <button onClick={fetchReport} disabled={loading || !sessionId.trim()} style={{
            padding: "10px 24px", borderRadius: 10,
            background: t.accent, color: "#fff",
            border: "none", cursor: "pointer",
            fontSize: 13, fontWeight: 700,
            display: "flex", alignItems: "center", gap: 8,
            opacity: (loading || !sessionId.trim()) ? 0.6 : 1,
          }}>
            {loading ? <Spinner t={t} /> : null}
            {loading ? "Loading..." : "Load Report"}
          </button>
        </div>
        {error && <p style={{ margin: "12px 0 0", fontSize: 13, color: t.red }}>{error}</p>}
      </Card>

      {!r && !loading && (
        <div style={{ textAlign: "center", padding: "48px 0", color: t.textMuted }}>
          <div style={{ fontSize: 40, marginBottom: 12 }}>📋</div>
          <p style={{ margin: 0, fontSize: 14 }}>Enter a session ID to load a candidate report</p>
        </div>
      )}

      {r && (
        <>
          {/* Verdict banner */}
          <Card t={t} style={{
            background: t.accentSofter,
            border: `1px solid ${t.accent}33`,
            padding: 24,
          }}>
            <div style={{ display: "flex", alignItems: "center", gap: 24, flexWrap: "wrap" }}>
              <ScoreRing score={r.performance?.final_score || 0} t={t} size={100} />
              <div style={{ flex: 1, minWidth: 200 }}>
                <div style={{ display: "flex", gap: 8, marginBottom: 12, flexWrap: "wrap" }}>
                  <Badge color={t.blue} bg={t.blueSoft} t={t}>{r.verdict?.hire_recommendation}</Badge>
                  <Badge color={scoreColor(r.performance?.final_score || 0, t)} bg={`${scoreColor(r.performance?.final_score || 0, t)}18`} t={t}>
                    {r.performance?.performance_label}
                  </Badge>
                  <Badge color={difficultyColor(r.meta?.difficulty, t)} bg={`${difficultyColor(r.meta?.difficulty, t)}18`} t={t}>
                    {r.meta?.difficulty}
                  </Badge>
                </div>
                <p style={{ margin: "0 0 6px", fontSize: 14, color: t.text, lineHeight: 1.5 }}>
                  {r.verdict?.summary}
                </p>
                <p style={{ margin: 0, fontSize: 12, color: t.textMuted, fontFamily: "'DM Mono', monospace" }}>
                  Session: {r.meta?.session_id} · {new Date(r.meta?.generated_at).toLocaleString()}
                </p>
              </div>
            </div>
          </Card>

          {/* Metrics grid */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12 }}>
            {[
              { label: "Final Score", value: `${r.performance?.final_score}/100`, color: scoreColor(r.performance?.final_score || 0, t) },
              { label: "Adjusted Score", value: `${r.performance?.adjusted_score}/100`, color: t.accent },
              { label: "Hints Used", value: r.performance?.hints_used ?? 0, color: r.performance?.hints_used > 2 ? t.red : t.green },
              { label: "Rounds", value: r.meta?.rounds ?? 1, color: t.blue },
            ].map((m, i) => (
              <Card key={i} t={t} style={{ padding: 16, textAlign: "center" }}>
                <div style={{ fontSize: 24, fontWeight: 800, color: m.color, fontFamily: "'DM Mono', monospace", lineHeight: 1 }}>{m.value}</div>
                <div style={{ fontSize: 11, color: t.textMuted, marginTop: 6, fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.05em" }}>{m.label}</div>
              </Card>
            ))}
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
            {/* Complexity */}
            <Card t={t} style={{ padding: 20 }}>
              <h4 style={{ margin: "0 0 14px", fontSize: 13, fontWeight: 700, color: t.textMuted, textTransform: "uppercase", letterSpacing: "0.06em" }}>Complexity</h4>
              <MetricRow label="Time" value={r.code_analysis?.complexity?.time} color={t.accent} t={t} />
              <MetricRow label="Space" value={r.code_analysis?.complexity?.space} color={t.blue} t={t} />
              <p style={{ margin: "12px 0 0", fontSize: 12, color: t.textMuted, lineHeight: 1.5 }}>
                {r.code_analysis?.complexity?.reasoning}
              </p>
            </Card>

            {/* Quality */}
            <Card t={t} style={{ padding: 20 }}>
              <h4 style={{ margin: "0 0 14px", fontSize: 13, fontWeight: 700, color: t.textMuted, textTransform: "uppercase", letterSpacing: "0.06em" }}>Code Quality</h4>
              <MetricRow label="Quality Score" value={`${r.code_analysis?.quality?.score}/100`}
                color={scoreColor(r.code_analysis?.quality?.score || 0, t)} t={t} />
              <MetricRow label="PEP 8 Violations" value={r.code_analysis?.quality?.pep8_violations ?? 0} t={t} />
              <MetricRow label="Docstrings" value={r.code_analysis?.quality?.has_docstrings ? "✓ Yes" : "✗ No"} t={t} />
            </Card>
          </div>

          {/* Strengths & Improvements */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
            <Card t={t} style={{ padding: 20 }}>
              <h4 style={{ margin: "0 0 14px", fontSize: 13, fontWeight: 700, color: t.green, textTransform: "uppercase", letterSpacing: "0.06em" }}>✓ Strengths</h4>
              {r.verdict?.strengths?.map((s, i) => (
                <div key={i} style={{ display: "flex", gap: 8, padding: "5px 0", fontSize: 13, color: t.text }}>
                  <span style={{ color: t.green }}>→</span><span>{s}</span>
                </div>
              ))}
            </Card>
            <Card t={t} style={{ padding: 20 }}>
              <h4 style={{ margin: "0 0 14px", fontSize: 13, fontWeight: 700, color: t.amber, textTransform: "uppercase", letterSpacing: "0.06em" }}>↑ Improvements</h4>
              {r.verdict?.improvements?.map((s, i) => (
                <div key={i} style={{ display: "flex", gap: 8, padding: "5px 0", fontSize: 13, color: t.text }}>
                  <span style={{ color: t.amber }}>→</span><span>{s}</span>
                </div>
              ))}
            </Card>
          </div>

          {/* Interviewer Notes */}
          <Card t={t} style={{ padding: 20 }}>
            <h4 style={{ margin: "0 0 14px", fontSize: 13, fontWeight: 700, color: t.textMuted, textTransform: "uppercase", letterSpacing: "0.06em" }}>Interviewer Notes</h4>
            <p style={{ margin: "0 0 12px", fontSize: 14, color: t.text, lineHeight: 1.6 }}>
              {r.interviewer_notes?.feedback}
            </p>
            {r.interviewer_notes?.followup_question && (
              <p style={{
                margin: 0, fontSize: 13, color: t.accent,
                fontStyle: "italic", lineHeight: 1.5,
                borderLeft: `2px solid ${t.accent}`,
                paddingLeft: 12,
              }}>
                💬 {r.interviewer_notes.followup_question}
              </p>
            )}
          </Card>

          {/* Code submitted */}
          <Card t={t} style={{ padding: 20 }}>
            <h4 style={{ margin: "0 0 14px", fontSize: 13, fontWeight: 700, color: t.textMuted, textTransform: "uppercase", letterSpacing: "0.06em" }}>Code Submitted</h4>
            <pre style={{
              margin: 0, padding: "16px",
              background: t.bg, borderRadius: 10,
              fontSize: 12, fontFamily: "'DM Mono', monospace",
              color: t.text, border: `1px solid ${t.border}`,
              whiteSpace: "pre-wrap", overflowX: "auto",
            }}>{r.problem?.code_submitted}</pre>
          </Card>
        </>
      )}
    </div>
  );
}

// ─── App Root ─────────────────────────────────────────────────────────────────
export default function App() {
  const [isDark, setIsDark] = useState(true);
  const [tab, setTab] = useState("interview");
  const t = THEMES[isDark ? "dark" : "light"];

  return (
    <div style={{
      minHeight: "100vh",
      background: t.bg,
      color: t.text,
      fontFamily: "'DM Sans', 'Segoe UI', sans-serif",
      transition: "background 0.3s, color 0.3s",
    }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=DM+Mono:wght@400;500&display=swap');
        * { box-sizing: border-box; }
        @keyframes spin { to { transform: rotate(360deg); } }
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: ${t.border}; border-radius: 3px; }
        button:hover { opacity: 0.88; }
      `}</style>

      {/* Header */}
      <div style={{
        position: "sticky", top: 0, zIndex: 100,
        background: `${t.surface}ee`,
        backdropFilter: "blur(16px)",
        borderBottom: `1px solid ${t.border}`,
        padding: "0 32px",
        display: "flex", alignItems: "center", justifyContent: "space-between",
        height: 60,
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div style={{
            width: 30, height: 30, borderRadius: 8,
            background: t.accent,
            display: "flex", alignItems: "center", justifyContent: "center",
            fontSize: 15,
          }}>⚡</div>
          <span style={{ fontSize: 15, fontWeight: 800, color: t.text, letterSpacing: "-0.02em" }}>
            ProctorAI
          </span>
          <span style={{
            fontSize: 10, fontWeight: 600, color: t.accent,
            background: t.accentSoft, padding: "2px 8px",
            borderRadius: 999, letterSpacing: "0.05em", textTransform: "uppercase",
          }}>Beta</span>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
          <TabBar
            tabs={[
              { id: "interview", label: "Interview" },
              { id: "dashboard", label: "Dashboard" },
            ]}
            active={tab}
            onChange={setTab}
            t={t}
          />
          <ThemeToggle isDark={isDark} onToggle={() => setIsDark(d => !d)} t={t} />
        </div>
      </div>

      {/* Main */}
      <div style={{ maxWidth: 860, margin: "0 auto", padding: "32px 24px 80px" }}>
        {tab === "interview" ? <InterviewView t={t} /> : <DashboardView t={t} />}
      </div>
    </div>
  );
}