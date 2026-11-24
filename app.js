/* ===================================================================
   देविश्री ✦ चेतन — INVITEVIBES "BLUSH & GOLD" INTERACTIVE ENGINE
   Entry Video Envelope Gate, Flute Audio, Falling Blush/Gold Petals,
   Interactive Scratch Cards + Confetti, Stacking Polaroids & Timeline
   =================================================================== */

(function () {
  'use strict';

  // -------------------------------------------------------------------
  // 1. STABLE MOBILE VIEWPORT HEIGHT LOCK
  // -------------------------------------------------------------------
  let lastWidth = -1;
  function captureStableViewport() {
    const h = window.innerHeight;
    const w = window.innerWidth;
    const root = document.documentElement;
    root.style.setProperty('--stable-vh', h + 'px');
    root.style.setProperty('--stable-vw', w + 'px');
    lastWidth = w;
  }
  captureStableViewport();
  window.addEventListener('resize', () => {
    if (Math.abs(window.innerWidth - lastWidth) > 10) {
      captureStableViewport();
    }
  }, { passive: true });
  window.addEventListener('orientationchange', () => {
    setTimeout(captureStableViewport, 250);
  });

  // -------------------------------------------------------------------
  // 2. BACKGROUND FLUTE AUDIO CONTROLLER (#bg-flute-audio & #audio-btn)
  // -------------------------------------------------------------------
  const audioEl = document.getElementById('bg-flute-audio');
  const audioBtn = document.getElementById('audio-btn');
  const iconUnmuted = document.getElementById('icon-unmuted');
  const iconMuted = document.getElementById('icon-muted');
  let isAudioPlaying = false;
  const TARGET_VOLUME = 0.52;

  function updateAudioIcon(playing) {
    isAudioPlaying = playing;
    if (iconUnmuted && iconMuted) {
      iconUnmuted.style.display = playing ? 'block' : 'none';
      iconMuted.style.display = playing ? 'none' : 'block';
    }
  }

  function startFluteMusicWithFade() {
    if (!audioEl) return;
    audioEl.volume = 0;
    audioEl.play().then(() => {
      updateAudioIcon(true);
      let step = 0;
      const timer = setInterval(() => {
        step++;
        audioEl.volume = Math.min(TARGET_VOLUME, (TARGET_VOLUME / 10) * step);
        if (step >= 10) clearInterval(timer);
      }, 45);
    }).catch(() => {
      updateAudioIcon(false);
    });
  }

  if (audioBtn && audioEl) {
    audioBtn.addEventListener('click', () => {
      if (isAudioPlaying && !audioEl.paused) {
        audioEl.pause();
        updateAudioIcon(false);
      } else {
        audioEl.volume = TARGET_VOLUME;
        audioEl.play().then(() => updateAudioIcon(true)).catch(() => {});
      }
    });
  }

  // -------------------------------------------------------------------
  // 3. SOFT FALLING BLUSH & GOLD PETALS ENGINE (#petals-canvas)
  // -------------------------------------------------------------------
  const petalsCanvas = document.getElementById('petals-canvas');
  let petalsActive = false;

  function startFallingPetals() {
    if (petalsActive || !petalsCanvas) return;
    petalsActive = true;
    petalsCanvas.classList.add('active');
    const ctx = petalsCanvas.getContext('2d');

    function resize() {
      petalsCanvas.width = window.innerWidth;
      petalsCanvas.height = window.innerHeight;
    }
    resize();
    window.addEventListener('resize', resize, { passive: true });

    const palette = ['#F7DCDA', '#EAC9C7', '#E2B4B1', '#FFFFFF', '#F7EFC8'];
    const count = window.innerWidth < 600 ? 15 : 26;
    const petals = [];

    for (let i = 0; i < count; i++) {
      petals.push({
        x: Math.random() * petalsCanvas.width,
        y: Math.random() * petalsCanvas.height * 2 - petalsCanvas.height,
        r: 4.5 + Math.random() * 5.5,
        vx: (Math.random() - 0.5) * 0.8,
        vy: 0.65 + Math.random() * 1.15,
        rot: Math.random() * Math.PI * 2,
        drot: (Math.random() - 0.5) * 0.04,
        color: palette[Math.floor(Math.random() * palette.length)],
        alpha: 0.35 + Math.random() * 0.42
      });
    }

    function animatePetals() {
      ctx.clearRect(0, 0, petalsCanvas.width, petalsCanvas.height);
      petals.forEach((p) => {
        p.x += p.vx + 0.4 * Math.sin(0.01 * p.y);
        p.y += p.vy;
        p.rot += p.drot;
        if (p.y > petalsCanvas.height + 20) {
          p.y = -20;
          p.x = Math.random() * petalsCanvas.width;
        }
        ctx.save();
        ctx.translate(p.x, p.y);
        ctx.rotate(p.rot);
        ctx.globalAlpha = p.alpha;
        ctx.fillStyle = p.color;
        ctx.beginPath();
        ctx.ellipse(0, 0, p.r * 0.56, p.r, 0, 0, Math.PI * 2);
        ctx.fill();
        ctx.restore();
      });
      requestAnimationFrame(animatePetals);
    }
    requestAnimationFrame(animatePetals);
  }

  // -------------------------------------------------------------------
  // 4. CELEBRATION CONFETTI BURST ENGINE (#confetti-canvas)
  // -------------------------------------------------------------------
  const confettiCanvas = document.getElementById('confetti-canvas');
  const confettiParticles = [];
  let confettiRunning = false;

  function fireConfettiBurst(originXRatio = 0.5, originYRatio = 0.6, count = 90) {
    if (!confettiCanvas) return;
    confettiCanvas.width = window.innerWidth;
    confettiCanvas.height = window.innerHeight;
    const colors = ['#E2B4B1', '#FDFBF7', '#D4AF37', '#BA7A76', '#E8CE73', '#8A4F4C'];
    const ox = confettiCanvas.width * originXRatio;
    const oy = confettiCanvas.height * originYRatio;

    for (let i = 0; i < count; i++) {
      const angle = -Math.PI * 0.5 + (Math.random() - 0.5) * 1.9;
      const speed = 5 + Math.random() * 11;
      confettiParticles.push({
        x: ox,
        y: oy,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed - 2,
        w: 6 + Math.random() * 6,
        h: 4 + Math.random() * 5,
        rot: Math.random() * Math.PI * 2,
        vrot: (Math.random() - 0.5) * 0.2,
        color: colors[i % colors.length],
        alpha: 1.0
      });
    }

    if (!confettiRunning) {
      confettiRunning = true;
      const cCtx = confettiCanvas.getContext('2d');
      function stepConfetti() {
        cCtx.clearRect(0, 0, confettiCanvas.width, confettiCanvas.height);
        for (let i = confettiParticles.length - 1; i >= 0; i--) {
          const p = confettiParticles[i];
          p.x += p.vx;
          p.y += p.vy;
          p.vy += 0.24;
          p.vx *= 0.99;
          p.rot += p.vrot;
          p.alpha -= 0.011;
          if (p.alpha <= 0.01 || p.y > confettiCanvas.height + 30) {
            confettiParticles.splice(i, 1);
            continue;
          }
          cCtx.save();
          cCtx.translate(p.x, p.y);
          cCtx.rotate(p.rot);
          cCtx.globalAlpha = Math.max(0, p.alpha);
          cCtx.fillStyle = p.color;
          cCtx.fillRect(-p.w * 0.5, -p.h * 0.5, p.w, p.h);
          cCtx.restore();
        }
        if (confettiParticles.length > 0) {
          requestAnimationFrame(stepConfetti);
        } else {
          confettiRunning = false;
        }
      }
      requestAnimationFrame(stepConfetti);
    }
  }

  // -------------------------------------------------------------------
  // 5. ENTRY VIDEO ENVELOPE GATE (#entry-gate & #entry-video)
  // -------------------------------------------------------------------
  const entryGate = document.getElementById('entry-gate');
  const entryVideo = document.getElementById('entry-video');
  const entryTapHint = document.getElementById('entry-tap-hint');
  const entryWelcomeMsg = document.getElementById('entry-welcome-msg');
  const mainContent = document.getElementById('main-content');
  let gatePlaying = false;
  let gateCompleted = false;

  if (entryVideo) {
    entryVideo.addEventListener('loadeddata', () => {
      if (entryVideo.currentTime === 0) {
        try { entryVideo.currentTime = 0.001; } catch (e) {}
      }
    });
  }

  let revealObserver = null;
  function observeReveals() {
    const reveals = document.querySelectorAll('.reveal:not(.revealed)');
    if ('IntersectionObserver' in window) {
      if (!revealObserver) {
        revealObserver = new IntersectionObserver((entries) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              entry.target.classList.add('revealed');
              revealObserver.unobserve(entry.target);
            }
          });
        }, { threshold: 0.06, rootMargin: '0px 0px -20px 0px' });
      }
      reveals.forEach((el) => revealObserver.observe(el));
    } else {
      reveals.forEach((el) => el.classList.add('revealed'));
    }
  }

  function completeGateAndRevealInvitation() {
    if (gateCompleted) return;
    gateCompleted = true;

    if (entryGate) {
      entryGate.classList.add('fade-out');
      setTimeout(() => {
        entryGate.style.display = 'none';
      }, 850);
    }

    if (mainContent) {
      mainContent.classList.add('visible');
    }
    if (audioBtn) {
      audioBtn.classList.add('visible');
    }
    document.body.style.overflow = 'auto';
    startFallingPetals();
    observeReveals();
    setTimeout(initAllScratchSurfaces, 60);
  }

  function handleEntryGateClick() {
    if (gatePlaying) return;
    gatePlaying = true;
    if (entryGate) entryGate.classList.add('video-playing');
    if (entryTapHint) entryTapHint.classList.add('hidden');

    // Start romantic flute music immediately on user gesture
    startFluteMusicWithFade();

    if (entryVideo) {
      entryVideo.currentTime = 0;
      entryVideo.muted = true;
      entryVideo.play().catch(() => {
        completeGateAndRevealInvitation();
      });

      setTimeout(() => {
        if (entryWelcomeMsg) entryWelcomeMsg.classList.add('hidden');
      }, 3200);

      entryVideo.addEventListener('timeupdate', () => {
        const dur = entryVideo.duration;
        if (Number.isFinite(dur) && dur > 1.5 && entryVideo.currentTime >= dur - 0.9) {
          try { entryVideo.pause(); } catch (e) {}
          completeGateAndRevealInvitation();
        }
      });

      entryVideo.addEventListener('ended', completeGateAndRevealInvitation);
      // Fallback timeout in case video ends or stalls
      setTimeout(completeGateAndRevealInvitation, 5200);
    } else {
      completeGateAndRevealInvitation();
    }
  }

  if (entryGate) {
    document.body.style.overflow = 'hidden';
    entryGate.addEventListener('click', handleEntryGateClick);
    entryGate.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        handleEntryGateClick();
      }
    });
  }

  const heroScrollBtn = document.getElementById('hero-scroll-btn');
  if (heroScrollBtn) {
    heroScrollBtn.addEventListener('click', () => {
      document.getElementById('scratch-section')?.scrollIntoView({ behavior: 'smooth' });
    });
  }

  // -------------------------------------------------------------------
  // 6. INTERACTIVE SCRATCH-TO-REVEAL DATE CARDS ([data-scratch-card])
  //    + TAP-TO-REVEAL ON MOBILE + SCROLL GATE UNTIL ALL 3 REVEALED
  // -------------------------------------------------------------------
  const scratchCards = document.querySelectorAll('[data-scratch-card]');
  const scratchInstructionEl = document.getElementById('scratch-instruction');
  const scratchGateNotice = document.getElementById('scratch-gate-notice');
  const scratchGateIcon = document.getElementById('scratch-gate-icon');
  const scratchGateText = document.getElementById('scratch-gate-text');
  let completedScratchCount = 0;
  let allScratchCelebrated = false;
  const scratchInitFns = [];

  function initAllScratchSurfaces() {
    scratchInitFns.forEach((fn) => fn());
  }

  function highlightUnrevealedScratchCards() {
    scratchCards.forEach((card) => {
      if (!card.classList.contains('glow')) {
        card.classList.remove('attention-pulse');
        void card.offsetWidth;
        card.classList.add('attention-pulse');
      }
    });
  }

  function unlockRestOfInvitation() {
    document.body.classList.add('date-unlocked');
    if (scratchInstructionEl) {
      scratchInstructionEl.innerHTML =
        '<span class="scratch-instruction-icon">✨</span>' +
        '<span>Wedding Date Revealed: 05 December 2026</span>' +
        '<span class="scratch-instruction-icon">✨</span>';
    }
    if (scratchGateNotice) {
      scratchGateNotice.classList.add('unlocked');
    }
    if (scratchGateIcon) {
      scratchGateIcon.textContent = '✨';
    }
    if (scratchGateText) {
      scratchGateText.textContent = 'Date Revealed! Tap here or scroll down to continue ↓';
    }
    setTimeout(() => {
      observeReveals();
      onStoryScroll();
      updateTimelineFlowerPosition();
    }, 60);
  }

  if (scratchGateNotice) {
    scratchGateNotice.addEventListener('click', () => {
      if (allScratchCelebrated) {
        document.getElementById('countdown-section')?.scrollIntoView({ behavior: 'smooth' });
      } else {
        highlightUnrevealedScratchCards();
      }
    });
  }

  let lastAttentionPulseAt = 0;
  function maybePulseLockedScratchOnScrollAttempt(deltaY) {
    if (allScratchCelebrated || !gateCompleted || deltaY <= 10) return;
    const scratchSec = document.getElementById('scratch-section');
    if (!scratchSec) return;
    const rect = scratchSec.getBoundingClientRect();
    if (rect.bottom <= window.innerHeight + 40) {
      const now = Date.now();
      if (now - lastAttentionPulseAt > 900) {
        lastAttentionPulseAt = now;
        highlightUnrevealedScratchCards();
      }
    }
  }

  window.addEventListener('wheel', (e) => {
    maybePulseLockedScratchOnScrollAttempt(e.deltaY);
  }, { passive: true });

  let pageTouchStartY = 0;
  window.addEventListener('touchstart', (e) => {
    if (e.touches && e.touches[0]) {
      pageTouchStartY = e.touches[0].clientY;
    }
  }, { passive: true });

  window.addEventListener('touchmove', (e) => {
    if (!allScratchCelebrated && e.touches && e.touches[0]) {
      const dy = pageTouchStartY - e.touches[0].clientY;
      maybePulseLockedScratchOnScrollAttempt(dy);
    }
  }, { passive: true });

  scratchCards.forEach((cardEl) => {
    const canvas = cardEl.querySelector('.scratch-canvas');
    const unitEl = cardEl.closest('.scratch-unit');
    const hintEl = unitEl?.querySelector('.scratch-hint');
    if (!canvas) return;

    const ctx = canvas.getContext('2d', { willReadFrequently: true });
    let isDrawing = false;
    let isCleared = false;
    let initialized = false;
    let touchStartX = 0;
    let touchStartY = 0;
    let touchMoved = false;

    function initScratchSurface() {
      if (initialized || isCleared) return;
      const rect = cardEl.getBoundingClientRect();
      const w = rect.width || cardEl.clientWidth || 110;
      const h = rect.height || cardEl.clientHeight || 150;
      if (w < 20 || h < 20) return;
      const dpr = window.devicePixelRatio || 1;
      canvas.width = w * dpr;
      canvas.height = h * dpr;
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.scale(dpr, dpr);

      const grad = ctx.createLinearGradient(0, 0, w, h);
      grad.addColorStop(0, '#E8C5B0');
      grad.addColorStop(0.35, '#C88A85');
      grad.addColorStop(0.65, '#D4AF37');
      grad.addColorStop(1, '#BA7A76');
      ctx.globalCompositeOperation = 'source-over';
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, w, h);

      // Highlighted inner border on the scratch foil
      ctx.strokeStyle = 'rgba(255, 249, 248, 0.72)';
      ctx.lineWidth = 1.5;
      ctx.strokeRect(7, 7, w - 14, h - 14);

      // Clear sparkle + TAP prompt on foil so mobile users know to tap/scratch
      ctx.fillStyle = '#FFFDF9';
      ctx.font = '700 18px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText('✦', w * 0.5, h * 0.44);

      ctx.font = '700 11px sans-serif';
      ctx.fillText('TAP / SCRATCH', w * 0.5, h * 0.62);

      ctx.globalCompositeOperation = 'destination-out';
      ctx.lineJoin = 'round';
      ctx.lineCap = 'round';
      ctx.lineWidth = Math.max(40, w * 0.38);
      initialized = true;
    }

    scratchInitFns.push(initScratchSurface);
    setTimeout(initScratchSurface, 220);

    function markCardCleared() {
      if (isCleared) return;
      isCleared = true;
      canvas.style.transition = 'opacity 0.4s ease';
      canvas.style.opacity = '0';
      setTimeout(() => { canvas.style.display = 'none'; }, 400);
      cardEl.classList.remove('attention-pulse');
      cardEl.classList.add('glow');
      if (hintEl) {
        hintEl.textContent = '✓ Revealed';
        hintEl.classList.add('revealed-hint');
      }

      completedScratchCount++;
      if (completedScratchCount < scratchCards.length && scratchGateText) {
        const remaining = scratchCards.length - completedScratchCount;
        scratchGateText.textContent =
          remaining === 1
            ? '1 card left! Tap the remaining card to unlock the invitation'
            : remaining + ' cards left! Tap the remaining cards to unlock the invitation';
      }

      if (completedScratchCount >= scratchCards.length && !allScratchCelebrated) {
        allScratchCelebrated = true;
        unlockRestOfInvitation();
        fireConfettiBurst(0.5, 0.62, 110);
        setTimeout(() => fireConfettiBurst(0.2, 0.68, 70), 320);
        setTimeout(() => fireConfettiBurst(0.8, 0.68, 70), 540);
      }
    }

    function revealByTap() {
      initScratchSurface();
      if (isCleared) return;
      const rect = cardEl.getBoundingClientRect();
      const w = rect.width || 110;
      const h = rect.height || 150;
      ctx.globalCompositeOperation = 'destination-out';
      ctx.beginPath();
      ctx.arc(w * 0.5, h * 0.5, Math.max(w, h) * 0.65, 0, Math.PI * 2);
      ctx.fill();
      markCardCleared();
    }

    function getLocalPos(e) {
      const rect = canvas.getBoundingClientRect();
      const touch = (e.touches && e.touches[0]) || (e.changedTouches && e.changedTouches[0]);
      const clientX = touch ? touch.clientX : e.clientX;
      const clientY = touch ? touch.clientY : e.clientY;
      return { x: clientX - rect.left, y: clientY - rect.top };
    }

    function checkScratchProgress() {
      if (isCleared) return;
      try {
        const imgData = ctx.getImageData(0, 0, canvas.width, canvas.height).data;
        let transparentPixels = 0;
        for (let i = 3; i < imgData.length; i += 16) {
          if (imgData[i] === 0) transparentPixels++;
        }
        const totalSampled = imgData.length / 16;
        if (transparentPixels / totalSampled > 0.16) {
          markCardCleared();
        }
      } catch (err) {
        markCardCleared();
      }
    }

    function scratchMove(e) {
      if (!isDrawing || isCleared) return;
      const pos = getLocalPos(e);
      if (e.type.startsWith('touch')) {
        const dx = Math.abs(pos.x - touchStartX);
        const dy = Math.abs(pos.y - touchStartY);
        if (dx > 6 || dy > 6) {
          touchMoved = true;
        }
        if (e.cancelable) e.preventDefault();
      }
      ctx.lineTo(pos.x, pos.y);
      ctx.stroke();
      ctx.beginPath();
      ctx.moveTo(pos.x, pos.y);
      checkScratchProgress();
    }

    function scratchStart(e) {
      initScratchSurface();
      if (isCleared) return;
      isDrawing = true;
      touchMoved = false;
      const pos = getLocalPos(e);
      touchStartX = pos.x;
      touchStartY = pos.y;
      ctx.beginPath();
      ctx.moveTo(pos.x, pos.y);
      ctx.lineTo(pos.x + 1, pos.y + 1);
      ctx.stroke();
    }

    function scratchEnd(e) {
      if (!isDrawing && !e.type.startsWith('touch')) return;
      isDrawing = false;
      if (!isCleared) {
        // On mobile touch or quick tap, reveal immediately on tap or after any scratch gesture
        if (e.type === 'touchend' && !touchMoved) {
          revealByTap();
        } else {
          checkScratchProgress();
          if (!isCleared && touchMoved) {
            revealByTap();
          }
        }
      }
    }

    canvas.addEventListener('mousedown', scratchStart);
    canvas.addEventListener('touchstart', scratchStart, { passive: true });
    window.addEventListener('mouseup', scratchEnd);
    canvas.addEventListener('touchend', scratchEnd);
    canvas.addEventListener('mousemove', scratchMove);
    canvas.addEventListener('touchmove', scratchMove, { passive: false });

    cardEl.addEventListener('click', () => {
      if (!isCleared) {
        revealByTap();
      }
    });

    cardEl.addEventListener('keydown', (e) => {
      if ((e.key === 'Enter' || e.key === ' ') && !isCleared) {
        e.preventDefault();
        revealByTap();
      }
    });

    if (unitEl) {
      unitEl.addEventListener('click', () => {
        if (!isCleared) {
          revealByTap();
        }
      });
    }
  });

  // -------------------------------------------------------------------
  // 7. LIVE COUNTDOWN (05/12/2026 12:35 PM)
  // -------------------------------------------------------------------
  function formatTwoDigits(num) {
    return String(Math.max(0, num)).padStart(2, '0');
  }

  const targetTime = new Date('2026-12-05T12:35:00+05:30').getTime();
  const cdDays = document.getElementById('cd-days');
  const cdHours = document.getElementById('cd-hours');
  const cdMins = document.getElementById('cd-mins');
  const cdSecs = document.getElementById('cd-secs');

  function updateCountdown() {
    const diff = Math.max(0, targetTime - Date.now());
    const d = Math.floor(diff / 86400000);
    const h = Math.floor((diff % 86400000) / 3600000);
    const m = Math.floor((diff % 3600000) / 60000);
    const s = Math.floor((diff % 60000) / 1000);

    if (cdDays) cdDays.textContent = formatTwoDigits(d);
    if (cdHours) cdHours.textContent = formatTwoDigits(h);
    if (cdMins) cdMins.textContent = formatTwoDigits(m);
    if (cdSecs) cdSecs.textContent = formatTwoDigits(s);
  }
  updateCountdown();
  setInterval(updateCountdown, 1000);

  // -------------------------------------------------------------------
  // 8. SCROLL-DRIVEN STACKING POLAROID GALLERY (#story-section)
  // -------------------------------------------------------------------
  const storySection = document.getElementById('story-section');
  const polaroidCards = Array.from(document.querySelectorAll('#polaroid-stack .ls-card'));
  const polaroidDots = Array.from(document.querySelectorAll('#polaroid-dots .ls-progress-dot'));
  const chapterEl = document.getElementById('polaroid-chapter');
  const descEl = document.getElementById('polaroid-desc');
  let activePolaroidIndex = 0;

  function setPolaroidIndex(idx) {
    const clamped = Math.max(0, Math.min(polaroidCards.length - 1, idx));
    if (clamped === activePolaroidIndex && polaroidCards[0].classList.contains('visible')) return;
    activePolaroidIndex = clamped;

    polaroidCards.forEach((card, i) => {
      card.classList.remove('visible', 'stacked');
      card.style.removeProperty('--d');
      if (i < clamped) {
        card.classList.add('stacked');
        card.style.setProperty('--d', String(clamped - i));
      } else if (i === clamped) {
        card.classList.add('visible');
      }
    });

    polaroidDots.forEach((dot, i) => {
      dot.classList.toggle('active', i === clamped);
      dot.classList.toggle('past', i < clamped);
    });

    const activeCard = polaroidCards[clamped];
    if (activeCard && chapterEl && descEl) {
      chapterEl.textContent = activeCard.getAttribute('data-chapter') || '';
      descEl.textContent = activeCard.getAttribute('data-desc') || '';
    }
  }

  function onStoryScroll() {
    if (!storySection || polaroidCards.length <= 1) return;
    const rect = storySection.getBoundingClientRect();
    const vh = window.innerHeight;
    const scrollable = Math.max(1, storySection.offsetHeight - vh);
    const progress = Math.max(0, Math.min(1, -rect.top / scrollable));
    const idx = Math.round(progress * (polaroidCards.length - 1));
    setPolaroidIndex(idx);
  }

  window.addEventListener('scroll', onStoryScroll, { passive: true });

  polaroidDots.forEach((dot, i) => {
    dot.style.cursor = 'pointer';
    dot.addEventListener('click', () => setPolaroidIndex(i));
  });

  const polaroidStack = document.getElementById('polaroid-stack');
  if (polaroidStack && polaroidCards.length > 1) {
    polaroidStack.style.cursor = 'pointer';
    polaroidStack.addEventListener('click', () => {
      setPolaroidIndex((activePolaroidIndex + 1) % polaroidCards.length);
    });
  }

  // -------------------------------------------------------------------
  // 9. SCROLL-DRIVEN SPINNING LOTUS ON TIMELINE SPINE (#timeline-wrap)
  // -------------------------------------------------------------------
  const timelineWrap = document.getElementById('timeline-wrap');
  const timelineFlower = document.getElementById('timeline-flower');

  function updateTimelineFlowerPosition() {
    if (!timelineWrap || !timelineFlower) return;
    const rect = timelineWrap.getBoundingClientRect();
    const totalH = timelineWrap.offsetHeight || rect.height || 1;
    let pos = window.innerHeight * 0.45 - rect.top;
    pos = Math.max(0, Math.min(totalH, pos));
    timelineFlower.style.top = pos + 'px';
  }

  window.addEventListener('scroll', updateTimelineFlowerPosition, { passive: true });
  window.addEventListener('resize', updateTimelineFlowerPosition, { passive: true });
  updateTimelineFlowerPosition();
})();
