async function runExperiment() {
    const instr = CONFIG.instructions;
    const container = document.getElementById('container');

    function showScreen(text) {
        return new Promise(resolve => {
            const html = text
                .split('\n')
                .map(line => `<p>${line}</p>`)
                .join('');
            container.innerHTML = `<div class="screen"><div>${html}</div></div>`;
            window.scrollTo(0, 0);
            function onKey(e) {
                if (e.key === ' ' || e.key === 'Enter') {
                    document.removeEventListener('keydown', onKey);
                    resolve();
                }
            }
            document.addEventListener('keydown', onKey);
        });
    }

    function sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    function convertDelayToStr(delay) {
        const tblConv = {
            0: 'Now',
            0.43: '3 days later',
            0.714: '5 days later',
            1: '1 week later',
            2: '2 weeks later',
            3: '3 weeks later',
            4.3: '1 month later',
            6.44: '6 weeks later',
            8.6: '2 months later',
            10.8: '10 weeks later',
            12.9: '3 months later',
            17.2: '4 months later',
            21.5: '5 months later',
            26: '6 months later',
            52: '1 year later',
            104: '2 years later',
            156: '3 years later',
            260: '5 years later',
            520: '10 years later'
        };
        let mv = null, ms = null;
        for (const [v, s] of Object.entries(tblConv)) {
            const numV = parseFloat(v);
            if (mv === null || Math.pow(delay - mv, 2) > Math.pow(delay - numV, 2)) {
                mv = numV;
                ms = s;
            }
        }
        return ms;
    }

    function showFixation() {
        return new Promise(resolve => {
            container.innerHTML = '<div class="fixation">+</div>';
            window.scrollTo(0, 0);
            setTimeout(resolve, 1000);
        });
    }

    async function runTrials(n, mode) {
        for (let i = 0; i < n; i++) {
            // Show initial fixation for first trial
            if (i === 0) {
                await showFixation();
            }
            
            const res = await fetch(`/next_design?mode=${mode}&session_id=${CONFIG.session_id}`);
            if (!res.ok) {
                const error = await res.json();
                alert('Session expired or invalid. Please refresh the page and start again.');
                throw new Error(error.error || 'Session error');
            }
            const { design, direction } = await res.json();
            
            const { resp_left, rt } = await showChoice(design, direction);
            // Note: fixation cross is now shown immediately when user presses key
            
            const respRes = await fetch('/response', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ mode, resp_left, direction, rt, session_id: CONFIG.session_id }),
            });
            if (!respRes.ok) {
                const error = await respRes.json();
                alert('Session expired or invalid. Please refresh the page and start again.');
                throw new Error(error.error || 'Session error');
            }
            
            const respData = await respRes.json();
            
            // Check if we started a new session
            if (respData.new_session) {
                CONFIG.current_session = respData.current_session;
            }
            
            // Return early if this session is finished but there are more sessions
            if (respData.finished === false && respData.new_session) {
                return { sessionComplete: true, allComplete: false };
            } else if (respData.finished === true) {
                return { sessionComplete: true, allComplete: true };
            }
            
            // The fixation cross stays visible while processing the next trial
            // This provides continuous feedback during the 1-2 second ADO computation
        }
        
        return { sessionComplete: false, allComplete: false };
    }

    function showChoice(design, direction) {
        return new Promise(resolve => {
            const leftIsSs = direction === 1;
            const ss = leftIsSs
                ? { amount: design.r_ss, delay: design.t_ss }
                : { amount: design.r_ll, delay: design.t_ll };
            const ll = leftIsSs
                ? { amount: design.r_ll, delay: design.t_ll }
                : { amount: design.r_ss, delay: design.t_ss };
            container.innerHTML = `
<div class="trial">
  <div class="option left">
    <div class="amount">$${ss.amount}</div>
    <div class="delay">${convertDelayToStr(ss.delay)}</div>
  </div>
  <div class="option right">
    <div class="amount">$${ll.amount}</div>
    <div class="delay">${convertDelayToStr(ll.delay)}</div>
  </div>
</div>`;
            window.scrollTo(0, 0);
            const start = performance.now();
            function onKey(e) {
                if (e.key === 'z' || e.key === 'm' || e.key === '/') {
                    const rt = performance.now() - start;
                    const resp_left = e.key === 'z' ? 1 : 0;
                    document.removeEventListener('keydown', onKey);
                    
                    // Immediately show fixation cross for user feedback
                    container.innerHTML = '<div class="fixation">+</div>';
                    window.scrollTo(0, 0);
                    
                    resolve({ resp_left, rt });
                }
            }
            document.addEventListener('keydown', onKey);
        });
    }

    if (CONFIG.show_tutorial) {
        await showScreen(instr.intro);
        for (const text of instr.train_before) {
            await showScreen(text);
        }
    }

    if (CONFIG.show_tutorial) {
        await runTrials(CONFIG.num_train_trials, 'train');
        await showScreen(instr.train_after);
    }

    // Run all sessions
    while (CONFIG.current_session <= CONFIG.session_count) {
        // Show pre-main session message only for first session or when coming from between-session screen
        if (CONFIG.current_session === 1) {
            if (CONFIG.session_count === 1) {
                await showScreen(instr.session_start_single);
            } else {
                await showScreen(instr.session_start_multi.replace('{}', CONFIG.current_session).replace('{}', CONFIG.session_count));
            }
        }
        
        await showScreen(instr.main_before.replace('{}', CONFIG.current_session).replace('{}', CONFIG.num_main_trials));
        
        const result = await runTrials(CONFIG.num_main_trials, 'optimal');
        
        // Check the result from runTrials
        if (result.allComplete) {
            // All sessions are complete
            break;
        } else if (result.sessionComplete && !result.allComplete) {
            // This session is complete, but there are more sessions
            const nextSession = CONFIG.current_session;  // current_session was already updated by the response handler
            const prevSession = nextSession - 1;
            await showScreen(instr.session_complete.replace('{}', prevSession).replace('{}', nextSession).replace('{}', CONFIG.session_count));
            // Don't show the "press space to proceed" message again - go directly to main_before
        }
    }

    await showScreen(instr.outro);
}

runExperiment();
