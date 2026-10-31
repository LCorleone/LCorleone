<div align="center">

<!-- ===================================================================== -->
<!-- 01 // CYBER-HUD HERO BANNER (DARK / LIGHT ADAPTIVE SVG)               -->
<!-- ===================================================================== -->
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./assets/hero-dark.svg" />
  <source media="(prefers-color-scheme: light)" srcset="./assets/hero-light.svg" />
  <img alt="July Lu (@LCorleone) — AI Agent Architect · LLM Gateway Engineer · Native & Wearable Systems" src="./assets/hero-dark.svg" width="100%" />
</picture>

<br />

<!-- ===================================================================== -->
<!-- 02 // QUICK PILLAR NAVIGATION & CREED BADGE BAR                       -->
<!-- ===================================================================== -->
<p align="center">
  <a href="#-featured-engineering-matrix">
    <img src="https://img.shields.io/badge/01_//_AGENT_HARNESS-pi--desktop_·_pi--wx--agent_·_pi--subagents-0F172A?style=flat-square&labelColor=0284C7&color=0F172A" alt="Agent Harness" />
  </a>
  <a href="#-featured-engineering-matrix">
    <img src="https://img.shields.io/badge/02_//_LLM_GATEWAYS-one--api_·_magpie-0F172A?style=flat-square&labelColor=059669&color=0F172A" alt="LLM Gateways" />
  </a>
  <a href="#-featured-engineering-matrix">
    <img src="https://img.shields.io/badge/03_//_WEARABLE_BIO-garmin--miniapp_(mygo_+_HRV/ACWR)-0F172A?style=flat-square&labelColor=D97706&color=0F172A" alt="Wearable Bio-Telemetry" />
  </a>
  <a href="#-featured-engineering-matrix">
    <img src="https://img.shields.io/badge/04_//_NATIVE_%26_AI_LAB-screenshot--dai_·_poker-0F172A?style=flat-square&labelColor=7C3AED&color=0F172A" alt="Native & AI Lab" />
  </a>
</p>

</div>

---

### 🧭 Engineering Topology // How My Projects Connect

<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="./assets/architecture-dark.svg" />
    <source media="(prefers-color-scheme: light)" srcset="./assets/architecture-light.svg" />
    <img alt="Engineering Topology — Interfaces, Agent Orchestration Core, Unified LLM Gateways, Wearable Bio & Native Systems" src="./assets/architecture-dark.svg" width="100%" />
  </picture>
</div>

---

### 🧱 Featured Engineering Matrix

