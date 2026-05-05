function loadQteSettings() {
  const stored = JSON.parse(localStorage.getItem("qteSettings") || "{}");
  const difficulty = stored.difficulty || "medium";
  const preset = stored.preset || "WASD";
  let keymap;
  if (preset === "CUSTOM" && stored.customKeys) {
    keymap = stored.customKeys;
  } else if (preset === "ARROWS") {
    keymap = { Up: "ArrowUp", Down: "ArrowDown", Left: "ArrowLeft", Right: "ArrowRight" };
  } else {
    keymap = { Up: "w", Down: "s", Left: "a", Right: "d" };
  }
  let duration;
  if (difficulty === "easy") duration = 1200;
  else if (difficulty === "hard") duration = 600;
  else duration = 900;
  return { difficulty, keymap, duration };
}

const qteSettings = loadQteSettings();
const DIRECTIONS = ["Up","Down","Left","Right"];

let qteSequence = [];
let qteIndex = 0;
let qteActive = false;
let qteStartTime = 0;
let qteDuration = qteSettings.duration;
let qteTimerId = null;
let qteScore = 0;
let qteHits = 0;
let qteMisses = 0;
let qteCombo = 0;
let qteMaxCombo = 0;

const sHit = new Audio();
const sMiss = new Audio();

document.getElementById("qte-hint").textContent =
  `Press: ${Object.entries(qteSettings.keymap).map(([dir,key]) => `${dir}=${key}`).join("  ")}`;

document.getElementById("start-qte").addEventListener("click", () => {
  startQTE();
});

function startQTE() {
  qteSequence = Array.from({length: 10}, () => DIRECTIONS[Math.floor(Math.random()*DIRECTIONS.length)]);
  qteIndex = 0;
  qteActive = true;
  qteScore = 0;
  qteHits = 0;
  qteMisses = 0;
  qteCombo = 0;
  qteMaxCombo = 0;

  updateQteScoreDisplay();
  renderQTEWindow();
  startPromptTimer();
}

function renderQTEWindow() {
  const container = document.getElementById("qte-container");
  container.innerHTML = "";

  const windowSize = 3;
  for (let i = 0; i < windowSize + 1; i++) {
    const idx = qteIndex + i;
    if (idx >= qteSequence.length) break;
    const div = document.createElement("div");
    div.classList.add("qte-prompt");
    if (i === 0) div.classList.add("active-prompt");
    div.textContent = qteSequence[idx];
    container.appendChild(div);
  }
}

function startPromptTimer() {
  qteStartTime = performance.now();
  const bar = document.getElementById("qte-bar");
  bar.style.width = "100%";

  if (qteTimerId) cancelAnimationFrame(qteTimerId);
  const step = () => {
    if (!qteActive) return;
    const elapsed = performance.now() - qteStartTime;
    const ratio = 1 - elapsed / qteDuration;
    bar.style.width = Math.max(0, ratio * 100) + "%";
    if (elapsed >= qteDuration) {
      registerMiss();
      nextPromptOrFinish();
    } else {
      qteTimerId = requestAnimationFrame(step);
    }
  };
  qteTimerId = requestAnimationFrame(step);
}

document.addEventListener("keydown", (e) => {
  if (!qteActive) return;
  const currentPrompt = qteSequence[qteIndex];
  const expectedKey = qteSettings.keymap[currentPrompt];

  const elapsed = performance.now() - qteStartTime;
  if (elapsed > qteDuration) return;

  if (e.key === expectedKey) {
    registerHit(elapsed);
    nextPromptOrFinish();
  }
});

function registerHit(elapsed) {
  if (sHit) { try { sHit.currentTime = 0; sHit.play(); } catch(e){} }
  qteHits++;
  qteCombo++;
  if (qteCombo > qteMaxCombo) qteMaxCombo = qteCombo;

  const errorRatio = Math.abs(elapsed - qteDuration / 2) / (qteDuration / 2);
  let points = 0;
  if (errorRatio < 0.2) points = 100;
  else if (errorRatio < 0.5) points = 70;
  else points = 40;
  qteScore += points;
  updateQteScoreDisplay();
}

function registerMiss() {
  if (sMiss) { try { sMiss.currentTime = 0; sMiss.play(); } catch(e){} }
  qteMisses++;
  qteCombo = 0;
  updateQteScoreDisplay();
}

function nextPromptOrFinish() {
  qteIndex++;
  if (qteIndex >= qteSequence.length) {
    qteActive = false;
  } else {
    renderQTEWindow();
    startPromptTimer();
  }
}

function updateQteScoreDisplay() {
  const total = qteHits + qteMisses;
  const acc = total === 0 ? 0 : Math.round((qteHits / total) * 100);
  document.getElementById("qte-score-value").textContent = qteScore;
  document.getElementById("qte-combo").textContent = qteCombo;
  document.getElementById("qte-max-combo").textContent = qteMaxCombo;
  document.getElementById("qte-accuracy").textContent = acc;
}
