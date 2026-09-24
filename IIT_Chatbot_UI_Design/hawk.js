/* Conversation state is volatile; no localStorage, cookies, or ticket API. */
(() => {
  "use strict";
  const $ = (id) => document.getElementById(id);
  let history = [], escalating = false, busy = false, pending = null, controller = null, epoch = 0;
  let draftNumber = 0;
  const greeting = "Hi, I'm Hawk. Try a fictional IT issue to test our conversation flow. My replies are placeholders for now. I can also prepare an email draft for you to review and send.";

  function message(role, text, sources = []) {
    const row = document.createElement("div");
    row.className = `message ${role}`;
    const bubble = document.createElement("div");
    bubble.className = "bubble";
    bubble.textContent = text;
    row.append(bubble);
    for (const source of sources) {
      // Never render arbitrary model output as HTML or executable links.
      try {
        const url = new URL(source.startsWith("https://") ? source : `https://${source}`);
        if (url.protocol !== "https:" || !url.hostname.includes(".")) continue;
        const link = document.createElement("a");
        link.className = "source";
        link.href = url.href;
        link.textContent = source;
        link.target = "_blank";
        link.rel = "noopener noreferrer";
        row.append(link);
      } catch { /* Ignore unusable source URLs. */ }
    }
    $("messages").append(row);
    scroll();
  }
  function scroll() { $("messages").scrollTop = $("messages").scrollHeight; }
  function controls() {
    for (const id of ["send", "message", "escalate"]) $(id).disabled = busy || pending !== null;
    for (const chip of document.querySelectorAll("[data-question]")) chip.disabled = busy || pending !== null;
    $("retry").disabled = busy;
    $("status").textContent = busy ? "Hawk is responding…" : "";
  }
  function emailCard(email) {
    const card = document.createElement("section");
    card.className = "email";
    const heading = document.createElement("h3");
    heading.textContent = "Your email draft";
    const note = document.createElement("p");
    note.textContent = "Test template. Review and edit before sending. Hawk has not sent this email.";
    const to = document.createElement("p");
    to.textContent = `To: ${email.to}`;
    const subject = document.createElement("p");
    subject.textContent = `Subject: ${email.subject}`;
    const label = document.createElement("label");
    const body = document.createElement("textarea");
    body.id = `email-body-${++draftNumber}`;
    body.value = email.body;
    label.htmlFor = body.id;
    label.textContent = "Review your message";
    const copy = document.createElement("button");
    copy.className = "copy";
    copy.textContent = "Copy email";
    const status = document.createElement("span");
    status.className = "copy-status";
    status.setAttribute("role", "status");
    copy.addEventListener("click", async () => {
      const text = `To: ${email.to}\nSubject: ${email.subject}\n\n${body.value}`;
      try {
        await navigator.clipboard.writeText(text);
        status.textContent = "Copied. Paste into your email app, review, and send.";
      } catch {
        body.focus(); body.select();
        status.textContent = "Clipboard unavailable. Copy the selected message and the To/Subject above manually.";
      }
    });
    card.append(heading, note, to, subject, label, body, copy, status);
    $("messages").append(card);
    scroll();
  }
  function validChat(data) {
    return typeof data.reply === "string" && Array.isArray(data.sources) && data.sources.every(s => typeof s === "string") &&
      typeof data.escalate === "boolean" && (data.escalate ? ["fixed_topic", "low_confidence", "user_request"].includes(data.escalation_reason) : data.escalation_reason === null);
  }
  function validEscalation(data) {
    return (data.email === null && typeof data.clarifying_question === "string" && data.clarifying_question.length > 0) ||
      (data.clarifying_question === null && data.email && ["to", "subject", "body"].every(key => typeof data.email[key] === "string"));
  }
  async function execute() {
    if (!pending || busy) return;
    const version = epoch;
    busy = true;
    $("error").hidden = true; $("retry").hidden = true; controls();
    controller = new AbortController();
    const timer = setTimeout(() => controller?.abort(), 15000);
    try {
      const path = pending;
      const response = await fetch(path, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ messages: history }), signal: controller.signal });
      const data = await response.json();
      if (version !== epoch) return;
      if (!response.ok) throw new Error(typeof data.detail === "string" ? data.detail : "Hawk could not respond. Please try again.");
      if (path === "/api/chat") {
        if (!validChat(data)) throw new Error("Hawk returned an unexpected reply. Please try again.");
        history.push({ role: "bot", text: data.reply });
        message("bot", data.reply, data.sources);
        pending = null;
        if (data.escalate) { escalating = true; pending = "/api/escalate"; }
      } else {
        if (!validEscalation(data)) throw new Error("Hawk returned an unexpected draft. Please try again.");
        if (data.clarifying_question) {
          history.push({ role: "bot", text: data.clarifying_question });
          message("bot", data.clarifying_question);
        } else emailCard(data.email);
        pending = null;
      }
    } catch (error) {
      if (version !== epoch) return;
      $("error").textContent = error.name === "AbortError" ? "Hawk took too long to respond. Try again or start a new chat." : (error instanceof TypeError ? "Cannot reach Hawk. Check that the local server is running, then try again." : error.message);
      $("error").hidden = false; $("retry").hidden = false;
    } finally {
      clearTimeout(timer);
      if (version === epoch) {
        busy = false; controller = null; controls();
        if (pending && $("error").hidden) execute();
        else if (!pending) $("message").focus();
      }
    }
  }
  function send(text) {
    text = text.trim();
    if (!text || busy || pending) return;
    // Leave room for the reply and an automatic escalation question.
    if (history.length >= 56 || history.reduce((n, m) => n + m.text.length, text.length) > 21000) {
      $("error").textContent = "This conversation is full. Copy any draft you need, then start a new chat.";
      $("error").hidden = false; return;
    }
    history.push({ role: "user", text });
    message("user", text);
    $("message").value = ""; $("chips").hidden = true;
    pending = escalating ? "/api/escalate" : "/api/chat";
    execute();
  }
  function reset() {
    epoch++; controller?.abort(); controller = null;
    history = []; escalating = false; pending = null; busy = false;
    $("messages").replaceChildren(); $("message").value = "";
    $("error").hidden = true; $("retry").hidden = true; $("chips").hidden = false;
    message("bot", greeting); controls(); $("message").focus();
  }
  function open(value) {
    $("chat").hidden = !value; $("launcher").hidden = value;
    $("launcher").setAttribute("aria-expanded", String(value));
    (value ? $("message") : $("launcher")).focus();
  }
  $("launcher").addEventListener("click", () => open(true));
  $("close").addEventListener("click", () => open(false));
  $("reset").addEventListener("click", reset);
  $("retry").addEventListener("click", execute);
  $("composer").addEventListener("submit", event => { event.preventDefault(); send($("message").value); });
  $("escalate").addEventListener("click", () => { if (busy || pending) return; escalating = true; $("chips").hidden = true; pending = "/api/escalate"; execute(); });
  document.querySelectorAll("[data-question]").forEach(button => button.addEventListener("click", () => send(button.dataset.question)));
  document.addEventListener("keydown", event => { if (event.key === "Escape" && !$("chat").hidden) open(false); });
  reset();
})();