<table>
  <tr>
    <td width="50%" valign="top">
      <h4>🤖 01 // Agent Harness &amp; Multi-Agent Surfaces</h4>
      <p><sub>Full-stack runtime surfaces, zero-port messaging bridges, and multi-agent worktree orchestration built around the <b>Pi Coding Agent</b> ecosystem.</sub></p>
      <ul>
        <li>
          <a href="https://github.com/LCorleone/pi-desktop"><b>pi-desktop</b></a> · <code>TypeScript</code> · <code>v1.9.1</code> · <b>★ 26</b><br />
          Native desktop shell for <code>pi --mode rpc</code> — multi-workspace project management, streaming tool-call chat, slash-command palette, RPC context-usage telemetry calibration, workspace scope retry, and provider/model picker with auth diagnostics.<br />
          <sub><i>Customized fork of <a href="https://github.com/gustavonline/pi-desktop">gustavonline/pi-desktop</a> with dedicated build &amp; release pipeline.</i></sub>
        </li>
        <li>
          <a href="https://github.com/LCorleone/pi-wx-agent"><b>pi-wx-agent</b></a> · <code>JavaScript</code> · <i>Original</i><br />
          In-process WeChat personal assistant bridge (<code>weixin-agent-sdk</code> + <code>pi-coding-agent</code>) requiring <b>zero public inbound ports</b> — QR login, one-time <code>OWNER_CODE</code> claim, <code>/invite</code> family access with per-conversation hash isolation, two-tier verified file memory (<code>MEMORY.md</code> + <code>memory/&lt;topic&gt;.md</code>), nightly reflection (<code>dream</code>), media send/receive, and cross-session WeChat push.
        </li>
        <li>
          <a href="https://github.com/LCorleone/pi-subagents"><b>pi-subagents</b></a> · <code>TypeScript</code> · <code>v0.83.1</code><br />
          Async multi-agent delegation extension — isolated git worktrees, scripted JS workflows, lane-board TUI with UTF-8 character-boundary truncation, supervisor checkpoints, project-trust ancestor discovery guards, and advisor council mode.<br />
          <sub><i>Customized fork of <a href="https://github.com/nicobailon/pi-subagents">nicobailon/pi-subagents</a>.</i></sub>
        </li>
        <li>
          <a href="https://github.com/LCorleone/pi-tau-codex"><b>pi-tau-codex</b></a> · <code>JavaScript</code><br />
          Codex-style browser web UI that live-mirrors running Pi terminal sessions in real time (tool calls, thinking blocks, slash command keyboard menu, extension dialogs) directly from the extension process.<br />
          <sub><i>Customized fork of <a href="https://github.com/Averyyy/pi-tau-codex">Averyyy/pi-tau-codex</a>.</i></sub>
        </li>
        <li>
          <a href="https://github.com/LCorleone/pi-extensions"><b>pi-extensions</b></a> · <a href="https://github.com/LCorleone/pi-tasks"><b>pi-tasks</b></a> (<code>v0.9.0</code>) · <a href="https://github.com/LCorleone/pi-english-polisher"><b>pi-english-polisher</b></a> (<b>★ 1</b>)<br />
          <code>/token</code> per-model breakdown &amp; 30-day usage chart; <code>pi-emote</code> pixel-art HUD with live TPS, cache analytics &amp; git branch telemetry; Claude Code-style task DAG widget; and prefix <code>&gt;</code> mixed CN/EN draft polisher with before/after diff preview.
        </li>
      </ul>
    </td>
    <td width="50%" valign="top">
      <h4>⚡ 02 // LLM Gateways &amp; Protocol Infrastructure</h4>
      <p><sub>High-reliability Go model routers, multi-protocol API translation layers, and idempotent billing/refund engines for coding agents.</sub></p>
      <ul>
        <li>
          <a href="https://github.com/LCorleone/one-api"><b>one-api</b></a> · <code>Go</code><br />
          Multi-tenant, multi-protocol LLM API gateway (OpenAI Chat/Responses, Anthropic Messages, Gemini, DeepSeek, Azure) — hardened with <b>durable idempotent refund intent recovery</b>, timed-out refund deferral without starving recovery workers, and isolated audio retry pipelines with native pricing reconciliation.<br />
          <sub><i>Customized fork of <a href="https://github.com/Laisky/one-api">Laisky/one-api</a>.</i></sub>
        </li>
        <li>
          <a href="https://github.com/LCorleone/magpie"><b>magpie</b></a> · <code>Go</code><br />
          Unified menu-bar &amp; LAN model gateway for coding agents (running Codex on DeepSeek, Claude Code on Kimi) — engineered with <b>streaming <code>tool_use</code> / relay <code>tool_calls</code> state preservation</b> across <code>end_turn</code> boundaries, upstream protocol/stop-reason telemetry, skill library hash-failure resilience, and automatic gateway proxy injection into plugin-spawned child processes.<br />
          <sub><i>Customized fork of <a href="https://github.com/yetone/magpie">yetone/magpie</a>.</i></sub>
        </li>
      </ul>
    </td>
  </tr>
  <tr>
    <td width="50%" valign="top">
      <h4>💓 03 // Wearable Bio-Telemetry &amp; Sports-Science Systems</h4>
      <p><sub>End-to-end physiological modeling, high-frequency wearable ingestion, and native cross-platform desktop visualization.</sub></p>
      <ul>
        <li>
          <a href="https://github.com/LCorleone/garmin-miniapp"><b>garmin-miniapp — Native <code>mygo</code> Desktop Client</b></a> · <code>Go</code> · <i>Original</i><br />
          Native desktop GUI built with a <b>3-tier <code>ui.Router</code> architecture</b>:
          <ul>
            <li><b>Overview Dashboard</b>: daily recovery readiness with sparklines &amp; multi-factor attribution.</li>
            <li><b><code>/trend/*</code> Drilldowns</b>: single-metric longitudinal analysis.</li>
            <li><b><code>/charts</code> Multi-Axis Engine</b>: 6 synchronized X-axis-aligned physiological charts with anomaly markers &amp; painter-level clipping, OS keychain integration (Windows Credential Manager / macOS Keychain / Linux <code>libsecret</code>), system/dark/light high-contrast themes, and opt-in OpenAI-compatible AI coaching.</li>
          </ul>
        </li>
        <li>
          <a href="https://github.com/LCorleone/garmin-miniapp"><b>garmin-miniapp — Sports-Science &amp; Personal API Pipeline</b></a> · <code>Python</code> · <i>Original</i><br />
          <b>6 validated physiological models</b> (HRV 60-day rolling baseline &amp; SD bands, ACWR workload ratio, recovery attribution, sleep architecture, body battery, resting HR) backed by chunked <code>--full-history</code> backfill with ~96 req/min rate-limit resilience, resumable minute-level heart-rate curves (<code>heart_rate.jsonl</code>), incremental analysis cache rebuild, and dual international/China (<code>garmin.cn</code>) OAuth2 endpoint support.
        </li>
      </ul>
    </td>
    <td width="50%" valign="top">
      <h4>🦀 04 // Native Utilities &amp; Applied AI Lab</h4>
      <p><sub>Zero-bloat native desktop tooling in Rust and interactive game-theory + reasoning-model training environments.</sub></p>
      <ul>
        <li>
          <a href="https://github.com/LCorleone/screenshot"><b>screenshot (<code>screenshot-dai</code>)</b></a> · <code>Rust</code> · <b>★ 1</b> · <i>Original</i><br />
          Native Windows screenshot &amp; OCR utility written in Rust — region capture, OCR with structured <b>Table-to-Excel grid paste</b>, contextual LLM chat over captured regions, one-click Chinese translation, and automated self-contained Windows <code>.exe</code> GitHub Release CI.
        </li>
        <li>
          <a href="https://github.com/LCorleone/poker"><b>poker</b></a> · <code>TypeScript</code> · <code>React 19 + Vite 6</code> · <i>Original</i><br />
          Texas Hold'em GTO + LLM trainer — 5 distinct AI opponent personas with <code>&lt;think&gt;</code> reasoning extraction (including MiniMax truncation salvage), real-time GTO strategy advisor, live chip-equity line charts, hand-history replay, and tournament mode.
        </li>
      </ul>
    </td>
  </tr>
</table>

---

### 🛠️ Recent Engineering Ship Log (`2026.09` – `2026.10` Commit Highlights)

| Date | Repository | Stack | Verified Engineering Breakthrough &amp; Commit Evidence |
| :--- | :--- | :--- | :--- |
| **`2026.10.31`** | [**`garmin-miniapp`**](https://github.com/LCorleone/garmin-miniapp) | `Go` / `Python` | Shipped native **`mygo` desktop client** (3-tier router, OS keychain, 6 X-axis-aligned physiological charts with anomaly markers &amp; painter-level clipping) + incremental analysis cache rebuild (`8bda2a6`, `69f61f8`, `a9288e1`). |
| **`2026.10.29`** | [**`garmin-miniapp`**](https://github.com/LCorleone/garmin-miniapp) | `Python` | Implemented **6 sports-science physiology models** (HRV 60d rolling baseline &amp; SD bands, ACWR workload ratio, recovery attribution) + `--full-history` rate-limited backfill, resumable minute-level HR curves, and `garmin.cn` endpoint support (`26224de`, `793c1ec`, `66ad4f1`). |
| **`2026.10.28`** | [**`pi-subagents`**](https://github.com/LCorleone/pi-subagents) | `TypeScript` (`v0.83.1`) | Fixed **UTF-8 character-boundary truncation** in the async lane-board TUI (`#3097`) and enforced **project-trust verification** before ancestor discovery probes (`#3080`). |
| **`2026.10.17`** | [**`pi-wx-agent`**](https://github.com/LCorleone/pi-wx-agent) | `JavaScript` | Completed pre-1.0 hardening — **cross-session WeChat push**, owner-only extension tool visibility, extension disposal-race crash containment, and multi-user `/invite` family isolation (`694eac6`, `63288e0`, `4067997`, `2382d9e`). |
| **`2026.10.05`** | [**`magpie`**](https://github.com/LCorleone/magpie) | `Go` | Preserved **streaming `tool_use` inputs &amp; relay `tool_calls`** across `end_turn` boundaries, surfaced upstream protocol/stop-reason telemetry, and injected gateway proxy into plugin-spawned processes (`#910`, `#916`, `#918`). |
| **`2026.09.22`** | [**`one-api`**](https://github.com/LCorleone/one-api) | `Go` | Engineered **durable idempotent refund intent recovery**, deferred timed-out refunds without starving recovery, and isolated audio retry pipelines with native pricing reconciliation (`b0755aa`, `b2e2b4c`, `c8b2585`). |

---

### 🧰 Tech Stack &amp; Runtime Environment

<div align="center">

![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![Go](https://img.shields.io/badge/Go-00ADD8?style=for-the-badge&logo=go&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Rust](https://img.shields.io/badge/Rust-000000?style=for-the-badge&logo=rust&logoColor=white)
![C++](https://img.shields.io/badge/C++-00599C?style=for-the-badge&logo=c%2B%2B&logoColor=white)
![C#](https://img.shields.io/badge/C%23-512BD4?style=for-the-badge&logo=csharp&logoColor=white)
![React](https://img.shields.io/badge/React_19-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)
![Linux](https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Git](https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white)

</div>

---

### 📊 GitHub Pulse &amp; Contribution Telemetry

<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://github-pulse-topaz.vercel.app/u/LCorleone?theme=dracula" />
    <source media="(prefers-color-scheme: light)" srcset="https://github-pulse-topaz.vercel.app/u/LCorleone?theme=paper" />
    <img alt="GitHub Pulse" src="https://github-pulse-topaz.vercel.app/u/LCorleone?theme=dracula" />
  </picture>

  <br /><br />

  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/LCorleone/LCorleone/output/github-snake-dark.svg" />
    <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/LCorleone/LCorleone/output/github-snake.svg" />
    <img alt="github-snake" src="https://raw.githubusercontent.com/LCorleone/LCorleone/output/github-snake-dark.svg" width="100%" />
  </picture>
</div>
