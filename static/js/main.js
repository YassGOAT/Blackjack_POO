document.addEventListener("DOMContentLoaded", () => {
    // --- RÉFÉRENCES AUDIO ---
    const clickSfx = document.getElementById("sfx-click");
    const cardSfx  = document.getElementById("sfx-card");
    const winSfx   = document.getElementById("sfx-win");
    const loseSfx  = document.getElementById("sfx-lose");
    const bgMusic  = document.getElementById("music-bg");

    const audioMap = {
        click: clickSfx,
        card:  cardSfx,
        win:   winSfx,
        lose:  loseSfx,
        bg:    bgMusic,
    };

    const defaultVolumes = {
        click: 0.4,
        card:  0.4,
        win:   0.45,
        lose:  0.45,
        bg:    0.2,
    };

    // --- SETTINGS LOCALSTORAGE ---
    const SETTINGS_KEY = "bj_audio_settings";

    const loadSettings = () => {
        try {
            const raw = localStorage.getItem(SETTINGS_KEY);
            if (!raw) {
                return {
                    masterMuted: false,
                    volumes: { ...defaultVolumes },
                };
            }
            const parsed = JSON.parse(raw);
            return {
                masterMuted: !!parsed.masterMuted,
                volumes: { ...defaultVolumes, ...(parsed.volumes || {}) },
            };
        } catch {
            return {
                masterMuted: false,
                volumes: { ...defaultVolumes },
            };
        }
    };

    const saveSettings = (settings) => {
        try {
            localStorage.setItem(SETTINGS_KEY, JSON.stringify(settings));
        } catch {
            // ignore
        }
    };

    let audioSettings = loadSettings();

    const applyAudioSettings = () => {
        Object.entries(audioMap).forEach(([key, audio]) => {
            if (!audio) return;
            const vol = audioSettings.volumes[key] ?? defaultVolumes[key] ?? 0.3;
            audio.volume = Math.min(Math.max(vol, 0), 1);
            audio.muted  = !!audioSettings.masterMuted;
        });
    };

    applyAudioSettings();

    const playSafe = (audioEl) => {
        if (!audioEl || audioSettings.masterMuted) return;
        try {
            audioEl.currentTime = 0;
            audioEl.play().catch(() => {});
        } catch {
            // autoplay bloqué → pas grave
        }
    };

    // --- MUSIQUE DE FOND : on ESSAIE dès le chargement ---
    if (bgMusic && !audioSettings.masterMuted) {
        playSafe(bgMusic);
    }

    // Et on retente au premier clic utilisateur si besoin
    let bgStarted = false;
    const startBgMusic = () => {
        if (!bgStarted && bgMusic && !audioSettings.masterMuted) {
            playSafe(bgMusic);
            bgStarted = true;
        }
    };

    // --- SONS DE RÉSULTAT (win/lose) ---
    const body = document.body;
    const resultRaw = (body.dataset.result || "").toLowerCase().trim();

    // petit délai pour laisser le DOM se poser
    if (resultRaw && !audioSettings.masterMuted) {
        setTimeout(() => {
            if (resultRaw === "victoire") {
                playSafe(winSfx);
            } else if (resultRaw === "défaite" || resultRaw === "defaite") {
                playSafe(loseSfx);
            }
        }, 150);
    }

    // --- SONS SUR LES BOUTONS (click/card) ---
    const buttons = document.querySelectorAll(".btn");
    buttons.forEach((btn) => {
        btn.addEventListener("click", () => {
            startBgMusic();
            const soundType = (btn.dataset.sound || "click").toLowerCase();
            if (soundType === "card") {
                playSafe(cardSfx);
            } else {
                playSafe(clickSfx);
            }
        });
    });

    // --- ACTIVATION DU BOUTON "Commencer une partie" SELON LA MISE ---
    const betInput  = document.getElementById("bet");
    const startBtn  = document.getElementById("start-btn");

    if (betInput && startBtn) {
        const updateStartBtn = () => {
            const value = parseInt(betInput.value || "0", 10);
            const max   = parseInt(betInput.max || "999999", 10);

            if (!isNaN(value) && value > 0 && value <= max) {
                startBtn.disabled = false;
            } else {
                startBtn.disabled = true;
            }
        };

        betInput.addEventListener("input", updateStartBtn);
        updateStartBtn();
    }

    // --- PARAMÈTRES AUDIO (mute + sliders) ---
    const settingsToggle = document.querySelector(".settings-toggle");
    const settingsPanel  = document.querySelector(".settings-panel");
    const muteCheckbox   = document.getElementById("audio-mute");
    const sliders        = document.querySelectorAll(".audio-volume-slider");

    if (settingsPanel && settingsToggle) {
        settingsToggle.addEventListener("click", () => {
            settingsPanel.classList.toggle("hidden");
        });
    }

    if (muteCheckbox) {
        muteCheckbox.checked = !!audioSettings.masterMuted;
        muteCheckbox.addEventListener("change", () => {
            audioSettings.masterMuted = muteCheckbox.checked;
            applyAudioSettings();
            saveSettings(audioSettings);
        });
    }

    sliders.forEach((slider) => {
        const key = slider.dataset.soundKey;
        if (!key) return;
        const vol = audioSettings.volumes[key] ?? defaultVolumes[key] ?? 0.3;
        slider.value = Math.round(vol * 100);

        slider.addEventListener("input", () => {
            let v = parseInt(slider.value || "0", 10);
            if (isNaN(v)) v = 0;
            v = Math.min(Math.max(v, 0), 100);
            audioSettings.volumes[key] = v / 100;
            applyAudioSettings();
            saveSettings(audioSettings);
        });
    });
});
