#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import mimetypes
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
    resolve_working_dir,
    save_settings,
    select_artifact,
    send_chat_message,
    setup_status,
    update_session_working_dir,
)


PAGE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Musai Studio</title>
  <link rel="icon" href="/assets/brand/fun-lazying-art-logo-192.png" type="image/png">
  <style>
    :root {
      color-scheme: light;
      --bg: #fff8ea;
      --paper: rgba(255,255,255,.86);
      --paper-solid: #ffffff;
      --ink: #111827;
      --muted: #64748b;
      --line: rgba(15,23,42,.12);
      --teal: #15a394;
      --blue: #2563eb;
      --violet: #7c3aed;
      --rose: #e85d75;
      --amber: #f59e0b;
      --green: #16a34a;
      --shadow: 0 24px 70px rgba(31, 41, 55, .13);
    }
    * { box-sizing: border-box; }
    html { min-height: 100%; }
    body {
      margin: 0;
      min-height: 100vh;
      color: var(--ink);
      background:
        radial-gradient(circle at 12% 0%, rgba(21,163,148,.23), transparent 32rem),
        radial-gradient(circle at 78% 4%, rgba(232,93,117,.22), transparent 30rem),
        linear-gradient(135deg, #fff9e8 0%, #f7fbff 52%, #fff6fb 100%);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      font-size: 16px;
      letter-spacing: 0;
    }
    button, input, textarea, select { font: inherit; }
    button {
      border: 0;
      border-radius: 999px;
      background: linear-gradient(135deg, var(--teal), var(--blue));
      color: white;
      padding: 11px 16px;
      font-weight: 800;
      cursor: pointer;
      box-shadow: 0 10px 26px rgba(37, 99, 235, .18);
    }
    button.secondary { background: rgba(255,255,255,.72); color: var(--ink); border: 1px solid var(--line); box-shadow: none; }
    button.worker { background: linear-gradient(135deg, var(--amber), var(--rose)); }
    button.ghost { background: transparent; color: var(--muted); border: 1px solid var(--line); box-shadow: none; }
    button:disabled { opacity: .55; cursor: wait; }
    input, textarea, select {
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 11px 12px;
      background: rgba(255,255,255,.86);
      color: var(--ink);
      outline: none;
    }
    input:focus, textarea:focus, select:focus { border-color: rgba(21,163,148,.65); box-shadow: 0 0 0 4px rgba(21,163,148,.13); }
    textarea { min-height: 92px; resize: vertical; line-height: 1.45; }
    label { display: block; margin: 12px 0 6px; color: #334155; font-size: 13px; font-weight: 850; }
    h1, h2, h3, p { margin-top: 0; }
    h1 { margin-bottom: 5px; font-size: clamp(30px, 4vw, 50px); line-height: .98; }
    h2 { margin-bottom: 8px; font-size: 22px; }
    h3 { margin-bottom: 8px; font-size: 15px; color: var(--muted); text-transform: uppercase; }
    pre { margin: 0; white-space: pre-wrap; overflow: auto; }
    a { color: #1d4ed8; }
    .topbar {
      position: sticky;
      top: 0;
      z-index: 20;
      display: grid;
      grid-template-columns: auto minmax(260px, 1fr) auto;
      gap: 18px;
      align-items: center;
      padding: 16px clamp(16px, 3vw, 36px);
      backdrop-filter: blur(20px);
      background: rgba(255,248,234,.76);
      border-bottom: 1px solid rgba(15,23,42,.08);
    }
    .brand { display: flex; gap: 12px; align-items: center; min-width: 220px; }
    .brand-logo, .mark { width: 46px; height: 46px; display: grid; place-items: center; border-radius: 16px; object-fit: cover; box-shadow: 0 12px 30px rgba(21,163,148,.16); }
    .mark { background: linear-gradient(135deg, var(--rose), var(--violet), var(--teal)); color: #fff; font-weight: 950; }
    .brand strong, .brand span { display: block; }
    .brand strong { font-size: clamp(22px, 2.6vw, 32px); line-height: .92; letter-spacing: 0; }
    .brand span, .muted, .small { color: var(--muted); }
    .small { font-size: 13px; }
    .workspace-line { display: grid; grid-template-columns: minmax(260px, 1fr) auto auto; gap: 10px; align-items: center; }
    .session-chip { max-width: 420px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; border: 1px solid var(--line); border-radius: 999px; padding: 10px 13px; background: rgba(255,255,255,.78); color: #334155; }
    .shell {
      width: min(1420px, 100%);
      margin: 0 auto;
      padding: 28px clamp(16px, 3vw, 36px) 190px;
      display: grid;
      grid-template-columns: minmax(0, 1fr) minmax(300px, 380px);
      gap: 20px;
    }
    .hero, .panel, .dock-card, .composer {
      border: 1px solid rgba(15,23,42,.1);
      background: var(--paper);
      box-shadow: var(--shadow);
      border-radius: 24px;
    }
    .hero { padding: 26px; overflow: hidden; position: relative; }
    .hero:after {
      content: "";
      position: absolute;
      inset: auto -70px -130px auto;
      width: 320px;
      height: 320px;
      border-radius: 50%;
      background: radial-gradient(circle, rgba(245,158,11,.28), transparent 66%);
      pointer-events: none;
    }
    .hero p { max-width: 760px; color: #475569; font-size: 18px; line-height: 1.55; }
    .quick-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; margin-top: 18px; }
    .quick-card { border: 1px solid var(--line); border-radius: 18px; padding: 14px; background: rgba(255,255,255,.68); }
    .quick-card strong { display: block; margin-bottom: 6px; }
    .pill-row { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 14px; }
    .pill { display: inline-flex; align-items: center; border-radius: 999px; padding: 6px 10px; background: rgba(255,255,255,.74); border: 1px solid var(--line); color: #475569; font-size: 13px; font-weight: 750; }
    .panel { margin-top: 18px; padding: 18px; }
    .panel summary, .dock-card summary { cursor: pointer; font-weight: 900; }
    .grid2 { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }
    .checks { display: flex; flex-wrap: wrap; gap: 12px; margin: 12px 0; }
    .checks label { margin: 0; display: inline-flex; gap: 7px; align-items: center; }
    .checks input { width: auto; }
    .conversation {
      margin-top: 18px;
      display: grid;
      gap: 14px;
      min-height: 320px;
      scroll-margin-bottom: 180px;
    }
    .empty {
      padding: 26px;
      border: 1px dashed rgba(21,163,148,.36);
      border-radius: 22px;
      background: rgba(255,255,255,.62);
      color: #475569;
      font-size: 18px;
    }
    .bubble {
      max-width: 900px;
      border: 1px solid var(--line);
      border-radius: 22px;
      padding: 16px 18px;
      background: rgba(255,255,255,.82);
      box-shadow: 0 14px 34px rgba(15,23,42,.07);
    }
    .bubble.user { margin-left: auto; background: linear-gradient(135deg, rgba(255,255,255,.9), rgba(255,237,213,.82)); border-color: rgba(245,158,11,.3); }
    .bubble.assistant { margin-right: auto; }
    .meta { margin-bottom: 8px; color: var(--muted); font-size: 13px; font-weight: 800; }
    .side-dock { display: grid; gap: 12px; align-content: start; position: sticky; top: 88px; }
    .dock-card { padding: 14px; box-shadow: 0 14px 38px rgba(15,23,42,.08); }
    .dock-card[open] { background: rgba(255,255,255,.92); }
    .dock-body { margin-top: 12px; display: grid; gap: 10px; }
    .item { border: 1px solid var(--line); border-radius: 16px; padding: 12px; background: rgba(255,255,255,.76); cursor: pointer; }
    .item.active { border-color: rgba(21,163,148,.7); box-shadow: 0 0 0 4px rgba(21,163,148,.12); }
    .item-title { font-weight: 850; overflow-wrap: anywhere; }
    .tabs { display: flex; gap: 7px; flex-wrap: wrap; }
    .tabs button { padding: 8px 10px; }
    .viewer { min-height: 220px; max-height: 520px; overflow: auto; border: 1px solid var(--line); border-radius: 16px; padding: 12px; background: rgba(255,255,255,.72); }
    .viewer img, .viewer video { max-width: 100%; border-radius: 14px; }
    .viewer iframe { width: 100%; min-height: 420px; border: 0; background: #fff; }
    .viewer audio { width: 100%; }
    .composer {
      position: fixed;
      z-index: 30;
      left: 50%;
      bottom: 18px;
      transform: translateX(-50%);
      width: min(980px, calc(100% - 28px));
      padding: 12px;
      backdrop-filter: blur(22px);
      background: rgba(255,255,255,.86);
    }
    .composer textarea { min-height: 74px; max-height: 180px; border-radius: 18px; font-size: 17px; }
    .composer-actions { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; margin-top: 10px; }
    .composer-actions .status { margin-left: auto; color: var(--muted); font-size: 13px; }
    @media (max-width: 1100px) {
      .topbar { grid-template-columns: 1fr; }
      .workspace-line { grid-template-columns: 1fr; }
      .shell { grid-template-columns: 1fr; }
      .side-dock { position: static; }
      .quick-grid, .grid2 { grid-template-columns: 1fr 1fr; }
    }
    @media (max-width: 680px) {
      body { font-size: 15px; }
      .quick-grid, .grid2 { grid-template-columns: 1fr; }
      .shell { padding-bottom: 220px; }
    }
  </style>
</head>
<body>
  <header class="topbar">
    <div class="brand">
      <img class="brand-logo" src="/assets/brand/fun-lazying-art-logo-192.png" alt="" width="46" height="46">
      <div><strong>Musai Studio</strong></div>
    </div>
    <div class="workspace-line">
      <input id="working-dir" aria-label="Working directory" placeholder="/path/to/music-folder">
      <button id="apply-workdir" class="secondary" type="button">Use folder</button>
      <button id="new-session" type="button">New session</button>
    </div>
    <div id="current-session" class="session-chip">No session loaded</div>
  </header>

  <main class="shell">
    <section>
      <div class="hero">
        <h1 id="session-title">Create music from an idea, lyrics, melody, or a song you own.</h1>
        <p id="session-subtitle">Choose a folder, drop your materials there, then chat or send a worker task. Web and CLI messages use the same session, working directory, jobs, and artifacts.</p>
        <div id="setup-line" class="pill-row"></div>
        <div class="quick-grid">
          <div class="quick-card"><strong>Idea</strong><span class="small">Expand a concept into lyrics, mood, and production plan.</span></div>
          <div class="quick-card"><strong>Lyrics</strong><span class="small">Polish lines for rhythm, language, and vocal phrasing.</span></div>
          <div class="quick-card"><strong>Reference</strong><span class="small">Analyze audio, stems, chords, beats, and human voice.</span></div>
          <div class="quick-card"><strong>Localization</strong><span class="small">Adapt a rights-cleared song into a new language.</span></div>
        </div>
      </div>

      <details class="panel">
        <summary>Create a controlled music project</summary>
        <div class="grid2">
          <div><label>Title</label><input id="project-title" value="New Musai song"></div>
          <div><label>Provider</label><select id="project-provider"><option>deepseek</option><option>openai</option><option>offline</option></select></div>
          <div><label>Model</label><input id="project-model" placeholder="deepseek-reasoner or gpt-5.5"></div>
          <div><label>Language</label><input id="project-language" value="en"></div>
          <div><label>Generation mode</label><select id="project-generation-mode"><option>auto</option><option>free_vocal</option><option>melody_generation</option><option>full_production</option><option>controlled_song</option><option>localization</option></select></div>
          <div><label>Control level</label><select id="project-control-level"><option>auto</option><option>free</option><option>lyrics</option><option>lyrics_chords</option><option>melody_sheet</option><option>reference_audio</option><option>strict_localization</option></select></div>
          <div><label>Target language</label><input id="project-target" placeholder="zh-CN, en, ja"></div>
          <div><label>Reference audio path</label><input id="project-reference" placeholder="relative/path.wav or /absolute/path.wav"></div>
        </div>
        <label>Idea</label><textarea id="project-idea" placeholder="What should this song become?"></textarea>
        <label>Lyrics</label><textarea id="project-lyrics" placeholder="Optional lyrics, fragments, hook, or bilingual draft."></textarea>
        <label>Melody / 旋律 / sheet notes</label><textarea id="project-melody" placeholder="Melody contour, hook rhythm, jianpu/numbered notation, staff notes, phrase counts, or friend recording description."></textarea>
        <label>Style references</label><textarea id="project-style-references" placeholder="Broad style influences only; no real voice impersonation unless consented."></textarea>
        <label>Voice notes</label><textarea id="project-voice-notes" placeholder="Vocal range, timbre, emotion, language, pronunciation, consent details."></textarea>
        <div class="checks">
          <label><input id="project-analyze" type="checkbox"> Analyze reference</label>
          <label><input id="project-rights" type="checkbox"> Rights confirmed</label>
          <label><input id="project-voice-consent" type="checkbox"> Voice consent</label>
        </div>
        <button id="create-project" type="button">Create project</button>
        <span id="project-status" class="small muted"></span>
      </details>

      <details class="panel">
        <summary>Generate a SoulX vocal verse</summary>
        <div class="grid2">
          <div><label>Title</label><input id="verse-title" value="Rain Day Bilingual Verse"></div>
          <div><label>Provider</label><select id="verse-provider"><option>deepseek</option><option>openai</option><option>offline</option></select></div>
          <div><label>Model</label><input id="verse-model" placeholder="deepseek-reasoner or gpt-5.5"></div>
          <div><label>Device</label><input id="verse-device" value="cuda"></div>
        </div>
        <label>Idea</label><textarea id="verse-idea">A gentle rainy-day musical short film verse in Chinese and English.</textarea>
        <label>Lyrics</label><textarea id="verse-lyrics" placeholder="Optional. Leave empty and Musai will create bilingual rainy-day lyrics."></textarea>
        <div class="checks">
          <label><input id="verse-refine" type="checkbox" checked> AI refine</label>
          <label><input id="verse-run-soulx" type="checkbox" checked> Run SoulX</label>
        </div>
        <button id="generate-soulx-verse" type="button">Generate verse</button>
        <span id="verse-status" class="small muted"></span>
      </details>

      <div id="chat" class="conversation"></div>
    </section>

    <aside class="side-dock">
      <details class="dock-card">
        <summary>Sessions</summary>
        <div class="dock-body">
          <div class="grid2">
            <input id="resume-id" placeholder="session id">
            <button id="resume-session" class="secondary" type="button">Resume</button>
          </div>
          <div id="sessions" class="dock-body"></div>
        </div>
      </details>
      <details class="dock-card">
        <summary>Jobs</summary>
        <div id="jobs" class="dock-body"></div>
      </details>
      <details class="dock-card">
        <summary>Projects</summary>
        <div id="projects" class="dock-body"></div>
      </details>
      <details class="dock-card">
        <summary>Artifacts and canvas</summary>
        <div class="dock-body">
          <div class="tabs">
            <button data-tab="all" class="secondary" type="button">All</button>
            <button data-tab="canvas" class="secondary" type="button">Canvas</button>
            <button data-tab="editor" class="secondary" type="button">Editor</button>
            <button data-tab="pdf" class="secondary" type="button">PDF</button>
          </div>
          <div id="artifacts" class="dock-body"></div>
          <div id="viewer" class="viewer muted">No artifact selected.</div>
        </div>
      </details>
    </aside>
  </main>

  <div class="composer">
    <textarea id="message" placeholder="Tell Musai what to make, analyze, localize, or refine. Relative paths are read from the working folder."></textarea>
    <div class="composer-actions">
      <button id="send-auto" type="button">Auto route</button>
      <button id="send-chat" class="secondary" type="button">Chat</button>
      <button id="send-worker" class="worker" type="button">Worker</button>
      <span id="chat-status" class="status"></span>
    </div>
  </div>

<script>
const state = {
  sessionId: localStorage.getItem("musaiSessionId") || "",
  workingDir: localStorage.getItem("musaiWorkingDir") || "",
  selectedArtifactId: "",
  artifactTab: "all",
  artifacts: [],
  sessions: []
};
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

function activeWorkingDir() {
  return $("working-dir").value.trim() || state.workingDir || "";
}

function setSession(id) {
  state.sessionId = id || "";
  if (state.sessionId) localStorage.setItem("musaiSessionId", state.sessionId);
}

function setWorkingDir(value) {
  state.workingDir = value || "";
  $("working-dir").value = state.workingDir;
  if (state.workingDir) localStorage.setItem("musaiWorkingDir", state.workingDir);
}

async function loadSetup() {
  const setup = await api("/api/setup");
  if (!state.workingDir) setWorkingDir(setup.root || "");
  $("setup-line").innerHTML = [
    setup.codex_cli ? "Codex ready" : "Codex missing",
    setup.deepseek_api_key ? "DeepSeek key" : "DeepSeek no key",
    setup.openai_api_key ? "OpenAI key" : "OpenAI no key",
    setup.third_party?.soulx_singer ? "SoulX installed" : "SoulX not installed"
  ].map(x => `<span class="pill">${escapeHtml(x)}</span>`).join("");
}

async function loadSessions() {
  const query = activeWorkingDir() ? `?working_dir=${encodeURIComponent(activeWorkingDir())}` : "";
  state.sessions = await api(`/api/chat/sessions${query}`);
  if (!state.sessionId && state.sessions.length) setSession(state.sessions[0].id);
  $("sessions").innerHTML = state.sessions.length ? state.sessions.map(s => `
    <div class="item ${s.id === state.sessionId ? "active" : ""}" data-session="${escapeHtml(s.id)}">
      <div class="item-title">${escapeHtml(s.title || s.id)}</div>
      <div class="small muted">${escapeHtml(s.id)} · ${s.message_count || 0} msg · ${s.artifact_count || 0} art</div>
      <div class="small muted">${escapeHtml(s.working_dir || "")}</div>
    </div>`).join("") : `<div class="muted small">No sessions for this folder yet.</div>`;
  document.querySelectorAll("[data-session]").forEach(el => el.onclick = () => selectSession(el.dataset.session));
  renderSessionHeader();
}

function currentSession() {
  return state.sessions.find(s => s.id === state.sessionId) || {};
}

function renderSessionHeader() {
  const session = currentSession();
  $("session-title").textContent = session.title || "Create music from an idea, lyrics, melody, or a song you own.";
  $("current-session").textContent = state.sessionId ? `${state.sessionId}` : "No session loaded";
  $("session-subtitle").textContent = session.working_dir || activeWorkingDir()
    ? `Working folder: ${session.working_dir || activeWorkingDir()}`
    : "Choose a working folder to sync web and CLI sessions.";
}

async function selectSession(id) {
  setSession(id);
  state.selectedArtifactId = "";
  await refreshSession();
}

async function newSession() {
  const title = $("message").value.trim().slice(0, 70) || "Musai music session";
  const session = await api("/api/chat/sessions", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({title, working_dir: activeWorkingDir()})
  });
  setSession(session.id);
  setWorkingDir(session.working_dir || activeWorkingDir());
  await refreshAll();
}

async function resumeSession() {
  const id = $("resume-id").value.trim();
  if (!id) return;
  const session = await api("/api/chat/resume", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({session_id: id, working_dir: activeWorkingDir()})
  });
  setSession(session.id);
  setWorkingDir(session.working_dir || activeWorkingDir());
  await refreshSession();
}

function renderMessages(messages) {
  $("chat").innerHTML = messages.length ? messages.map(m => `
    <article class="bubble ${m.role === "user" ? "user" : "assistant"}">
      <div class="meta">${escapeHtml(m.role)}${m.profile ? " · " + escapeHtml(m.profile) : ""}${m.status && m.status !== "ok" ? " · " + escapeHtml(m.status) : ""}</div>
      <pre>${escapeHtml(m.content)}</pre>
    </article>`).join("") : `
    <div class="empty">
      Start with a goal like “make a song from these lyrics”, “analyze the files in this folder”, or “localize my licensed song to Chinese”.
      The fixed composer below can route to chat or a worker.
    </div>`;
  window.requestAnimationFrame(() => window.scrollTo({ top: document.body.scrollHeight, behavior: "smooth" }));
}

async function loadMessages() {
  if (!state.sessionId) return renderMessages([]);
  const messages = await api(`/api/chat/messages?session_id=${encodeURIComponent(state.sessionId)}`);
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
      body: JSON.stringify({session_id: state.sessionId, message: text, mode, working_dir: activeWorkingDir()})
    });
    setSession(result.session_id);
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
      <div class="small"><a href="/project/${encodeURIComponent(p.project_id)}/BRIEF.md" target="_blank">Brief</a> · <a href="/project/${encodeURIComponent(p.project_id)}/SOULX_REQUEST.md" target="_blank">SoulX</a> · <a href="/project/${encodeURIComponent(p.project_id)}/commands.sh" target="_blank">Commands</a></div>
    </div>`;
  }).join("") : `<div class="muted small">No projects.</div>`;
}

async function createProject() {
  $("project-status").textContent = "creating...";
  try {
    const payload = {
      working_dir: activeWorkingDir(),
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
      working_dir: activeWorkingDir(),
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
    setSession(result.session_id || state.sessionId);
    $("verse-status").textContent = `created ${result.output_dir}`;
    await refreshSession();
  } catch (err) {
    $("verse-status").textContent = err.message;
  } finally {
    $("generate-soulx-verse").disabled = false;
  }
}

async function loadJobs() {
  if (!state.sessionId) return $("jobs").innerHTML = `<div class="muted small">No session.</div>`;
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
    $("artifacts").innerHTML = `<div class="muted small">No session.</div>`;
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
  renderSessionHeader();
}

async function refreshAll() {
  await loadSetup();
  await loadSessions();
  if (!state.sessionId) await newSession();
  await refreshSession();
}

$("apply-workdir").onclick = async () => { setWorkingDir(activeWorkingDir()); setSession(""); await refreshAll(); };
$("new-session").onclick = newSession;
$("resume-session").onclick = resumeSession;
$("send-chat").onclick = () => send("chat");
$("send-worker").onclick = () => send("worker");
$("send-auto").onclick = () => send("auto");
$("create-project").onclick = createProject;
$("generate-soulx-verse").onclick = createSoulXVerse;
$("message").addEventListener("keydown", (event) => {
  if ((event.metaKey || event.ctrlKey) && event.key === "Enter") send("auto");
});
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
            elif path.startswith("/assets/"):
                self.serve_website_asset(path)
            elif path == "/api/setup":
                self.send_json(setup_status())
            elif path == "/api/settings":
                self.send_json(load_settings())
            elif path == "/api/models":
                self.send_json(MODEL_REGISTRY)
            elif path == "/api/projects":
                self.send_json(list_projects())
            elif path == "/api/chat/sessions":
                self.send_json(list_sessions(query.get("working_dir", [""])[0] or None))
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
                self.send_json(
                    create_session(
                        str(payload.get("title") or "Musai chat"),
                        working_dir=str(payload.get("working_dir") or "") or None,
                    ),
                    HTTPStatus.CREATED,
                )
            elif path == "/api/chat/send":
                self.send_json(
                    send_chat_message(
                        str(payload.get("session_id") or "") or None,
                        str(payload.get("message") or ""),
                        str(payload.get("mode") or "auto"),
                        working_dir=str(payload.get("working_dir") or "") or None,
                    )
                )
            elif path == "/api/chat/resume":
                session = update_session_working_dir(
                    str(payload.get("session_id") or ""),
                    str(payload.get("working_dir") or "") or None,
                )
                self.send_json(session or {"error": "not found"}, HTTPStatus.OK if session else HTTPStatus.NOT_FOUND)
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
        working_dir = resolve_working_dir(str(payload.get("working_dir") or "") or None)
        reference_audio = str(payload.get("reference_audio") or "")
        if reference_audio and not Path(reference_audio).expanduser().is_absolute():
            reference_audio = str((working_dir / reference_audio).resolve())
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
            reference_audio=reference_audio,
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
        working_dir = resolve_working_dir(str(payload.get("working_dir") or "") or None)
        output_dir = str(payload.get("output_dir") or "") or ""
        request = SoulXVerseRequest(
            title=str(payload.get("title") or "Rain Day Bilingual Verse"),
            idea=str(payload.get("idea") or "A gentle rainy-day verse in Chinese and English."),
            lyrics=str(payload.get("lyrics") or ""),
            provider=str(payload.get("provider") or "deepseek"),
            model=str(payload.get("model") or ""),
            output_dir=output_dir,
            refine=bool(payload.get("refine", True)),
            run_soulx=bool(payload.get("run_soulx", True)),
            device=str(payload.get("device") or "cuda"),
        )
        result = generate_soulx_verse(request)
        session_id = str(payload.get("session_id") or "")
        if not session_id:
            session_id = create_session("SoulX verse", working_dir=working_dir)["id"]
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

    def serve_website_asset(self, path: str) -> None:
        parts = [unquote(part) for part in path.split("/") if part]
        rel = Path(*parts)
        base = (ROOT / "website").resolve()
        target = (base / rel).resolve()
        if base not in target.parents and target != base:
            self.send_text("invalid path", status=HTTPStatus.BAD_REQUEST)
            return
        if not target.exists() or not target.is_file():
            self.send_text("not found", status=HTTPStatus.NOT_FOUND)
            return
        content_type = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
        self.send_bytes(target.read_bytes(), content_type)

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
