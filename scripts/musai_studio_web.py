#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from musai.creative import CreativeMaterials, MODEL_REGISTRY, PROJECTS_ROOT, create_project, list_projects
from musai.soulx_verse import SoulXVerseRequest, generate_soulx_verse
from musai.studio import (
    artifact_payload,
    create_session,
    get_artifact,
    list_artifacts,
    list_jobs,
    list_sessions,
    load_job,
    load_messages,
    load_settings,
    register_artifact,
    save_settings,
    select_artifact,
    send_chat_message,
    setup_status,
)


PAGE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Musai Studio</title>
  <style>
    :root {
      --ink: #17202a;
      --muted: #637083;
      --line: #d9e2ec;
      --soft: #f6f8fb;
      --panel: #ffffff;
      --teal: #0f766e;
      --teal-dark: #115e59;
      --amber: #b45309;
      --rose: #be123c;
      --slate: #243041;
    }
    * { box-sizing: border-box; }
    body { margin: 0; font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: var(--ink); background: var(--soft); }
    .app { min-height: 100vh; display: grid; grid-template-columns: 300px minmax(420px, 1fr) 360px; }
    aside, .right { background: var(--panel); border-right: 1px solid var(--line); overflow: auto; }
    .right { border-right: 0; border-left: 1px solid var(--line); }
    .main { display: grid; grid-template-rows: auto 1fr auto; min-width: 0; }
    header { padding: 18px 22px; background: var(--slate); color: white; }
    h1 { margin: 0; font-size: 24px; letter-spacing: 0; }
    h2 { margin: 0 0 12px; font-size: 16px; }
    h3 { margin: 18px 0 8px; font-size: 14px; color: var(--muted); text-transform: uppercase; letter-spacing: 0; }
    section { padding: 16px; border-bottom: 1px solid var(--line); }
    .muted { color: var(--muted); }
    .small { font-size: 12px; }
    button { border: 0; border-radius: 6px; background: var(--teal); color: white; padding: 9px 12px; font-weight: 700; cursor: pointer; }
    button.secondary { background: #e7edf3; color: var(--ink); }
    button.worker { background: var(--amber); }
    button.danger { background: var(--rose); }
    button:disabled { opacity: 0.55; cursor: wait; }
    input, textarea, select { width: 100%; border: 1px solid #c9d3df; border-radius: 6px; padding: 8px; font: inherit; background: white; }
    textarea { min-height: 76px; resize: vertical; }
    label { display: block; font-size: 12px; font-weight: 700; color: #344052; margin: 10px 0 4px; }
    code { background: #eef2f6; border-radius: 4px; padding: 2px 5px; }
    pre { white-space: pre-wrap; overflow: auto; margin: 0; }
    .row { display: flex; gap: 8px; align-items: center; }
    .row > * { min-width: 0; }
    .stack { display: grid; gap: 8px; }
    .list { display: grid; gap: 8px; }
    .item { border: 1px solid var(--line); border-radius: 8px; padding: 10px; background: white; cursor: pointer; }
    .item.active { border-color: var(--teal); box-shadow: 0 0 0 2px rgba(15,118,110,0.12); }
    .item-title { font-weight: 750; overflow-wrap: anywhere; }
    .chat { overflow: auto; padding: 18px; display: grid; align-content: start; gap: 12px; }
    .bubble { max-width: 880px; border: 1px solid var(--line); border-radius: 8px; padding: 12px; background: white; }
    .bubble.user { margin-left: auto; border-color: #d7c5a4; background: #fffaf2; }
    .bubble.assistant { margin-right: auto; }
    .bubble .meta { font-size: 12px; color: var(--muted); margin-bottom: 6px; }
    .composer { padding: 14px 18px; background: white; border-top: 1px solid var(--line); }
    .composer textarea { min-height: 84px; }
    .project-form { padding: 14px 18px; background: #fbfcfe; border-top: 1px solid var(--line); }
    .grid2 { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; }
    .viewer { border: 1px solid var(--line); border-radius: 8px; background: #fbfcfe; min-height: 260px; padding: 10px; overflow: auto; }
    .viewer img, .viewer video { max-width: 100%; border-radius: 6px; }
    .viewer iframe { width: 100%; min-height: 460px; border: 0; background: white; }
    .viewer audio { width: 100%; }
    .tabs { display: flex; gap: 6px; margin-bottom: 10px; flex-wrap: wrap; }
    .tabs button { padding: 7px 9px; background: #e7edf3; color: var(--ink); }
    .tabs button.active { background: var(--teal); color: white; }
    .pill { display: inline-flex; align-items: center; border-radius: 999px; padding: 2px 8px; background: #eef2f6; color: #334155; font-size: 12px; }
    a { color: #075985; }
    @media (max-width: 1100px) {
      .app { grid-template-columns: 1fr; }
      aside, .right { border: 0; border-bottom: 1px solid var(--line); max-height: none; }
      .main { min-height: 700px; }
    }
  </style>
</head>
<body>
  <div class="app">
    <aside>
      <section>
        <h1>Musai Studio</h1>
        <div class="small muted" id="setup-line">Loading setup...</div>
      </section>
      <section>
        <div class="row">
          <h2 style="flex:1">Sessions</h2>
          <button class="secondary" id="new-session">New</button>
        </div>
        <div id="sessions" class="list"></div>
      </section>
      <section>
        <h2>Profiles</h2>
        <pre id="profiles" class="small"></pre>
      </section>
      <section>
        <h2>Projects</h2>
        <div id="projects" class="list"></div>
      </section>
    </aside>

    <div class="main">
      <header>
        <h1 id="session-title">Musai Chat Router</h1>
        <div id="session-subtitle" class="small muted"></div>
      </header>

      <div id="chat" class="chat"></div>

      <div>
        <div class="composer">
          <textarea id="message" placeholder="Ask about the song, setup, localization, stems, lyrics, chords, or generation."></textarea>
          <div class="row" style="margin-top:8px">
            <button id="send-chat">Chat</button>
            <button id="send-worker" class="worker">Worker</button>
            <button id="send-auto" class="secondary">Auto</button>
            <span id="chat-status" class="small muted"></span>
          </div>
        </div>

        <details class="project-form">
          <summary><strong>Create Project</strong></summary>
          <div class="grid2">
            <div><label>Title</label><input id="project-title" value="New Musai song"></div>
            <div><label>Provider</label><select id="project-provider"><option>deepseek</option><option>openai</option><option>offline</option></select></div>
            <div><label>Model</label><input id="project-model" placeholder="deepseek-reasoner or gpt-5.5"></div>
            <div><label>Language</label><input id="project-language" value="en"></div>
            <div><label>Generation Mode</label><select id="project-generation-mode"><option>auto</option><option>free_vocal</option><option>melody_generation</option><option>full_production</option><option>controlled_song</option><option>localization</option></select></div>
            <div><label>Control Level</label><select id="project-control-level"><option>auto</option><option>free</option><option>lyrics</option><option>lyrics_chords</option><option>melody_sheet</option><option>reference_audio</option><option>strict_localization</option></select></div>
            <div><label>Target Language</label><input id="project-target" placeholder="zh-CN, en, ja"></div>
            <div><label>Reference Audio Path</label><input id="project-reference" placeholder="/path/to/reference.wav"></div>
          </div>
          <label>Idea</label><textarea id="project-idea"></textarea>
          <label>Lyrics</label><textarea id="project-lyrics"></textarea>
          <label>Melody / 旋律 / Sheet Notes</label><textarea id="project-melody" placeholder="Melody contour, hook rhythm, jianpu/numbered notation, staff notes, phrase counts, or a friend recording description."></textarea>
          <label>Style References</label><textarea id="project-style-references" placeholder="Broad style influences only; not a request to impersonate a real voice."></textarea>
          <label>Voice Notes</label><textarea id="project-voice-notes" placeholder="Vocal range, timbre, language, emotion, pronunciation, or consented voice details."></textarea>
          <div class="row" style="margin-top:8px">
            <label style="margin:0; font-weight:600"><input id="project-analyze" type="checkbox" style="width:auto"> Analyze reference</label>
            <label style="margin:0; font-weight:600"><input id="project-rights" type="checkbox" style="width:auto"> Rights confirmed</label>
            <label style="margin:0; font-weight:600"><input id="project-voice-consent" type="checkbox" style="width:auto"> Voice consent</label>
            <button id="create-project">Create</button>
            <span id="project-status" class="small muted"></span>
          </div>
        </details>

        <details class="project-form">
          <summary><strong>SoulX Verse</strong></summary>
          <div class="grid2">
            <div><label>Title</label><input id="verse-title" value="Rain Day Bilingual Verse"></div>
            <div><label>Provider</label><select id="verse-provider"><option>deepseek</option><option>openai</option><option>offline</option></select></div>
            <div><label>Model</label><input id="verse-model" placeholder="deepseek-reasoner or gpt-5.5"></div>
            <div><label>Device</label><input id="verse-device" value="cuda"></div>
          </div>
          <label>Idea</label><textarea id="verse-idea">A gentle rainy-day musical short film verse in Chinese and English.</textarea>
          <label>Lyrics</label><textarea id="verse-lyrics" placeholder="Optional. Leave empty and Musai will create bilingual rainy-day lyrics."></textarea>
          <div class="row" style="margin-top:8px">
            <label style="margin:0; font-weight:600"><input id="verse-refine" type="checkbox" checked style="width:auto"> AI refine</label>
            <label style="margin:0; font-weight:600"><input id="verse-run-soulx" type="checkbox" checked style="width:auto"> Run SoulX</label>
            <button id="generate-soulx-verse">Generate Verse</button>
            <span id="verse-status" class="small muted"></span>
          </div>
        </details>
      </div>
    </div>

    <div class="right">
      <section>
        <h2>Jobs</h2>
        <div id="jobs" class="list"></div>
      </section>
      <section>
        <div class="row">
          <h2 style="flex:1">Artifacts</h2>
          <button class="secondary" id="refresh-artifacts">Refresh</button>
        </div>
        <div class="tabs">
          <button data-tab="all" class="active">All</button>
          <button data-tab="canvas">Canvas</button>
          <button data-tab="editor">Editor</button>
          <button data-tab="pdf">PDF</button>
        </div>
        <div id="artifacts" class="list"></div>
      </section>
      <section>
        <h2>Canvas</h2>
        <div id="viewer" class="viewer muted">No artifact selected.</div>
      </section>
    </div>
  </div>

<script>
const state = { sessionId: "", selectedArtifactId: "", artifactTab: "all", artifacts: [] };
const $ = (id) => document.getElementById(id);

async function api(url, options = {}) {
  const res = await fetch(url, options);
  const type = res.headers.get("content-type") || "";
  const body = type.includes("application/json") ? await res.json() : await res.text();
  if (!res.ok) throw new Error(typeof body === "string" ? body : JSON.stringify(body));
  return body;
}

function escapeHtml(value) {
  return String(value || "").replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}

function artifactIcon(kind) {
  return {image:"image", audio:"audio", video:"video", pdf:"pdf", markdown:"md", text:"txt"}[kind] || "file";
}

async function loadSetup() {
  const setup = await api("/api/setup");
  $("setup-line").innerHTML = [
    setup.codex_cli ? "codex ok" : "codex missing",
    setup.deepseek_api_key ? "DeepSeek key" : "DeepSeek no key",
    setup.openai_api_key ? "OpenAI key" : "OpenAI no key"
  ].map(x => `<span class="pill">${escapeHtml(x)}</span>`).join(" ");
  $("profiles").textContent = JSON.stringify(setup.profiles, null, 2);
}

async function loadSessions() {
  const sessions = await api("/api/chat/sessions");
  if (!state.sessionId && sessions.length) state.sessionId = sessions[0].id;
  $("sessions").innerHTML = sessions.length ? sessions.map(s => `
    <div class="item ${s.id === state.sessionId ? "active" : ""}" data-session="${escapeHtml(s.id)}">
      <div class="item-title">${escapeHtml(s.title || s.id)}</div>
      <div class="small muted">${escapeHtml(s.id)} · ${s.message_count || 0} msg · ${s.artifact_count || 0} art</div>
    </div>`).join("") : `<div class="muted small">No sessions.</div>`;
  document.querySelectorAll("[data-session]").forEach(el => el.onclick = () => selectSession(el.dataset.session));
}

async function selectSession(id) {
  state.sessionId = id;
  state.selectedArtifactId = "";
  await refreshSession();
}

async function newSession() {
  const session = await api("/api/chat/sessions", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({title: "Musai chat"})
  });
  state.sessionId = session.id;
  await refreshAll();
}

function renderMessages(messages) {
  $("chat").innerHTML = messages.length ? messages.map(m => `
    <div class="bubble ${m.role === "user" ? "user" : "assistant"}">
      <div class="meta">${escapeHtml(m.role)} ${m.profile ? "· " + escapeHtml(m.profile) : ""} ${m.status && m.status !== "ok" ? "· " + escapeHtml(m.status) : ""}</div>
      <pre>${escapeHtml(m.content)}</pre>
    </div>`).join("") : `<div class="muted">No messages yet.</div>`;
  $("chat").scrollTop = $("chat").scrollHeight;
}

async function loadMessages() {
  if (!state.sessionId) return renderMessages([]);
  const messages = await api(`/api/chat/messages?session_id=${encodeURIComponent(state.sessionId)}`);
  const session = (await api("/api/chat/sessions")).find(s => s.id === state.sessionId) || {};
  $("session-title").textContent = session.title || "Musai Chat Router";
  $("session-subtitle").textContent = state.sessionId;
  renderMessages(messages);
}

async function send(mode) {
  const text = $("message").value.trim();
  if (!text) return;
  $("chat-status").textContent = "sending...";
  $("send-chat").disabled = $("send-worker").disabled = $("send-auto").disabled = true;
  try {
    const result = await api("/api/chat/send", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({session_id: state.sessionId, message: text, mode})
    });
    state.sessionId = result.session_id;
    $("message").value = "";
    $("chat-status").textContent = result.mode === "worker" ? `queued ${result.job.id}` : "done";
    await refreshSession();
  } catch (err) {
    $("chat-status").textContent = err.message;
  } finally {
    $("send-chat").disabled = $("send-worker").disabled = $("send-auto").disabled = false;
  }
}

async function loadProjects() {
  const projects = await api("/api/projects");
  $("projects").innerHTML = projects.length ? projects.slice(0, 8).map(p => {
    const m = p.materials || {};
    return `<div class="item">
      <div class="item-title">${escapeHtml(m.title || p.project_id)}</div>
      <div class="small muted">${escapeHtml(p.workflow)} · ${escapeHtml(p.provider)}/${escapeHtml(p.model)}</div>
      <div class="small"><a href="/project/${encodeURIComponent(p.project_id)}/BRIEF.md" target="_blank">BRIEF</a> · <a href="/project/${encodeURIComponent(p.project_id)}/SOULX_REQUEST.md" target="_blank">SoulX</a> · <a href="/project/${encodeURIComponent(p.project_id)}/commands.sh" target="_blank">commands</a></div>
    </div>`;
  }).join("") : `<div class="muted small">No projects.</div>`;
}

async function createProject() {
  $("project-status").textContent = "creating...";
  try {
    const payload = {
      title: $("project-title").value,
      provider: $("project-provider").value,
      model: $("project-model").value,
      language: $("project-language").value,
      vocal_language: $("project-language").value,
      target_language: $("project-target").value,
      reference_audio: $("project-reference").value,
      generation_mode: $("project-generation-mode").value,
      control_level: $("project-control-level").value,
      idea: $("project-idea").value,
      lyrics: $("project-lyrics").value,
      melody: $("project-melody").value,
      style_references: $("project-style-references").value,
      voice_notes: $("project-voice-notes").value,
      rights_confirmed: $("project-rights").checked,
      voice_consent: $("project-voice-consent").checked,
      duration: 120,
      analyze_reference: $("project-analyze").checked
    };
    const project = await api("/api/projects", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(payload)
    });
    $("project-status").textContent = `created ${project.project_id}`;
    await loadProjects();
  } catch (err) {
    $("project-status").textContent = err.message;
  }
}

async function createSoulXVerse() {
  $("verse-status").textContent = "generating...";
  $("generate-soulx-verse").disabled = true;
  try {
    const payload = {
      session_id: state.sessionId,
      title: $("verse-title").value,
      provider: $("verse-provider").value,
      model: $("verse-model").value,
      device: $("verse-device").value,
      idea: $("verse-idea").value,
      lyrics: $("verse-lyrics").value,
      refine: $("verse-refine").checked,
      run_soulx: $("verse-run-soulx").checked
    };
    const result = await api("/api/soulx/verse", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(payload)
    });
    state.sessionId = result.session_id || state.sessionId;
    $("verse-status").textContent = `created ${result.output_dir}`;
    await refreshSession();
  } catch (err) {
    $("verse-status").textContent = err.message;
  } finally {
    $("generate-soulx-verse").disabled = false;
  }
}

async function loadJobs() {
  if (!state.sessionId) return;
  const jobs = await api(`/api/jobs?session_id=${encodeURIComponent(state.sessionId)}`);
  $("jobs").innerHTML = jobs.length ? jobs.slice(0, 8).map(job => `
    <div class="item">
      <div class="item-title">${escapeHtml(job.status)} · ${escapeHtml(job.id)}</div>
      <div class="small muted">${escapeHtml((job.message || "").slice(0, 120))}</div>
    </div>`).join("") : `<div class="muted small">No jobs.</div>`;
}

function filteredArtifacts() {
  if (state.artifactTab === "all") return state.artifacts;
  return state.artifacts.filter(a => a.tab === state.artifactTab || a.kind === state.artifactTab);
}

async function loadArtifacts() {
  if (!state.sessionId) {
    state.artifacts = [];
    $("artifacts").innerHTML = "";
    return;
  }
  const data = await api(`/api/artifacts?session_id=${encodeURIComponent(state.sessionId)}`);
  state.artifacts = data.items || [];
  if (!state.selectedArtifactId && data.selected_artifact_id) state.selectedArtifactId = data.selected_artifact_id;
  renderArtifacts();
  if (state.selectedArtifactId) await renderArtifact(state.selectedArtifactId);
}

function renderArtifacts() {
  const items = filteredArtifacts();
  $("artifacts").innerHTML = items.length ? items.map(a => `
    <div class="item ${a.id === state.selectedArtifactId ? "active" : ""}" data-artifact="${escapeHtml(a.id)}">
      <div class="item-title">${escapeHtml(artifactIcon(a.kind))} · ${escapeHtml(a.title)}</div>
      <div class="small muted">${escapeHtml(a.kind)} · ${escapeHtml(a.source)} · ${escapeHtml(a.filename || "")}</div>
    </div>`).join("") : `<div class="muted small">No artifacts.</div>`;
  document.querySelectorAll("[data-artifact]").forEach(el => el.onclick = () => renderArtifact(el.dataset.artifact));
}

async function renderArtifact(id) {
  state.selectedArtifactId = id;
  renderArtifacts();
  const data = await api(`/api/artifact?session_id=${encodeURIComponent(state.sessionId)}&artifact_id=${encodeURIComponent(id)}`);
  const item = data.artifact || {};
  if (data.text !== undefined) {
    $("viewer").innerHTML = `<pre>${escapeHtml(data.text)}</pre>`;
  } else if (data.data_url && item.kind === "image") {
    $("viewer").innerHTML = `<img src="${data.data_url}" alt="${escapeHtml(item.title)}">`;
  } else if (data.data_url && item.kind === "audio") {
    $("viewer").innerHTML = `<audio controls src="${data.data_url}"></audio>`;
  } else if (data.data_url && item.kind === "video") {
    $("viewer").innerHTML = `<video controls src="${data.data_url}"></video>`;
  } else if (data.data_url && item.kind === "pdf") {
    $("viewer").innerHTML = `<iframe src="${data.data_url}"></iframe>`;
  } else {
    const url = `/api/artifact/file?session_id=${encodeURIComponent(state.sessionId)}&artifact_id=${encodeURIComponent(id)}`;
    $("viewer").innerHTML = `<p>${escapeHtml(item.title || data.filename)}</p><p><a href="${url}" target="_blank">Open artifact</a></p>`;
  }
}

async function refreshSession() {
  await Promise.all([loadSessions(), loadMessages(), loadJobs(), loadArtifacts(), loadProjects()]);
}

async function refreshAll() {
  await loadSetup();
  await loadSessions();
  if (!state.sessionId) await newSession();
  await refreshSession();
}

$("new-session").onclick = newSession;
$("send-chat").onclick = () => send("chat");
$("send-worker").onclick = () => send("worker");
$("send-auto").onclick = () => send("auto");
$("create-project").onclick = createProject;
$("generate-soulx-verse").onclick = createSoulXVerse;
$("refresh-artifacts").onclick = loadArtifacts;
document.querySelectorAll(".tabs button").forEach(button => {
  button.onclick = () => {
    document.querySelectorAll(".tabs button").forEach(b => b.classList.remove("active"));
    button.classList.add("active");
    state.artifactTab = button.dataset.tab;
    renderArtifacts();
  };
});
setInterval(() => {
  if (state.sessionId) Promise.all([loadJobs(), loadArtifacts(), loadMessages(), loadSessions()]).catch(() => {});
}, 5000);
refreshAll().catch(err => { $("chat").textContent = err.message; });
</script>
</body>
</html>"""


class Handler(BaseHTTPRequestHandler):
    server_version = "MusaiStudio/0.2"

    def send_json(self, data: object, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_text(self, text: str, content_type: str = "text/plain; charset=utf-8", status: HTTPStatus = HTTPStatus.OK) -> None:
        body = text.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_bytes(self, body: bytes, content_type: str, status: HTTPStatus = HTTPStatus.OK) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def read_json(self) -> dict[str, object]:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            return {}
        return json.loads(self.rfile.read(length).decode("utf-8") or "{}")

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)
        try:
            if path == "/":
                self.send_text(PAGE, "text/html; charset=utf-8")
            elif path == "/api/setup":
                self.send_json(setup_status())
            elif path == "/api/settings":
                self.send_json(load_settings())
            elif path == "/api/models":
                self.send_json(MODEL_REGISTRY)
            elif path == "/api/projects":
                self.send_json(list_projects())
            elif path == "/api/chat/sessions":
                self.send_json(list_sessions())
            elif path == "/api/chat/messages":
                self.send_json(load_messages(query.get("session_id", [""])[0]))
            elif path == "/api/jobs":
                self.send_json(list_jobs(query.get("session_id", [""])[0] or None))
            elif path == "/api/job":
                job = load_job(query.get("id", [""])[0])
                self.send_json(job or {"error": "not found"}, HTTPStatus.OK if job else HTTPStatus.NOT_FOUND)
            elif path == "/api/artifacts":
                self.send_json(list_artifacts(query.get("session_id", [""])[0]))
            elif path == "/api/artifact":
                self.send_json(artifact_payload(query.get("session_id", [""])[0], query.get("artifact_id", [""])[0]))
            elif path == "/api/artifact/file":
                self.serve_artifact_file(query.get("session_id", [""])[0], query.get("artifact_id", [""])[0])
            elif path.startswith("/project/"):
                self.serve_project_file(path)
            else:
                self.send_text("not found", status=HTTPStatus.NOT_FOUND)
        except Exception as exc:
            self.send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        try:
            payload = self.read_json()
            if path == "/api/settings":
                self.send_json(save_settings(payload))
            elif path == "/api/chat/sessions":
                self.send_json(create_session(str(payload.get("title") or "Musai chat")), HTTPStatus.CREATED)
            elif path == "/api/chat/send":
                self.send_json(
                    send_chat_message(
                        str(payload.get("session_id") or "") or None,
                        str(payload.get("message") or ""),
                        str(payload.get("mode") or "auto"),
                    )
                )
            elif path == "/api/artifacts":
                self.send_json(
                    register_artifact(
                        session_id=str(payload.get("session_id") or ""),
                        title=str(payload.get("title") or "Artifact"),
                        path=str(payload.get("path") or "") or None,
                        text=str(payload.get("text")) if payload.get("text") is not None else None,
                        kind=str(payload.get("kind") or "") or None,
                        source=str(payload.get("source") or "manual"),
                        tab=str(payload.get("tab") or "") or None,
                        selected=bool(payload.get("selected")),
                    ),
                    HTTPStatus.CREATED,
                )
            elif path == "/api/artifact/select":
                self.send_json(select_artifact(str(payload.get("session_id") or ""), str(payload.get("artifact_id") or "")))
            elif path == "/api/projects":
                self.handle_create_project(payload)
            elif path == "/api/soulx/verse":
                self.handle_soulx_verse(payload)
            else:
                self.send_text("not found", status=HTTPStatus.NOT_FOUND)
        except Exception as exc:
            self.send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)

    def handle_create_project(self, payload: dict[str, object]) -> None:
        materials = CreativeMaterials(
            title=str(payload.get("title") or "Untitled song"),
            idea=str(payload.get("idea") or ""),
            lyrics=str(payload.get("lyrics") or ""),
            chords=str(payload.get("chords") or ""),
            notation=str(payload.get("notation") or ""),
            melody=str(payload.get("melody") or ""),
            style=str(payload.get("style") or ""),
            genre=str(payload.get("genre") or ""),
            mood=str(payload.get("mood") or ""),
            language=str(payload.get("language") or "en"),
            vocal_language=str(payload.get("vocal_language") or payload.get("language") or "en"),
            reference_audio=str(payload.get("reference_audio") or ""),
            target_language=str(payload.get("target_language") or ""),
            generation_mode=str(payload.get("generation_mode") or "auto"),
            control_level=str(payload.get("control_level") or "auto"),
            style_references=str(payload.get("style_references") or ""),
            voice_notes=str(payload.get("voice_notes") or ""),
            rights_confirmed=bool(payload.get("rights_confirmed")),
            voice_consent=bool(payload.get("voice_consent")),
            duration=int(payload.get("duration") or 120),
            bpm=payload.get("bpm"),
            keyscale=str(payload.get("keyscale") or ""),
            notes=str(payload.get("notes") or ""),
        )
        project = create_project(
            materials,
            provider=str(payload.get("provider") or "deepseek"),
            model=str(payload.get("model") or "") or None,
            analyze_reference=bool(payload.get("analyze_reference")),
        )
        self.send_json(json.loads(Path(project.root, "project.json").read_text(encoding="utf-8")), HTTPStatus.CREATED)

    def handle_soulx_verse(self, payload: dict[str, object]) -> None:
        request = SoulXVerseRequest(
            title=str(payload.get("title") or "Rain Day Bilingual Verse"),
            idea=str(payload.get("idea") or "A gentle rainy-day verse in Chinese and English."),
            lyrics=str(payload.get("lyrics") or ""),
            provider=str(payload.get("provider") or "deepseek"),
            model=str(payload.get("model") or ""),
            refine=bool(payload.get("refine", True)),
            run_soulx=bool(payload.get("run_soulx", True)),
            device=str(payload.get("device") or "cuda"),
        )
        result = generate_soulx_verse(request)
        session_id = str(payload.get("session_id") or "")
        artifacts: list[dict[str, object]] = []
        if session_id:
            artifacts.append(
                register_artifact(session_id, "SoulX verse mix", path=result.mix_wav, kind="audio", source="soulx-verse", tab="canvas", selected=True)
            )
            artifacts.append(
                register_artifact(session_id, "SoulX verse vocal", path=result.vocal_wav, kind="audio", source="soulx-verse", tab="canvas")
            )
            artifacts.append(
                register_artifact(session_id, "SoulX verse melody", path=result.melody_wav, kind="audio", source="soulx-verse", tab="canvas")
            )
            artifacts.append(
                register_artifact(session_id, "SoulX verse lyrics", path=result.lyrics_md, kind="markdown", source="soulx-verse", tab="editor")
            )
            artifacts.append(
                register_artifact(session_id, "LALACHAN music handoff", path=result.handoff, kind="markdown", source="soulx-verse", tab="editor")
            )
        self.send_json({**result.__dict__, "session_id": session_id, "artifacts": artifacts}, HTTPStatus.CREATED)

    def serve_project_file(self, path: str) -> None:
        parts = [unquote(part) for part in path.split("/") if part]
        if len(parts) < 3:
            self.send_text("missing project file", status=HTTPStatus.BAD_REQUEST)
            return
        project_id = parts[1]
        rel = Path(*parts[2:])
        base = (PROJECTS_ROOT / project_id).resolve()
        target = (base / rel).resolve()
        if base not in target.parents and target != base:
            self.send_text("invalid path", status=HTTPStatus.BAD_REQUEST)
            return
        if not target.exists() or not target.is_file():
            self.send_text("not found", status=HTTPStatus.NOT_FOUND)
            return
        content_type = "text/markdown; charset=utf-8" if target.suffix == ".md" else "text/plain; charset=utf-8"
        self.send_text(target.read_text(encoding="utf-8"), content_type)

    def serve_artifact_file(self, session_id: str, artifact_id: str) -> None:
        data = get_artifact(session_id, artifact_id)
        self.send_bytes(data["path"].read_bytes(), data["mime"])

    def log_message(self, fmt: str, *args: object) -> None:
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the local Musai Studio web app.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"Musai Studio: http://{args.host}:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
