// Suez Canal Tonnage Software Tool Frontend Engine
let sacChartInstance = null;
let currentOffsetsData = null;
let currentUdtData = null;
let currentBulbData = null;

const DEFAULT_HATCH_LIST = [
    { name: "No. 1 Cargo Hatchway", length: 15.20, breadth: 14.00, height: 1.80 },
    { name: "No. 2 Cargo Hatchway", length: 17.60, breadth: 16.00, height: 1.80 },
    { name: "No. 3 Cargo Hatchway", length: 17.60, breadth: 16.00, height: 1.80 },
    { name: "No. 4 Cargo Hatchway", length: 17.60, breadth: 16.00, height: 1.80 },
    { name: "No. 5 Cargo Hatchway", length: 17.60, breadth: 16.00, height: 1.80 }
];

// =========================================================================
// NAVIGATION - LEFT SIDEBAR TAB SWITCHING
// =========================================================================
function switchTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));

    // Update sidebar nav buttons
    document.querySelectorAll('.sidebar-nav-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    const activeContent = document.getElementById(tabId);
    if (activeContent) activeContent.classList.remove('hidden');

    const navBtnId = 'nav-' + tabId.replace('tab-', '');
    const activeNav = document.getElementById(navBtnId);
    if (activeNav) activeNav.classList.add('active');

    // Tab-specific calculations and view refreshes
    if (tabId === 'tab-udt') {
        if (!currentUdtData) {
            calculateUDT();
        } else {
            setTimeout(() => {
                if (currentUdtData && currentUdtData.sac_curve) {
                    try { renderSacChart(currentUdtData.sac_curve); } catch(e){}
                }
                displaySelectedStationTransverse();
            }, 60);
        }
    } else if (tabId === 'tab-bulbous') {
        if (!currentBulbData) calculateBulbousBow();
    } else if (tabId === 'tab-forecastle') {
        if (!currentForecastleData) calculateForecastle();
    } else if (tabId === 'tab-hatches') {
        if (!currentHatchesData) calculateHatchCoamings();
    } else if (tabId === 'tab-superstructure') {
        if (!currentSuperstructureData) calculateSuperstructures();
        triggerAutosave(false);
    } else if (tabId === 'tab-export') {
        loadReportPreview(false);
    }
}

async function proceedToCalculateUDT() {
    switchTab('tab-udt');
    showToast('Calculating Under Deck Tonnage & Appendages...');
    await runAllCalculations();
}

async function runAllCalculations() {
    await calculateUDT();
    await pullBulbousFromOffsets(true);
    await pullForecastleFromOffsets(true);
    await calculateHatchCoamings();
    await calculateSuperstructures();
    triggerAutosave(false);
}

// =========================================================================
// TOAST NOTIFICATIONS
// =========================================================================
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    const msg = document.getElementById('toast-message');
    const icon = document.getElementById('toast-icon');

    msg.innerText = message;
    if (type === 'success') {
        icon.innerHTML = '<span class="text-emerald-400 font-bold">[OK]</span>';
        toast.className = 'fixed bottom-5 right-5 z-50 transform transition-all duration-300 translate-y-0 opacity-100 bg-slate-900 text-white px-4 py-3 rounded-lg shadow-xl border border-emerald-600 flex items-center space-x-3 text-sm';
    } else {
        icon.innerHTML = '<span class="text-red-400 font-bold">[X]</span>';
        toast.className = 'fixed bottom-5 right-5 z-50 transform transition-all duration-300 translate-y-0 opacity-100 bg-slate-900 text-white px-4 py-3 rounded-lg shadow-xl border border-red-600 flex items-center space-x-3 text-sm';
    }

    setTimeout(() => {
        toast.classList.add('translate-y-20', 'opacity-0');
        toast.classList.remove('translate-y-0', 'opacity-100');
    }, 4000);
}

// =========================================================================
// FEATURE TOGGLES (show/hide tabs based on yes/no selections)
// =========================================================================
function applyFeatureToggles() {
    const hasBulb = (document.getElementById('toggle-bulbous')?.value === 'yes');
    const hasFc = (document.getElementById('toggle-forecastle')?.value === 'yes');
    const hasHatches = (document.getElementById('toggle-hatches')?.value === 'yes');
    const hasRh = (document.getElementById('toggle-roundhouses')?.value === 'yes');

    // Nav elements (sidebar buttons)
    const navBulb = document.getElementById('nav-bulbous');
    const navFc = document.getElementById('nav-forecastle');
    const navHatches = document.getElementById('nav-hatches');
    const navRh = document.getElementById('nav-superstructure');

    if (navBulb) navBulb.style.display = hasBulb ? '' : 'none';
    if (navFc) navFc.style.display = hasFc ? '' : 'none';
    if (navHatches) navHatches.style.display = hasHatches ? '' : 'none';
    if (navRh) navRh.style.display = hasRh ? '' : 'none';

    // Highlight toggle cards
    const cBulb = document.getElementById('card-toggle-bulbous');
    const cFc = document.getElementById('card-toggle-forecastle');
    const cHatches = document.getElementById('card-toggle-hatches');
    const cRh = document.getElementById('card-toggle-roundhouses');

    if (cBulb) cBulb.className = hasBulb ? 'p-4 rounded-xl border-2 transition bg-blue-50/40 border-blue-500' : 'p-4 rounded-xl border-2 transition bg-slate-50 border-slate-200 opacity-60';
    if (cFc) cFc.className = hasFc ? 'p-4 rounded-xl border-2 transition bg-blue-50/40 border-blue-500' : 'p-4 rounded-xl border-2 transition bg-slate-50 border-slate-200 opacity-60';
    if (cHatches) cHatches.className = hasHatches ? 'p-4 rounded-xl border-2 transition bg-blue-50/40 border-blue-500' : 'p-4 rounded-xl border-2 transition bg-slate-50 border-slate-200 opacity-60';
    if (cRh) cRh.className = hasRh ? 'p-4 rounded-xl border-2 transition bg-blue-50/40 border-blue-500' : 'p-4 rounded-xl border-2 transition bg-slate-50 border-slate-200 opacity-60';

    // Renumber step badges for visible sidebar tabs
    const allNavs = [
        { el: document.getElementById('nav-config'), active: true },
        { el: document.getElementById('nav-upload'), active: true },
        { el: document.getElementById('nav-udt'), active: true },
        { el: navBulb, active: hasBulb },
        { el: navFc, active: hasFc },
        { el: navHatches, active: hasHatches },
        { el: navRh, active: hasRh },
        { el: document.getElementById('nav-export'), active: true }
    ];

    let badgeNum = 1;
    allNavs.forEach(item => {
        if (!item.el || item.active === false) return;
        const badge = item.el.querySelector('.step-badge');
        if (badge) badge.innerText = badgeNum++;
    });

    // If active tab is now hidden, fallback to tab-config
    const activeTab = document.querySelector('.tab-content:not(.hidden)');
    if (activeTab) {
        if (!hasBulb && activeTab.id === 'tab-bulbous') switchTab('tab-config');
        if (!hasFc && activeTab.id === 'tab-forecastle') switchTab('tab-config');
        if (!hasHatches && activeTab.id === 'tab-hatches') switchTab('tab-config');
        if (!hasRh && activeTab.id === 'tab-superstructure') switchTab('tab-config');
    }
}

// =========================================================================
// CLEAR DATA FUNCTIONS (one per tab)
// =========================================================================
function clearTab1() {
    const fields = [
        'cfg-vessel-name','cfg-nationality','cfg-kind-of-ship','cfg-official-number',
        'cfg-signal-letters','cfg-port-of-registry','cfg-keel-date','cfg-launch-date',
        'cfg-built-where','cfg-material-hull','cfg-builder','cfg-engine','cfg-propellers',
        'cfg-hull-note','cfg-lbp','cfg-breadth','cfg-depth'
    ];
    fields.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.value = '';
    });
    // Reset toggles to default YES
    ['toggle-bulbous','toggle-forecastle','toggle-hatches','toggle-roundhouses'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.value = 'yes';
    });
    applyFeatureToggles();
    showToast('Tab 1 data cleared.');
}

function clearTab2() {
    clearOffsetGrid();
    showToast('Offset grid cleared. You can input custom data or load standard offsets.');
}

function clearTab3() {
    currentUdtData = null;
    const cards = ['card-udt-tons','card-udt-vol','card-udt-dx','card-udt-transom'];
    cards.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.innerText = '--';
    });
    const tbody = document.getElementById('udt-table-body');
    if (tbody) tbody.innerHTML = '';
    const stBody = document.getElementById('transverse-st-tbody');
    if (stBody) stBody.innerHTML = '';
    if (sacChartInstance) { 
        sacChartInstance.destroy(); 
        sacChartInstance = null; 
    }
    const canvas = document.getElementById('sacChart');
    if (canvas) {
        const ctx = canvas.getContext('2d');
        if (ctx) ctx.clearRect(0, 0, canvas.width, canvas.height);
    }
    showToast('Under Deck Tonnage data cleared.');
}

async function clearAllData() {
    try {
        localStorage.removeItem(AUTOSAVE_STORAGE_KEY);
    } catch (e) {}
    clearTab1();
    clearTab2();
    clearTab3();
    clearTab4();
    clearTab5();
    clearTab6();
    clearTab7();
    clearTab8();
    updateOverallTonnageTables(null);
    try {
        await fetch('/api/clear_all_data', { method: 'POST' });
    } catch (e) {}
    setAutosaveBadge('saved', '✓ Cleared');
    showToast('All session data and calculations have been cleared.');
}

function clearTab4() {
    ['bb-len','bb-dx-body','bb-l-nose','bb-dy'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.value = '';
    });
    currentBulbData = null;
    ['card-bb-tonnage','card-bb-vol','card-bb-area-a','card-bb-area-b'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.innerText = '--';
    });
    ['bulb-st20-table-body','bulb-stA-table-body','bulb-stB-table-body','bulb-long-table-body'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.innerHTML = '';
    });
    showToast('Bulbous Bow data cleared.');
}

function clearTab5() {
    const fcH = document.getElementById('fc-height-input');
    if (fcH) fcH.value = '';
    currentForecastleData = null;
    ['card-fc-tonnage','card-fc-vol','card-fc-sum-prod','card-fc-vol-body'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.innerText = '--';
    });
    const tbody = document.getElementById('fc-table-body');
    if (tbody) tbody.innerHTML = '';
    showToast('Forecastle data cleared.');
}

function clearTab6() {
    clearHatches();
    showToast('Hatch Coamings data cleared.');
}

function clearHatches() {
    const countInput = document.getElementById('hatch-count-input');
    if (countInput) countInput.value = 1;
    renderHatchInputRows([{ name: 'No. 1 Cargo Hatchway', length: 0, breadth: 0, height: 0 }]);
    ['card-hatch-total-vol','card-hatch-total-ton','card-hatch-allowance-ton','card-hatch-excess-ton'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.innerText = '--';
    });
    document.querySelectorAll('#hatch-table-body tr.hatch-summary-row').forEach(el => el.remove());
    currentHatchesData = null;
}

function clearTab7() {
    currentSuperstructureData = null;
    DEFAULT_SUPERSTRUCTURE_LIST = [];
    renderSuperstructureRows([{
        deck_level: 'Upper Deck', space_group: 'New Space 1',
        qty: 1, length_m: 0, breadth_m: 0, height_m: 0, form_factor: 1.0,
        action: 'addition', deduction_category: 'NONE'
    }]);
    ['card-super-add-vol','card-super-ded-vol','card-super-net-vol','card-super-net-ton'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.innerText = '--';
    });
    const cardAddTon = document.getElementById('card-super-add-ton');
    if (cardAddTon) cardAddTon.innerText = '-- Tons';
    const cardDedTon = document.getElementById('card-super-ded-ton');
    if (cardDedTon) cardDedTon.innerText = '-- Tons';
    updateOverallTonnageTables(null);
    showToast('Round Houses data cleared.');
}

function clearTab8() {
    const frame = document.getElementById('report-preview-frame');
    if (frame) frame.src = 'about:blank';
    const overlay = document.getElementById('report-loading-overlay');
    if (overlay) overlay.classList.add('hidden');
    showToast('Report preview cleared. Click "Refresh Preview" to re-generate.');
}

// =========================================================================
// GENERATE BLANK TEMPLATE
// =========================================================================
async function generateBlankTemplate() {
    const btn = document.getElementById('btn-gen-template');
    btn.disabled = true;
    btn.innerText = 'Generating Template...';

    const payload = {
        vessel_name: document.getElementById('cfg-vessel-name').value.trim() || 'VESSEL',
        lbp: parseFloat(document.getElementById('cfg-lbp').value) || 186.10,
        breadth: parseFloat(document.getElementById('cfg-breadth').value) || 32.26,
        depth: parseFloat(document.getElementById('cfg-depth').value) || 17.80,
        stations: document.getElementById('cfg-stations').value.split(',').map(s => s.trim()).filter(s => s),
        waterlines: document.getElementById('cfg-waterlines').value.split(',').map(s => s.trim()).filter(s => s),
        buttocks: document.getElementById('cfg-buttocks').value.split(',').map(s => s.trim()).filter(s => s)
    };

    try {
        const resp = await fetch('/api/generate_template', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const res = await resp.json();
        if (res.success) {
            showToast('Empty offset template generated successfully!');
            window.location.href = res.download_url;
        } else {
            showToast(res.error || 'Failed to generate template', 'error');
        }
    } catch (err) {
        showToast('Error communicating with server: ' + err, 'error');
    } finally {
        btn.disabled = false;
        btn.innerHTML = `<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg><span>Generate Blank Offset Template (.xlsx)</span>`;
    }
}

// =========================================================================
// TAB 2: INTERACTIVE TABLE OF OFFSETS WEB SPREADSHEET GRID
// =========================================================================
let webOffsetsData = null;
let currentGridMode = 'hb'; // 'hb', 'ht', 'all'

const STANDARD_STATIONS = [
    "Transom", "0", "0.5", "1", "1.5", "2", "2.5", "3", "4", "5",
    "6", "7", "8", "9", "10", "11", "12", "13", "14", "15",
    "16", "17", "18", "18.5", "19", "19.5", "20", "A", "B"
];

const STANDARD_WATERLINES = [
    "BL", "500WL", "1000WL", "2000WL", "3000WL", "4000WL", "5000WL", "6000WL",
    "7000WL", "8000WL", "9000WL", "10000WL", "11000WL", "12000WL", "14000WL", "16000WL",
    "Upper Deck Side"
];

const STANDARD_BUTTOCKS = [
    "C.L.", "1000 B.L.", "2000 B.L.", "4000 B.L.", "6000 B.L.", "8000 B.L.",
    "10000 B.L.", "12000 B.L.", "14000 B.L.", "Flat of Bottom", "Upper Deck Height",
    "Forecastle Deck Height", "Bulwark Top Height"
];

function setGridMode(mode) {
    currentGridMode = mode;
    ['btn-grid-hb', 'btn-grid-ht', 'btn-grid-all'].forEach(id => {
        const btn = document.getElementById(id);
        if (btn) {
            btn.className = 'px-3 py-1.5 rounded-md text-xs font-bold bg-white text-slate-700 border border-slate-300 hover:bg-slate-100 transition';
        }
    });
    const activeBtn = document.getElementById('btn-grid-' + mode);
    if (activeBtn) {
        activeBtn.className = 'px-3 py-1.5 rounded-md text-xs font-bold bg-navy-800 text-white shadow-sm transition';
    }
    renderOffsetGrid();
}

function initCleanOffsetGrid() {
    webOffsetsData = {
        stations: STANDARD_STATIONS,
        waterlines: STANDARD_WATERLINES,
        buttocks: STANDARD_BUTTOCKS,
        half_breadths: {},
        heights: {},
        vessel_info: {}
    };
    webOffsetsData.stations.forEach(st => {
        webOffsetsData.half_breadths[st] = {};
        webOffsetsData.waterlines.forEach(wl => {
            webOffsetsData.half_breadths[st][wl] = '';
        });
        webOffsetsData.heights[st] = {};
        webOffsetsData.buttocks.forEach(bt => {
            webOffsetsData.heights[st][bt] = '';
        });
    });
    renderOffsetGrid();
    updateBulbousDropdowns();
    updateForecastleDropdowns();
}

function updateBulbousDropdowns() {
    const stations = (webOffsetsData && webOffsetsData.stations && webOffsetsData.stations.length > 0) ? webOffsetsData.stations : STANDARD_STATIONS;
    const buttocks = (webOffsetsData && webOffsetsData.buttocks && webOffsetsData.buttocks.length > 0) ? webOffsetsData.buttocks : STANDARD_BUTTOCKS;

    ['bb-sel-st1', 'bb-sel-st2', 'bb-sel-st3'].forEach((id, idx) => {
        const el = document.getElementById(id);
        if (!el) return;
        const currentVal = el.value;
        const defaultChoice = idx === 0 ? '20' : (idx === 1 ? 'A' : 'B');
        let optionsHtml = '';
        stations.forEach(st => {
            const isSel = currentVal ? (st === currentVal) : (st === defaultChoice);
            optionsHtml += `<option value="${st}" ${isSel ? 'selected' : ''}>Station ${st}</option>`;
        });
        el.innerHTML = optionsHtml;
    });

    ['bb-sel-bt1', 'bb-sel-bt2', 'bb-sel-bt3'].forEach((id, idx) => {
        const el = document.getElementById(id);
        if (!el) return;
        const currentVal = el.value;
        const defaultChoice = idx === 0 ? 'C.L.' : (idx === 1 ? '1000 B.L.' : '2000 B.L.');
        let optionsHtml = '';
        buttocks.forEach(bt => {
            const isSel = currentVal ? (bt === currentVal) : (bt.toLowerCase() === defaultChoice.toLowerCase() || bt.includes(defaultChoice));
            optionsHtml += `<option value="${bt}" ${isSel ? 'selected' : ''}>${bt}</option>`;
        });
        el.innerHTML = optionsHtml;
    });
}

function updateForecastleDropdowns() {
    const stations = (webOffsetsData && webOffsetsData.stations && webOffsetsData.stations.length > 0) ? webOffsetsData.stations : STANDARD_STATIONS;
    const waterlines = (webOffsetsData && webOffsetsData.waterlines && webOffsetsData.waterlines.length > 0) ? webOffsetsData.waterlines : STANDARD_WATERLINES;
    const buttocks = (webOffsetsData && webOffsetsData.buttocks && webOffsetsData.buttocks.length > 0) ? webOffsetsData.buttocks : STANDARD_BUTTOCKS;
    const allCols = [...waterlines, ...buttocks];

    const colEl = document.getElementById('fc-sel-column');
    if (colEl) {
        const currentVal = colEl.value;
        let html = '';
        allCols.forEach(c => {
            const isSel = currentVal ? (c === currentVal) : (c === 'Upper Deck Side' || c.toLowerCase().includes('upper deck'));
            html += `<option value="${c}" ${isSel ? 'selected' : ''}>${c}</option>`;
        });
        colEl.innerHTML = html;
    }

    const startEl = document.getElementById('fc-sel-start-st');
    if (startEl) {
        const currentVal = startEl.value;
        let html = '';
        stations.forEach(st => {
            const isSel = currentVal ? (st === currentVal) : (st === '17');
            html += `<option value="${st}" ${isSel ? 'selected' : ''}>Station ${st}</option>`;
        });
        startEl.innerHTML = html;
    }

    const endEl = document.getElementById('fc-sel-end-st');
    if (endEl) {
        const currentVal = endEl.value;
        let html = '';
        stations.forEach(st => {
            const isSel = currentVal ? (st === currentVal) : (st === 'B');
            html += `<option value="${st}" ${isSel ? 'selected' : ''}>Station ${st}</option>`;
        });
        endEl.innerHTML = html;
    }
}

async function loadStandardOffsetsToGrid() {
    try {
        const resp = await fetch('/api/get_standard_offsets');
        const res = await resp.json();
        if (res.success && res.data) {
            webOffsetsData = res.data;
            currentOffsetsData = res.data;
            renderOffsetGrid();
            updateBulbousDropdowns();
            updateForecastleDropdowns();
            await pullBulbousFromOffsets(true);
            await pullForecastleFromOffsets(true);
            await saveWebOffsets(false);
            showToast('Standard shipyard offsets loaded into web grid!');
        } else {
            showToast('Failed to load standard offsets', 'error');
        }
    } catch (err) {
        showToast('Error loading offsets: ' + err, 'error');
    }
}

function clearOffsetGrid() {
    initCleanOffsetGrid();
    fetch('/api/clear_all_data', { method: 'POST' }).catch(() => {});
    showToast('Offset grid cleared. Ready for custom data input.');
}

function renderOffsetGrid() {
    const table = document.getElementById('web-offset-grid');
    const thead = document.getElementById('grid-thead');
    const tbody = document.getElementById('grid-tbody');
    if (!table || !thead || !tbody) return;

    if (!webOffsetsData) {
        initCleanOffsetGrid();
        return;
    }

    const stations = webOffsetsData.stations || STANDARD_STATIONS;
    const waterlines = webOffsetsData.waterlines || STANDARD_WATERLINES;
    const buttocks = webOffsetsData.buttocks || STANDARD_BUTTOCKS;

    // Update stat labels
    const statCols = document.getElementById('grid-stat-cols');
    if (statCols) {
        if (currentGridMode === 'hb') statCols.innerText = `${waterlines.length} Waterlines`;
        else if (currentGridMode === 'ht') statCols.innerText = `${buttocks.length} Buttocks / Decks`;
        else statCols.innerText = `${waterlines.length} WLs + ${buttocks.length} Buttocks`;
    }

    // Header generation
    let hdrTop = '<tr>';
    hdrTop += `<th class="px-3 py-2 text-center bg-navy-800 text-white font-black sticky left-0 z-20 border-r border-slate-300 w-24">Station</th>`;

    if (currentGridMode === 'hb' || currentGridMode === 'all') {
        waterlines.forEach(wl => {
            hdrTop += `<th class="px-2 py-2 text-right bg-blue-900 text-white font-bold whitespace-nowrap min-w-[75px] border-r border-blue-800">${wl}</th>`;
        });
    }

    if (currentGridMode === 'ht' || currentGridMode === 'all') {
        buttocks.forEach(bt => {
            hdrTop += `<th class="px-2 py-2 text-right bg-slate-800 text-amber-300 font-bold whitespace-nowrap min-w-[85px] border-r border-slate-700">${bt}</th>`;
        });
    }
    hdrTop += '</tr>';
    thead.innerHTML = hdrTop;

    // Rows generation
    let rowsHtml = '';
    stations.forEach((st, idx) => {
        const bgRow = idx % 2 === 0 ? 'bg-white' : 'bg-slate-50/70';
        rowsHtml += `<tr class="${bgRow} hover:bg-amber-50/40 transition">`;
        rowsHtml += `<td class="px-2 py-1 text-center font-bold text-navy-900 sticky left-0 z-10 bg-inherit border-r border-slate-300 font-mono text-xs">${st}</td>`;

        if (currentGridMode === 'hb' || currentGridMode === 'all') {
            waterlines.forEach(wl => {
                const rawVal = webOffsetsData.half_breadths?.[st]?.[wl];
                const displayVal = (rawVal !== undefined && rawVal !== null && rawVal !== '') ? (Array.isArray(rawVal) ? rawVal.join('/') : rawVal) : '';
                rowsHtml += `<td class="p-1 border-r border-slate-200">
                    <input type="text" value="${displayVal}"
                        placeholder="-"
                        oninput="onOffsetCellInput('${st}', 'hb', '${wl}', this.value)"
                        class="w-full text-right font-mono text-xs px-1.5 py-0.5 border border-transparent hover:border-slate-300 focus:border-amber-500 focus:bg-amber-100/60 rounded outline-none transition">
                </td>`;
            });
        }

        if (currentGridMode === 'ht' || currentGridMode === 'all') {
            buttocks.forEach(bt => {
                const rawVal = webOffsetsData.heights?.[st]?.[bt];
                const displayVal = (rawVal !== undefined && rawVal !== null && rawVal !== '') ? (Array.isArray(rawVal) ? rawVal.join('/') : rawVal) : '';
                rowsHtml += `<td class="p-1 border-r border-slate-200">
                    <input type="text" value="${displayVal}"
                        placeholder="-"
                        oninput="onOffsetCellInput('${st}', 'ht', '${bt}', this.value)"
                        class="w-full text-right font-mono text-xs px-1.5 py-0.5 border border-transparent hover:border-slate-300 focus:border-amber-500 focus:bg-amber-100/60 rounded outline-none transition">
                </td>`;
            });
        }
        rowsHtml += '</tr>';
    });
    tbody.innerHTML = rowsHtml;
}

function onOffsetCellInput(st, colType, colName, val) {
    if (!webOffsetsData) return;
    let parsedVal = val === '' ? '' : val;
    if (val !== '' && !val.includes('/') && !isNaN(parseFloat(val))) {
        parsedVal = parseFloat(val);
    }
    if (colType === 'hb') {
        if (!webOffsetsData.half_breadths[st]) webOffsetsData.half_breadths[st] = {};
        webOffsetsData.half_breadths[st][colName] = parsedVal;
    } else {
        if (!webOffsetsData.heights[st]) webOffsetsData.heights[st] = {};
        webOffsetsData.heights[st][colName] = parsedVal;
    }
    triggerAutosave(false);
    debounce('web_offsets_save', () => saveWebOffsets(false), 500);
}

async function saveWebOffsets(showToastMsg = true) {
    if (!webOffsetsData) return;
    try {
        const payload = {
            stations: webOffsetsData.stations || STANDARD_STATIONS,
            waterlines: webOffsetsData.waterlines || STANDARD_WATERLINES,
            buttocks: webOffsetsData.buttocks || STANDARD_BUTTOCKS,
            half_breadths: webOffsetsData.half_breadths || {},
            heights: webOffsetsData.heights || {},
            vessel_info: {
                vessel_name: document.getElementById('cfg-vessel-name')?.value || 'VESSEL',
                lbp: parseFloat(document.getElementById('cfg-lbp')?.value) || 186.10,
                breadth: parseFloat(document.getElementById('cfg-breadth')?.value) || 32.26,
                depth: parseFloat(document.getElementById('cfg-depth')?.value) || 17.80
            }
        };
        const resp = await fetch('/api/save_web_offsets', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const res = await resp.json();
        if (res.success) {
            currentOffsetsData = res.data;
            if (showToastMsg) showToast('Offset grid saved successfully!');
            triggerAutosave(false);
        }
    } catch (err) {
        console.warn('Error saving web offsets:', err);
    }
}

function toggleImportDropzone() {
    const p = document.getElementById('optional-dropzone-panel');
    if (p) p.classList.toggle('hidden');
}

async function exportGridToExcel() {
    await saveWebOffsets(false);
    await generateBlankTemplate();
}

async function uploadOffsetFile(file) {
    const formData = new FormData();
    formData.append('file', file);

    showToast('Importing spreadsheet ' + file.name + '...');
    try {
        const resp = await fetch('/api/upload_offsets', {
            method: 'POST',
            body: formData
        });
        const res = await resp.json();
        if (res.success && res.data) {
            webOffsetsData = res.data;
            currentOffsetsData = res.data;
            renderOffsetGrid();
            updateBulbousDropdowns();
            updateForecastleDropdowns();
            showToast('Excel offsets imported into web grid!');
            await runAllCalculations();
        } else {
            showToast(res.error || 'Upload error', 'error');
        }
    } catch (err) {
        showToast('Error uploading file: ' + err, 'error');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('file-input');
    if (fileInput) {
        fileInput.addEventListener('change', async (e) => {
            if (e.target.files.length > 0) {
                await uploadOffsetFile(e.target.files[0]);
            }
        });
    }
});


// =========================================================================
// REAL-TIME AUTOSAVE & STATE PERSISTENCE ENGINE
// =========================================================================
const AUTOSAVE_STORAGE_KEY = 'suez_tonnage_autosave_state';

function setAutosaveBadge(status, text) {
    const badge = document.getElementById('autosave-status');
    const dot = document.getElementById('autosave-dot');
    const label = document.getElementById('autosave-text');
    if (!badge || !dot || !label) return;

    if (status === 'saving') {
        dot.style.background = '#f59e0b';
        dot.style.boxShadow = '0 0 6px rgba(245, 158, 11, 0.9)';
        label.innerText = 'Saving...';
    } else if (status === 'saved') {
        dot.style.background = '#10b981';
        dot.style.boxShadow = '0 0 6px rgba(16, 185, 129, 0.9)';
        label.innerText = text || '✓ Autosaved';
    } else if (status === 'error') {
        dot.style.background = '#ef4444';
        dot.style.boxShadow = '0 0 6px rgba(239, 68, 68, 0.9)';
        label.innerText = 'Save Error';
    }
}

function collectFullAppState() {
    return {
        ship_particulars: {
            vessel_name: document.getElementById('cfg-vessel-name')?.value || '',
            nationality: document.getElementById('cfg-nationality')?.value || '',
            kind_of_ship: document.getElementById('cfg-kind-of-ship')?.value || '',
            official_number: document.getElementById('cfg-official-number')?.value || '',
            signal_letters: document.getElementById('cfg-signal-letters')?.value || '',
            port_of_registry: document.getElementById('cfg-port-of-registry')?.value || '',
            keel_laying_date: document.getElementById('cfg-keel-date')?.value || '',
            date_of_launch: document.getElementById('cfg-launch-date')?.value || '',
            built_where: document.getElementById('cfg-built-where')?.value || '',
            material_of_hull: document.getElementById('cfg-material-hull')?.value || '',
            builder: document.getElementById('cfg-builder')?.value || '',
            engine_type: document.getElementById('cfg-engine')?.value || '',
            propellers: document.getElementById('cfg-propellers')?.value || '',
            hull_note: document.getElementById('cfg-hull-note')?.value || '',
            lbp: parseFloat(document.getElementById('cfg-lbp')?.value) || 186.10,
            breadth: parseFloat(document.getElementById('cfg-breadth')?.value) || 32.26,
            depth: parseFloat(document.getElementById('cfg-depth')?.value) || 17.80,
            has_bulbous: document.getElementById('toggle-bulbous')?.value === 'yes',
            has_forecastle: document.getElementById('toggle-forecastle')?.value === 'yes',
            has_hatches: document.getElementById('toggle-hatches')?.value === 'yes',
            has_roundhouses: document.getElementById('toggle-roundhouses')?.value === 'yes',
        },
        offsets: webOffsetsData ? {
            stations: webOffsetsData.stations,
            waterlines: webOffsetsData.waterlines,
            buttocks: webOffsetsData.buttocks,
            half_breadths: webOffsetsData.half_breadths,
            heights: webOffsetsData.heights,
        } : null,
        bulbous: {
            has_bulbous: (document.getElementById('bb-has-bulbous')?.value === 'yes'),
            l_bulb: parseFloat(document.getElementById('bb-len')?.value) || 5.0,
            dx_body: parseFloat(document.getElementById('bb-dx-body')?.value) || 1.5,
            l_nose: parseFloat(document.getElementById('bb-l-nose')?.value) || 2.0,
            dy: parseFloat(document.getElementById('bb-dy')?.value) || 1.0,
            selected_stations: [
                document.getElementById('bb-sel-st1')?.value || '20',
                document.getElementById('bb-sel-st2')?.value || 'A',
                document.getElementById('bb-sel-st3')?.value || 'B'
            ],
            selected_buttocks: [
                document.getElementById('bb-sel-bt1')?.value || 'C.L.',
                document.getElementById('bb-sel-bt2')?.value || '1000 B.L.',
                document.getElementById('bb-sel-bt3')?.value || '2000 B.L.'
            ],
            custom_data: currentBulbCustomData,
            calculated: !!currentBulbData
        },
        forecastle: {
            has_forecastle: (document.getElementById('fc-has-forecastle')?.value === 'yes'),
            height: parseFloat(document.getElementById('fc-height-input')?.value) || 2.60,
            column_name: document.getElementById('fc-sel-column')?.value || 'Upper Deck Side',
            start_station: document.getElementById('fc-sel-start-st')?.value || '17',
            end_station: document.getElementById('fc-sel-end-st')?.value || 'B',
            calculated: !!currentForecastleData
        },
        hatches: typeof collectHatchInputs === 'function' ? collectHatchInputs() : [],
        hatches_calculated: !!currentHatchesData,
        superstructures: typeof collectSuperstructureInputs === 'function' ? collectSuperstructureInputs() : [],
        superstructures_calculated: !!currentSuperstructureData,
        udt_calculated: !!currentUdtData,
        timestamp: new Date().toISOString()
    };
}

async function triggerAutosave(immediate = false) {
    if (immediate) {
        await executeAutosave();
    } else {
        setAutosaveBadge('saving');
        debounce('global_autosave', executeAutosave, 450);
    }
}

async function executeAutosave() {
    try {
        setAutosaveBadge('saving');
        const state = collectFullAppState();
        
        // 1. Persist locally to browser storage
        try {
            localStorage.setItem(AUTOSAVE_STORAGE_KEY, JSON.stringify(state));
        } catch (e) {
            console.warn('LocalStorage save error:', e);
        }

        // 2. Sync with Python Flask backend APP_STATE
        const resp = await fetch('/api/autosave', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(state)
        });
        const res = await resp.json();
        if (res.success) {
            const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
            setAutosaveBadge('saved', `✓ Autosaved ${timeStr}`);
        } else {
            setAutosaveBadge('saved', `✓ Autosaved (Local)`);
        }
    } catch (err) {
        const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
        setAutosaveBadge('saved', `✓ Autosaved (Local) ${timeStr}`);
    }
}

function restoreSavedState() {
    try {
        const raw = localStorage.getItem(AUTOSAVE_STORAGE_KEY);
        if (!raw) return false;
        const state = JSON.parse(raw);
        if (!state) return false;

        // Restore Ship Particulars & Features
        if (state.ship_particulars) {
            const sp = state.ship_particulars;
            const setVal = (id, val) => {
                const el = document.getElementById(id);
                if (el && val !== undefined && val !== null && val !== '') el.value = val;
            };
            setVal('cfg-vessel-name', sp.vessel_name);
            setVal('cfg-nationality', sp.nationality);
            setVal('cfg-kind-of-ship', sp.kind_of_ship);
            setVal('cfg-official-number', sp.official_number);
            setVal('cfg-signal-letters', sp.signal_letters);
            setVal('cfg-port-of-registry', sp.port_of_registry);
            setVal('cfg-keel-date', sp.keel_laying_date);
            setVal('cfg-launch-date', sp.date_of_launch);
            setVal('cfg-built-where', sp.built_where);
            setVal('cfg-material-hull', sp.material_of_hull);
            setVal('cfg-builder', sp.builder);
            setVal('cfg-engine', sp.engine_type);
            setVal('cfg-propellers', sp.propellers);
            setVal('cfg-hull-note', sp.hull_note);
            setVal('cfg-lbp', sp.lbp);
            setVal('cfg-breadth', sp.breadth);
            setVal('cfg-depth', sp.depth);

            if (sp.has_bulbous !== undefined) {
                const el = document.getElementById('toggle-bulbous');
                if (el) el.value = sp.has_bulbous ? 'yes' : 'no';
            }
            if (sp.has_forecastle !== undefined) {
                const el = document.getElementById('toggle-forecastle');
                if (el) el.value = sp.has_forecastle ? 'yes' : 'no';
            }
            if (sp.has_hatches !== undefined) {
                const el = document.getElementById('toggle-hatches');
                if (el) el.value = sp.has_hatches ? 'yes' : 'no';
            }
            if (sp.has_roundhouses !== undefined) {
                const el = document.getElementById('toggle-roundhouses');
                if (el) el.value = sp.has_roundhouses ? 'yes' : 'no';
            }
            applyFeatureToggles();
        }

        // Restore Offsets
        if (state.offsets && state.offsets.half_breadths) {
            webOffsetsData = state.offsets;
            currentOffsetsData = state.offsets;
            renderOffsetGrid();
            updateBulbousDropdowns();
            updateForecastleDropdowns();
        }

        // Restore Bulbous Bow
        if (state.bulbous) {
            const b = state.bulbous;
            const bbSel = document.getElementById('bb-has-bulbous');
            if (bbSel) bbSel.value = b.has_bulbous ? 'yes' : 'no';
            if (b.l_bulb) document.getElementById('bb-len').value = b.l_bulb;
            if (b.dx_body) document.getElementById('bb-dx-body').value = b.dx_body;
            if (b.l_nose) document.getElementById('bb-l-nose').value = b.l_nose;
            if (b.dy) document.getElementById('bb-dy').value = b.dy;
            if (b.custom_data) currentBulbCustomData = b.custom_data;
            if (b.selected_stations && b.selected_stations.length === 3) {
                const s1 = document.getElementById('bb-sel-st1'); if (s1) s1.value = b.selected_stations[0];
                const s2 = document.getElementById('bb-sel-st2'); if (s2) s2.value = b.selected_stations[1];
                const s3 = document.getElementById('bb-sel-st3'); if (s3) s3.value = b.selected_stations[2];
            }
            if (b.selected_buttocks && b.selected_buttocks.length === 3) {
                const b1 = document.getElementById('bb-sel-bt1'); if (b1) b1.value = b.selected_buttocks[0];
                const b2 = document.getElementById('bb-sel-bt2'); if (b2) b2.value = b.selected_buttocks[1];
                const b3 = document.getElementById('bb-sel-bt3'); if (b3) b3.value = b.selected_buttocks[2];
            }
        }

        // Restore Forecastle
        if (state.forecastle) {
            const fc = state.forecastle;
            const fcSel = document.getElementById('fc-has-forecastle');
            if (fcSel) fcSel.value = fc.has_forecastle ? 'yes' : 'no';
            if (fc.height) document.getElementById('fc-height-input').value = fc.height;
            if (fc.column_name) {
                const cEl = document.getElementById('fc-sel-column'); if (cEl) cEl.value = fc.column_name;
            }
            if (fc.start_station) {
                const sEl = document.getElementById('fc-sel-start-st'); if (sEl) sEl.value = fc.start_station;
            }
            if (fc.end_station) {
                const eEl = document.getElementById('fc-sel-end-st'); if (eEl) eEl.value = fc.end_station;
            }
        }

        // Restore Hatches
        if (state.hatches && state.hatches.length > 0) {
            const countInput = document.getElementById('hatch-count-input');
            if (countInput) countInput.value = state.hatches.length;
            renderHatchInputRows(state.hatches);
        }

        // Restore Superstructures
        if (state.superstructures && state.superstructures.length > 0) {
            DEFAULT_SUPERSTRUCTURE_LIST = state.superstructures;
            renderSuperstructureRows(state.superstructures);
        }

        return true;
    } catch (e) {
        console.warn('Error restoring autosaved state:', e);
        return false;
    }
}

function setupAutosaveEventListeners() {
    ['tab-config', 'tab-bulbous', 'tab-forecastle'].forEach(tabId => {
        const tabEl = document.getElementById(tabId);
        if (tabEl) {
            tabEl.addEventListener('input', () => triggerAutosave(false));
            tabEl.addEventListener('change', () => triggerAutosave(false));
        }
    });
}

// =========================================================================
// REALTIME CALCULATION DEBOUNCER
// =========================================================================
const _debounceTimers = {};
function debounce(key, fn, delay = 350) {
    if (_debounceTimers[key]) clearTimeout(_debounceTimers[key]);
    _debounceTimers[key] = setTimeout(fn, delay);
}

// =========================================================================
// CALCULATE UNDER DECK TONNAGE
// =========================================================================
async function calculateUDT() {
    const btn = document.getElementById('btn-calc-udt');
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = `<span class="animate-spin inline-block mr-1">⌛</span> Calculating...`;
    }

    try {
        const lbpVal = parseFloat(document.getElementById('cfg-lbp')?.value) || 0;
        const breadthVal = parseFloat(document.getElementById('cfg-breadth')?.value) || 0;
        const depthVal = parseFloat(document.getElementById('cfg-depth')?.value) || 0;
        const vesselName = document.getElementById('cfg-vessel-name')?.value || '';

        const resp = await fetch('/api/calculate_udt', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ lbp: lbpVal, breadth: breadthVal, depth: depthVal, vessel_name: vesselName })
        });
        const res = await resp.json();
        if (res.success && res.data) {
            currentUdtData = res.data;
            document.getElementById('card-udt-tons').innerText = res.data.underdeck_tonnage.toLocaleString('en-US', { minimumFractionDigits: 2 });
            document.getElementById('card-udt-vol').innerText = res.data.total_underdeck_volume.toLocaleString('en-US', { minimumFractionDigits: 2 });
            document.getElementById('card-udt-dx').innerText = res.data.dx.toFixed(3);
            document.getElementById('card-udt-transom').innerText = res.data.transom_volume.toLocaleString('en-US', { minimumFractionDigits: 2 });

            renderLongitudinalTable(res.data.long_rows);
            try {
                renderSacChart(res.data.sac_curve);
            triggerAutosave(false);
            } catch (ce) {
                console.warn('SAC chart render deferred:', ce);
            }
            populateTransverseStationSelect(res.data.station_results);
            if (res.overall_tonnage) updateOverallTonnageTables(res.overall_tonnage);
            showToast('Under Deck Tonnage: ' + res.data.underdeck_tonnage.toLocaleString() + ' Tons');
        } else {
            showToast(res.error || 'Calculation error', 'error');
        }
    } catch (err) {
        showToast('Error calculating UDT: ' + err, 'error');
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = `<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z"></path></svg><span>Calculate Under Deck Tonnage</span>`;
        }
    }
}

// =========================================================================
// POPULATE TRANSVERSE STATION SELECT
// =========================================================================
function populateTransverseStationSelect(stResults) {
    const sel = document.getElementById('select-transverse-st');
    if (!sel || !stResults) return;

    sel.innerHTML = '';
    const sortedKeys = Object.keys(stResults).sort((a, b) => {
        if (a.toLowerCase() === 'transom') return -1;
        if (b.toLowerCase() === 'transom') return 1;
        return (parseFloat(a) || 99) - (parseFloat(b) || 99);
    });

    sortedKeys.forEach(st => {
        const opt = document.createElement('option');
        opt.value = st;
        opt.innerText = `Station ${st}`;
        sel.appendChild(opt);
    });

    if (sortedKeys.length > 0) {
        sel.value = sortedKeys.includes('10') ? '10' : sortedKeys[0];
        displaySelectedStationTransverse();
    }
}

// =========================================================================
// DISPLAY SELECTED STATION TRANSVERSE TABLE
// =========================================================================
function displaySelectedStationTransverse() {
    if (!currentUdtData || !currentUdtData.station_results) return;
    const sel = document.getElementById('select-transverse-st');
    if (!sel) return;

    const stKey = sel.value;
    const stData = currentUdtData.station_results[stKey];
    if (!stData) return;

    const titleEl = document.getElementById('transverse-st-title');
    const metaEl = document.getElementById('transverse-st-meta');
    const tbody = document.getElementById('transverse-st-tbody');

    if (titleEl) titleEl.innerText = `STATION ${stKey.toUpperCase()} TRANSVERSE CALCULATION TABLE`;
    if (metaEl) metaEl.innerText = `Depth D: ${stData.depth_m.toFixed(3)} m | h: ${stData.h_m.toFixed(4)} m | 1/3 h: ${stData.h_over_3.toFixed(4)} m | Section Area: ${stData.area_m2.toFixed(3)} m2`;

    if (!tbody) return;

    let html = '';
    (stData.rows || []).forEach(r => {
        const wlHeight = r.waterline_height_m !== undefined ? r.waterline_height_m.toFixed(3) : '0.000';
        html += `<tr class="hover:bg-slate-50 transition">
            <td class="px-3 py-2 text-center font-bold text-slate-500">${r.point}</td>
            <td class="px-3 py-2 font-bold text-navy-800">${r.waterline}</td>
            <td class="px-3 py-2 text-right font-semibold text-blue-900 bg-blue-50/40">${wlHeight}</td>
            <td class="px-3 py-2 text-right">${r.half_breadth_m.toFixed(3)}</td>
            <td class="px-3 py-2 text-right font-bold text-slate-800">${r.breadth_m.toFixed(3)}</td>
            <td class="px-3 py-2 text-center font-bold bg-slate-50">${r.factor}</td>
            <td class="px-3 py-2 text-right font-black text-navy-800 bg-emerald-50/30">${r.product.toFixed(3)}</td>
        </tr>`;
    });

    html += `
    <tr class="bg-slate-100 font-bold border-t border-slate-300">
        <td colspan="6" class="px-3 py-2 text-left font-bold text-slate-800">SUM OF PRODUCTS:</td>
        <td class="px-3 py-2 text-right font-black text-navy-800">${stData.sum_products.toFixed(3)}</td>
    </tr>
    <tr class="bg-blue-50 font-black">
        <td colspan="6" class="px-3 py-2 text-left text-navy-900">STATION CROSS-SECTIONAL AREA ( (1/3 h) x SUM ):</td>
        <td class="px-3 py-2 text-right text-emerald-800 text-sm">${stData.area_m2.toFixed(3)} m2</td>
    </tr>
    `;

    tbody.innerHTML = html;
}

// =========================================================================
// RENDER LONGITUDINAL TABLE
// =========================================================================
function renderLongitudinalTable(rows) {
    const tbody = document.getElementById('udt-table-body');
    if (!tbody) return;

    let html = '';
    rows.forEach(r => {
        html += `<tr class="hover:bg-slate-50 transition">
            <td class="px-3 py-2 text-center font-bold text-navy-800">${r.station_num}</td>
            <td class="px-3 py-2 text-left font-medium">${r.station_name}</td>
            <td class="px-3 py-2 text-right">${r.position_x.toFixed(3)}</td>
            <td class="px-3 py-2 text-right">${r.depth_m.toFixed(3)}</td>
            <td class="px-3 py-2 text-right font-bold">${r.area_m2.toLocaleString('en-US', { minimumFractionDigits: 2 })}</td>
            <td class="px-3 py-2 text-center font-bold bg-slate-50">${r.factor}</td>
            <td class="px-3 py-2 text-right font-bold text-navy-800">${r.product.toLocaleString('en-US', { minimumFractionDigits: 2 })}</td>
            <td class="px-3 py-2 text-left italic text-slate-500">${r.remark}</td>
        </tr>`;
    });
    tbody.innerHTML = html;
}

// =========================================================================
// RENDER SAC CHART
// =========================================================================
function renderSacChart(curveData) {
    const ctx = document.getElementById('sacChart');
    if (!ctx) return;

    const labels = curveData.map(pt => pt.station);
    const areas = curveData.map(pt => pt.area);

    if (sacChartInstance) {
        sacChartInstance.destroy();
    }

    sacChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Station Cross-Sectional Area (m2)',
                data: areas,
                borderColor: '#1B365D',
                backgroundColor: 'rgba(27, 54, 93, 0.12)',
                borderWidth: 2.5,
                fill: true,
                tension: 0.35,
                pointBackgroundColor: '#2B5B84',
                pointRadius: 4,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: (ctx) => `Area: ${ctx.raw} m2`
                    }
                }
            },
            scales: {
                x: {
                    grid: { color: '#E2E8F0' },
                    title: { display: true, text: 'Longitudinal Stations (AP -> Midship -> FP)', font: { size: 10, weight: 'bold' } }
                },
                y: {
                    beginAtZero: true,
                    grid: { color: '#E2E8F0' },
                    title: { display: true, text: 'Cross-Sectional Area (m2)', font: { size: 10, weight: 'bold' } }
                }
            }
        }
    });
}

// =========================================================================
// BULBOUS BOW
// =========================================================================
let currentBulbCustomData = null;

function parseBulbOffsetCell(val) {
    if (!val && val !== 0) return { up: 0, low: 0 };
    if (Array.isArray(val) && val.length >= 2) {
        const p0 = parseFloat(val[0]) || 0;
        const p1 = parseFloat(val[1]) || 0;
        return { 
            low: p0 > 50 ? p0 / 1000.0 : p0, 
            up: p1 > 50 ? p1 / 1000.0 : p1 
        };
    }
    if (typeof val === 'string' && val.includes('/')) {
        const parts = val.split('/').map(p => parseFloat(p.trim()) || 0);
        return { 
            low: parts[0] > 50 ? parts[0] / 1000.0 : parts[0], 
            up: parts[1] > 50 ? parts[1] / 1000.0 : parts[1] 
        };
    }
    const num = parseFloat(val) || 0;
    return { low: 0, up: num > 50 ? num / 1000.0 : num };
}

async function pullBulbousFromOffsets(silent = false) {
    const st1 = document.getElementById('bb-sel-st1')?.value || '20';
    const st2 = document.getElementById('bb-sel-st2')?.value || 'A';
    const st3 = document.getElementById('bb-sel-st3')?.value || 'B';

    const bt1 = document.getElementById('bb-sel-bt1')?.value || 'C.L.';
    const bt2 = document.getElementById('bb-sel-bt2')?.value || '1000 B.L.';
    const bt3 = document.getElementById('bb-sel-bt3')?.value || '2000 B.L.';

    const dy = parseFloat(document.getElementById('bb-dy')?.value) || 1.0;
    const dx_body = parseFloat(document.getElementById('bb-dx-body')?.value) || 1.5;
    const l_bulb = parseFloat(document.getElementById('bb-len')?.value) || 5.0;
    const l_nose = parseFloat(document.getElementById('bb-l-nose')?.value) || 2.0;

    let hts = webOffsetsData?.heights || {};
    let hbs = webOffsetsData?.half_breadths || {};

    function getVal(st, bt) {
        if (hts[st] && hts[st][bt] !== undefined && hts[st][bt] !== '') return hts[st][bt];
        if (hbs[st] && hbs[st][bt] !== undefined && hbs[st][bt] !== '') return hbs[st][bt];
        return 0;
    }

    const c1 = parseBulbOffsetCell(getVal(st1, bt1));
    const c2 = parseBulbOffsetCell(getVal(st1, bt2));
    const c3 = parseBulbOffsetCell(getVal(st1, bt3));

    const m1 = parseBulbOffsetCell(getVal(st2, bt1));
    const m2 = parseBulbOffsetCell(getVal(st2, bt2));
    const m3 = parseBulbOffsetCell(getVal(st2, bt3));

    const f1 = parseBulbOffsetCell(getVal(st3, bt1));
    const f2 = parseBulbOffsetCell(getVal(st3, bt2));
    const f3 = parseBulbOffsetCell(getVal(st3, bt3));

    const totalVals = c1.up + c1.low + c2.up + c2.low + c3.up + c3.low +
                      m1.up + m1.low + m2.up + m2.low + m3.up + m3.low +
                      f1.up + f1.low + f2.up + f2.low + f3.up + f3.low;

    if (totalVals <= 0) {
        currentBulbCustomData = null;
        currentBulbData = null;
        ['card-bb-tonnage','card-bb-vol','card-bb-area-a','card-bb-area-b'].forEach(id => {
            const el = document.getElementById(id);
            if (el) el.innerText = '--';
        });
        ['bulb-st20-table-body','bulb-stA-table-body','bulb-stB-table-body','bulb-long-table-body'].forEach(id => {
            const el = document.getElementById(id);
            if (el) el.innerHTML = `<tr><td colspan="7" class="text-center py-4 text-slate-500 font-semibold italic bg-slate-50">No bulbous cutting data in active offset table. Input coordinates or import offsets in Step 2.</td></tr>`;
        });
        if (!silent) showToast('No bulbous cutting coordinates found in offset table.', 'info');
        return;
    }

    currentBulbCustomData = {
        st20: {
            title: `Station ${st1}`,
            x_pos: 0.000,
            buttocks: [
                { name: bt1, y_m: 0.0, up: c1.up, low: c1.low, factor: 1 },
                { name: bt2, y_m: dy, up: c2.up, low: c2.low, factor: 4 },
                { name: bt3, y_m: dy * 2, up: c3.up, low: c3.low, factor: 1 },
            ]
        },
        stA: {
            title: `Station ${st2}`,
            x_pos: dx_body,
            buttocks: [
                { name: bt1, y_m: 0.0, up: m1.up, low: m1.low, factor: 1 },
                { name: bt2, y_m: dy, up: m2.up, low: m2.low, factor: 4 },
                { name: bt3, y_m: dy * 2, up: m3.up, low: m3.low, factor: 1 },
            ]
        },
        stB: {
            title: `Station ${st3}`,
            x_pos: dx_body * 2.0,
            buttocks: [
                { name: bt1, y_m: 0.0, up: f1.up, low: f1.low, factor: 1 },
                { name: bt2, y_m: dy, up: f2.up, low: f2.low, factor: 4 },
                { name: bt3, y_m: dy * 2, up: f3.up, low: f3.low, factor: 1 },
            ]
        }
    };

    await calculateBulbousBow(currentBulbCustomData);
    if (!silent) showToast(`Bulbous bow cutting data pulled from Station ${st1}, ${st2}, ${st3}!`);
}

function toggleBulbousInputs() {
    const sel = document.getElementById('bb-has-bulbous');
    const hasBulb = sel ? (sel.value === 'yes') : true;
    const grid = document.getElementById('bb-params-grid');
    const panel = document.getElementById('bb-mapping-panel');
    [grid, panel].forEach(el => {
        if (el) {
            el.style.opacity = hasBulb ? '1' : '0.4';
            el.style.pointerEvents = hasBulb ? 'auto' : 'none';
        }
    });
    debounce('bulbous', () => calculateBulbousBow(), 200);
}

async function calculateBulbousBow(customData = null) {
    const btn = document.getElementById('btn-calc-bulb');
    if (btn) btn.disabled = true;

    const sel = document.getElementById('bb-has-bulbous');
    const hasBulb = sel ? (sel.value === 'yes') : true;

    if (customData) currentBulbCustomData = customData;

    const payload = {
        has_bulbous: hasBulb,
        l_bulb: parseFloat(document.getElementById('bb-len').value) || 5.0,
        dx_body: parseFloat(document.getElementById('bb-dx-body').value) || 1.5,
        l_nose: parseFloat(document.getElementById('bb-l-nose').value) || 2.0,
        dy: parseFloat(document.getElementById('bb-dy').value) || 1.0,
        custom_data: currentBulbCustomData
    };

    try {
        const resp = await fetch('/api/calculate_bulbous', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const res = await resp.json();
        if (res.success) {
            currentBulbData = res.data;
            const mA = res.data.method_A;
            document.getElementById('card-bb-tonnage').innerText = mA.tonnage > 0 ? mA.tonnage.toFixed(2) : '--';
            document.getElementById('card-bb-vol').innerText = mA.total_volume > 0 ? mA.total_volume.toFixed(2) : '--';

            const areaA = (res.data.areas && res.data.areas.stA) ? res.data.areas.stA.total_area.toFixed(3) : '0.000';
            const areaB = (res.data.areas && res.data.areas.stB) ? res.data.areas.stB.total_area.toFixed(3) : '0.000';
            document.getElementById('card-bb-area-a').innerText = areaA !== '0.000' ? areaA : '--';
            document.getElementById('card-bb-area-b').innerText = areaB !== '0.000' ? areaB : '--';

            renderBulbousTables(res.data, hasBulb);
            if (res.overall_tonnage) updateOverallTonnageTables(res.overall_tonnage);
            triggerAutosave(false);
        } else {
            showToast(res.error || 'Error calculating bulbous bow', 'error');
        }
    } catch (err) {
        // silent for realtime
    } finally {
        if (btn) btn.disabled = false;
    }
}

// =========================================================================
// RENDER BULBOUS TABLES (4 tables)
// =========================================================================
function renderBulbousTables(bulbData, hasBulb = true) {
    const tb20 = document.getElementById('bulb-st20-table-body');
    const tbA = document.getElementById('bulb-stA-table-body');
    const tbB = document.getElementById('bulb-stB-table-body');
    const tbLong = document.getElementById('bulb-long-table-body');

    if (!hasBulb || !bulbData) {
        const emptyMsg = `<tr><td colspan="7" class="text-center py-4 text-slate-500 font-semibold italic bg-slate-50">Vessel is not fitted with a bulbous bow (Conventional Straight Bow). Area = 0.000 m2.</td></tr>`;
        if (tb20) tb20.innerHTML = emptyMsg;
        if (tbA) tbA.innerHTML = emptyMsg;
        if (tbB) tbB.innerHTML = emptyMsg;
        if (tbLong) tbLong.innerHTML = `<tr><td colspan="6" class="text-center py-4 text-slate-500 font-semibold italic bg-slate-50">Conventional Straight Bow: Volume = 0.00 m3, Tonnage = 0.00 Suez Tons.</td></tr>`;
        return;
    }

    const areas = bulbData.areas || {};

    function renderStationTbody(tbody, stInfo) {
        if (!tbody || !stInfo) return;
        let html = '';
        (stInfo.rows || []).forEach(r => {
            html += `<tr class="hover:bg-slate-50 transition">
                <td class="px-3 py-2 font-medium text-navy-800">${r.name}</td>
                <td class="px-3 py-2 text-right">${r.y_m.toFixed(3)}</td>
                <td class="px-3 py-2 text-right">${r.z_upper.toFixed(3)}</td>
                <td class="px-3 py-2 text-right">${r.z_lower.toFixed(3)}</td>
                <td class="px-3 py-2 text-right font-bold">${r.depth_m.toFixed(3)}</td>
                <td class="px-3 py-2 text-center font-bold bg-slate-50">${r.factor}</td>
                <td class="px-3 py-2 text-right font-bold text-navy-800">${r.product.toFixed(3)}</td>
            </tr>`;
        });
        html += `<tr class="bg-slate-50 font-bold border-t border-slate-300">
            <td colspan="6" class="px-3 py-1.5 text-left text-slate-700">SUM OF PRODUCTS:</td>
            <td class="px-3 py-1.5 text-right font-black text-navy-800">${(stInfo.sum_prod || 0).toFixed(3)}</td>
        </tr>
        <tr class="bg-slate-50 font-medium">
            <td colspan="6" class="px-3 py-1.5 text-left text-slate-600">HALF STATION AREA ( (dy / 3) x SUM = (${(stInfo.dy || 1.0).toFixed(3)} / 3) x ${(stInfo.sum_prod || 0).toFixed(3)} ):</td>
            <td class="px-3 py-1.5 text-right font-bold text-slate-800">${(stInfo.half_area || 0).toFixed(3)} m2</td>
        </tr>
        <tr class="bg-blue-50 font-black">
            <td colspan="6" class="px-3 py-1.5 text-left text-navy-900">TOTAL STATION AREA ( 2 x HALF AREA ):</td>
            <td class="px-3 py-1.5 text-right text-emerald-800 font-black">${(stInfo.total_area || 0).toFixed(3)} m2</td>
        </tr>`;
        tbody.innerHTML = html;
    }

    renderStationTbody(tb20, areas.st20);
    renderStationTbody(tbA,  areas.stA);
    renderStationTbody(tbB,  areas.stB);

    if (tbLong) {
        const mA = bulbData.method_A || {};
        const st20_info = areas.st20 || {};
        const stA_info  = areas.stA  || {};
        const stB_info  = areas.stB  || {};

        const st20_ar = st20_info.total_area || 0;
        const stA_ar  = stA_info.total_area  || 0;
        const stB_ar  = stB_info.total_area  || 0;

        const st20_name = st20_info.title || 'Station 20';
        const stA_name  = stA_info.title  || 'Station A';
        const stB_name  = stB_info.title  || 'Station B';

        let longHtml = `
        <tr class="hover:bg-slate-50 transition">
            <td class="px-3 py-2 font-bold text-navy-800">${st20_name}</td>
            <td class="px-3 py-2 text-right">0.000</td>
            <td class="px-3 py-2 text-right font-bold">${st20_ar.toFixed(3)}</td>
            <td class="px-3 py-2 text-center font-bold bg-slate-50">1</td>
            <td class="px-3 py-2 text-right font-bold text-navy-800">${(st20_ar * 1).toFixed(3)}</td>
            <td class="px-3 py-2 text-left italic text-slate-500">Aft Boundary / Forward Perpendicular</td>
        </tr>
        <tr class="hover:bg-slate-50 transition">
            <td class="px-3 py-2 font-bold text-navy-800">${stA_name}</td>
            <td class="px-3 py-2 text-right">1.500</td>
            <td class="px-3 py-2 text-right font-bold">${stA_ar.toFixed(3)}</td>
            <td class="px-3 py-2 text-center font-bold bg-slate-50">4</td>
            <td class="px-3 py-2 text-right font-bold text-navy-800">${(stA_ar * 4).toFixed(3)}</td>
            <td class="px-3 py-2 text-left italic text-slate-500">Intermediate Bulb Station</td>
        </tr>
        <tr class="hover:bg-slate-50 transition">
            <td class="px-3 py-2 font-bold text-navy-800">${stB_name}</td>
            <td class="px-3 py-2 text-right">3.000</td>
            <td class="px-3 py-2 text-right font-bold">${stB_ar.toFixed(3)}</td>
            <td class="px-3 py-2 text-center font-bold bg-slate-50">1</td>
            <td class="px-3 py-2 text-right font-bold text-navy-800">${(stB_ar * 1).toFixed(3)}</td>
            <td class="px-3 py-2 text-left italic text-slate-500">Fore Bulb Station</td>
        </tr>
        <tr class="bg-slate-50 font-bold border-t border-slate-300">
            <td colspan="4" class="px-3 py-1.5 text-left text-slate-700">SUM OF PRODUCTS (${st20_name.toUpperCase()} TO ${stB_name.toUpperCase()}):</td>
            <td colspan="2" class="px-3 py-1.5 text-right font-black text-navy-800">${(mA.body_sum || 0).toFixed(3)}</td>
        </tr>
        <tr class="bg-slate-50 font-medium">
            <td colspan="4" class="px-3 py-1.5 text-left text-slate-600">MAIN BULB BODY VOLUME ( (dx / 3) x SUM = (${(mA.dx_body || 1.5).toFixed(2)} / 3) x ${(mA.body_sum || 0).toFixed(3)} ):</td>
            <td colspan="2" class="px-3 py-1.5 text-right font-bold text-slate-800">${(mA.body_volume || 0).toFixed(3)} m3</td>
        </tr>
        <tr class="bg-slate-50 font-medium">
            <td colspan="4" class="px-3 py-1.5 text-left text-slate-600">FORWARD NOSE CAP VOLUME (${stB_name.toUpperCase()} TO TIP, LENGTH = ${(mA.l_nose || 2.0).toFixed(2)} m):</td>
            <td colspan="2" class="px-3 py-1.5 text-right font-bold text-slate-800">${(mA.nose_volume || 0).toFixed(3)} m3</td>
        </tr>
        <tr class="bg-blue-50 font-bold">
            <td colspan="4" class="px-3 py-1.5 text-left text-navy-900">TOTAL BULBOUS BOW VOLUME (MAIN BODY + NOSE CAP):</td>
            <td colspan="2" class="px-3 py-1.5 text-right text-navy-900 font-black">${(mA.total_volume || 0).toFixed(3)} m3</td>
        </tr>
        <tr class="bg-emerald-50 font-black">
            <td colspan="4" class="px-3 py-2 text-left text-emerald-900 text-sm">BULBOUS BOW SUEZ MOORSOM TONNAGE (TOTAL VOLUME / 2.83):</td>
            <td colspan="2" class="px-3 py-2 text-right text-emerald-800 text-sm">${(mA.tonnage || 0).toFixed(2)} Suez Tons</td>
        </tr>`;
        tbLong.innerHTML = longHtml;
    }
}

// =========================================================================
// EXPORT MASTER EXCEL
// =========================================================================
async function exportMasterExcel() {
    const btn = document.getElementById('btn-export-excel');
    btn.disabled = true;
    btn.innerText = 'Building 8-Sheet Workbook...';

    try {
        const resp = await fetch('/api/export_master_excel', { method: 'POST' });
        const res = await resp.json();
        if (res.success) {
            showToast('Master Excel Workbook built successfully!');
            window.location.href = res.download_url;
        } else {
            showToast(res.error || 'Export error', 'error');
        }
    } catch (err) {
        showToast('Error: ' + err, 'error');
    } finally {
        btn.disabled = false;
        btn.innerHTML = `<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg><span>Download Master Excel (.xlsx)</span>`;
    }
}

function getCurrentAppStatePayload() {
    const hasBulb = (document.getElementById('toggle-bulbous')?.value === 'yes');
    const hasFc = (document.getElementById('toggle-forecastle')?.value === 'yes');
    const hasHatches = (document.getElementById('toggle-hatches')?.value === 'yes');
    const hasRh = (document.getElementById('toggle-roundhouses')?.value === 'yes');

    return {
        vessel_name: document.getElementById('cfg-vessel-name')?.value || '',
        nationality: document.getElementById('cfg-nationality')?.value || '',
        kind_of_ship: document.getElementById('cfg-kind-of-ship')?.value || '',
        official_number: document.getElementById('cfg-official-number')?.value || '',
        signal_letters: document.getElementById('cfg-signal-letters')?.value || '',
        port_of_registry: document.getElementById('cfg-port-of-registry')?.value || '',
        keel_laying_date: document.getElementById('cfg-keel-date')?.value || '',
        date_of_launch: document.getElementById('cfg-launch-date')?.value || '',
        built_where: document.getElementById('cfg-built-where')?.value || '',
        material_of_hull: document.getElementById('cfg-material-hull')?.value || '',
        builder: document.getElementById('cfg-builder')?.value || '',
        engine_type: document.getElementById('cfg-engine')?.value || '',
        propellers: document.getElementById('cfg-propellers')?.value || '',
        hull_note: document.getElementById('cfg-hull-note')?.value || '',
        lbp: parseFloat(document.getElementById('cfg-lbp')?.value) || 0,
        breadth: parseFloat(document.getElementById('cfg-breadth')?.value) || 0,
        depth: parseFloat(document.getElementById('cfg-depth')?.value) || 0,
        has_bulbous: hasBulb,
        has_forecastle: hasFc,
        has_hatches: hasHatches,
        has_roundhouses: hasRh,
        l_bulb: parseFloat(document.getElementById('bb-len')?.value) || 5.0,
        dx_body: parseFloat(document.getElementById('bb-dx-body')?.value) || 1.5,
        l_nose: parseFloat(document.getElementById('bb-l-nose')?.value) || 2.0,
        dy: parseFloat(document.getElementById('bb-dy')?.value) || 1.0,
        fc_height: parseFloat(document.getElementById('fc-height-input')?.value) || 2.60,
        custom_data: currentBulbCustomData,
        column_name: document.getElementById('fc-sel-column')?.value || 'Upper Deck Side',
        start_station: document.getElementById('fc-sel-start-st')?.value || '17',
        end_station: document.getElementById('fc-sel-end-st')?.value || 'B',
        hatches: (typeof collectHatchInputs === 'function') ? collectHatchInputs() : null,
        superstructures: (typeof collectSuperstructureInputs === 'function') ? collectSuperstructureInputs() : null
    };
}

// =========================================================================
// EXPORT PDF
// =========================================================================
async function exportPdfReport() {
    const btn = document.getElementById('btn-export-pdf');
    if (btn) {
        btn.disabled = true;
        btn.innerText = 'Generating PDF...';
    }

    try {
        const payload = getCurrentAppStatePayload();
        const resp = await fetch('/api/export_pdf_report', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const res = await resp.json();
        if (res.success) {
            showToast('Professional PDF Report generated!');
            window.location.href = res.download_url;
        } else {
            showToast(res.error || 'PDF error', 'error');
        }
    } catch (err) {
        showToast('Error: ' + err, 'error');
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = `<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg><span>Download Tables Report (PDF)</span>`;
        }
    }
}

// =========================================================================
// LIVE REPORT PREVIEW & EXPORT HTML
// =========================================================================
let currentPreviewZoom = 1.0;
let lastReportViewUrl = '/view_report/Suez_Canal_Official_Tables_Report.html';

async function loadReportPreview(manualClick = false) {
    const overlay = document.getElementById('report-loading-overlay');
    const frame = document.getElementById('report-preview-frame');
    const refreshBtn = document.getElementById('btn-refresh-preview');

    if (overlay) overlay.classList.remove('hidden');
    if (refreshBtn) {
        refreshBtn.disabled = true;
        refreshBtn.classList.add('opacity-75');
    }

    try {
        const payload = getCurrentAppStatePayload();
        const resp = await fetch('/api/export_html_report', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const res = await resp.json();
        if (res.success && res.view_url) {
            lastReportViewUrl = res.view_url;
            const cacheBusterUrl = res.view_url + '?t=' + Date.now();
            if (frame) {
                frame.onload = () => {
                    if (overlay) overlay.classList.add('hidden');
                };
                frame.src = cacheBusterUrl;
            } else if (overlay) {
                overlay.classList.add('hidden');
            }
            if (manualClick) {
                showToast('Report preview refreshed successfully!');
            }
        } else {
            if (overlay) overlay.classList.add('hidden');
            showToast(res.error || 'Failed to generate report preview', 'error');
        }
    } catch (err) {
        if (overlay) overlay.classList.add('hidden');
        showToast('Error generating preview: ' + err, 'error');
    } finally {
        if (refreshBtn) {
            refreshBtn.disabled = false;
            refreshBtn.classList.remove('opacity-75');
        }
    }
}

function zoomReportPreview(delta) {
    currentPreviewZoom = Math.min(1.5, Math.max(0.6, Math.round((currentPreviewZoom + delta) * 10) / 10));
    applyPreviewZoom();
}

function resetReportZoom() {
    currentPreviewZoom = 1.0;
    applyPreviewZoom();
}

function applyPreviewZoom() {
    const wrapper = document.getElementById('preview-paper-wrapper');
    const label = document.getElementById('preview-zoom-label');
    if (label) label.innerText = Math.round(currentPreviewZoom * 100) + '%';
    if (wrapper) {
        wrapper.style.transform = `scale(${currentPreviewZoom})`;
    }
}

function printReportPreview() {
    const frame = document.getElementById('report-preview-frame');
    if (frame && frame.contentWindow) {
        try {
            frame.contentWindow.focus();
            frame.contentWindow.print();
            return;
        } catch (e) {
            // fallback
        }
    }
    window.open(lastReportViewUrl, '_blank');
}

function openReportNewTab() {
    window.open(lastReportViewUrl + '?t=' + Date.now(), '_blank');
}

async function exportHtmlReport() {
    openReportNewTab();
}

// =========================================================================
// EXPORT BULBOUS BOW EXCEL
// =========================================================================
async function exportBulbousExcel() {
    const btn = document.getElementById('btn-export-bulb-excel');
    if (btn) {
        btn.disabled = true;
        btn.innerText = 'Building Bulbous Excel...';
    }

    try {
        const resp = await fetch('/api/export_bulbous_excel', { method: 'POST' });
        const res = await resp.json();
        if (res.success) {
            showToast('Bulbous Bow 4-Table Excel Workbook generated!');
            window.location.href = res.download_url;
        } else {
            showToast(res.error || 'Export error', 'error');
        }
    } catch (err) {
        showToast('Error: ' + err, 'error');
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = `<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg><span>Download Bulbous Bow Excel (.xlsx)</span>`;
        }
    }
}

// =========================================================================
// FORECASTLE TONNAGE
// =========================================================================
let currentForecastleData = null;

function toggleForecastleInputs() {
    const sel = document.getElementById('fc-has-forecastle');
    const hasFc = sel ? (sel.value === 'yes') : true;
    const grid = document.getElementById('fc-params-grid');
    const panel = document.getElementById('fc-mapping-panel');
    [grid, panel].forEach(el => {
        if (el) {
            el.style.opacity = hasFc ? '1' : '0.4';
            el.style.pointerEvents = hasFc ? 'auto' : 'none';
        }
    });
    debounce('forecastle', () => calculateForecastle(), 200);
}

async function calculateForecastle() {
    const btn = document.getElementById('btn-calc-fc');
    if (btn) {
        btn.disabled = true;
        btn.innerText = 'Calculating Forecastle...';
    }

    let hVal = parseFloat(document.getElementById('fc-height-input')?.value);
    if (!hVal || isNaN(hVal) || hVal <= 0) {
        hVal = 2.60;
        const inputEl = document.getElementById('fc-height-input');
        if (inputEl) inputEl.value = '2.60';
    }
    const lbpVal = parseFloat(document.getElementById('cfg-lbp')?.value) || 0;
    const colName = document.getElementById('fc-sel-column')?.value || 'Upper Deck Side';
    const startSt = document.getElementById('fc-sel-start-st')?.value || '17';
    const endSt = document.getElementById('fc-sel-end-st')?.value || 'B';
    const hasFc = (document.getElementById('fc-has-forecastle')?.value !== 'no');

    const payload = { 
        height: hVal, 
        lbp: lbpVal,
        column_name: colName,
        start_station: startSt,
        end_station: endSt,
        has_forecastle: hasFc
    };

    try {
        const resp = await fetch('/api/calculate_forecastle', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const res = await resp.json();
        if (res.success) {
            currentForecastleData = res.data;
            renderForecastleTable(res.data);
            if (res.overall_tonnage) updateOverallTonnageTables(res.overall_tonnage);
            triggerAutosave(false);
        } else {
            showToast(res.error || 'Forecastle calculation error', 'error');
        }
    } catch (err) {
        // silent for realtime
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = `<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path></svg><span>Calculate Forecastle Tonnage</span>`;
        }
    }
}

async function pullForecastleFromOffsets(silent = false) {
    await calculateForecastle();
    const colName = document.getElementById('fc-sel-column')?.value || 'Upper Deck Side';
    const startSt = document.getElementById('fc-sel-start-st')?.value || '17';
    const endSt = document.getElementById('fc-sel-end-st')?.value || 'B';
    if (!silent) showToast(`Forecastle data pulled using column "${colName}" from Station ${startSt} to ${endSt}!`);
}

function renderForecastleTable(data) {
    const cardTon = document.getElementById('card-fc-tonnage');
    const cardVol = document.getElementById('card-fc-vol');
    const cardSum = document.getElementById('card-fc-sum-prod');
    const cardBody = document.getElementById('card-fc-vol-body');
    const tbody = document.getElementById('fc-table-body');

    if (!data || !data.rows || data.rows.length === 0) {
        if (cardTon) cardTon.innerText = '0.00';
        if (cardVol) cardVol.innerText = '0.00';
        if (cardSum) cardSum.innerText = '0.000';
        if (cardBody) cardBody.innerText = '0.00';
        if (tbody) tbody.innerHTML = `<tr><td colspan="10" class="text-center py-4 text-slate-500 font-semibold italic bg-slate-50">No forecastle data extracted or vessel is Flush Deck. Select offset column and stations above, then click "Pull Forecastle Data from Offset Table".</td></tr>`;
        return;
    }

    if (cardTon) cardTon.innerText = data.forecastle_tonnage.toFixed(2);
    if (cardVol) cardVol.innerText = data.forecastle_volume.toFixed(2);
    if (cardSum) cardSum.innerText = data.sum_products.toFixed(3);
    if (cardBody && data.breakdown) cardBody.innerText = data.breakdown.body_volume.toFixed(2);

    if (!tbody) return;

    let html = '';
    data.rows.forEach((r, idx) => {
        html += `<tr class="hover:bg-slate-50 transition">
            <td class="px-3 py-2 text-center font-bold text-slate-500">${idx + 1}</td>
            <td class="px-3 py-2 font-bold text-navy-800">${r.station}</td>
            <td class="px-3 py-2 text-center font-medium text-slate-600 bg-slate-50">${r.station_type}</td>
            <td class="px-3 py-2 text-right">${r.position_x.toFixed(3)}</td>
            <td class="px-3 py-2 text-right">${r.half_breadth_m.toFixed(3)}</td>
            <td class="px-3 py-2 text-right font-bold text-navy-800">${r.breadth_m.toFixed(3)}</td>
            <td class="px-3 py-2 text-right font-semibold text-amber-900 bg-amber-50/40">${r.height_m.toFixed(3)}</td>
            <td class="px-3 py-2 text-right font-black text-slate-800">${r.area_m2.toFixed(3)}</td>
            <td class="px-3 py-2 text-center font-bold bg-slate-50">${r.factor}</td>
            <td class="px-3 py-2 text-right font-black text-navy-800 bg-emerald-50/40">${r.product.toFixed(3)}</td>
        </tr>`;
    });

    const startLabel = data.rows[0]?.station || 'Start';
    const endLabel = data.rows[data.rows.length - 1]?.station || 'End';

    html += `
    <tr class="bg-slate-100 font-bold border-t-2 border-slate-300">
        <td colspan="8" class="px-3 py-2 text-left font-black text-navy-900">SUM OF PRODUCTS (SUM) [${startLabel.toUpperCase()} TO ${endLabel.toUpperCase()}]:</td>
        <td colspan="2" class="px-3 py-2 text-right font-black text-navy-900 text-sm">${data.sum_products.toFixed(3)}</td>
    </tr>
    <tr class="bg-slate-50 font-bold">
        <td colspan="8" class="px-3 py-2 text-left text-slate-700">1/3 STANDARD COMMON INTERVAL (dx / 3):</td>
        <td colspan="2" class="px-3 py-2 text-right text-slate-800">${data.dx_over_3.toFixed(4)} m</td>
    </tr>
    <tr class="bg-blue-50 font-black">
        <td colspan="8" class="px-3 py-2 text-left text-navy-900">FORECASTLE ENCLOSED VOLUME = (dx / 3) * SUM:</td>
        <td colspan="2" class="px-3 py-2 text-right text-navy-900 text-sm">${data.forecastle_volume.toFixed(2)} m3</td>
    </tr>
    <tr class="bg-amber-100 font-black border-t-2 border-amber-400">
        <td colspan="8" class="px-3 py-2 text-left text-amber-950 text-sm">FORECASTLE SUEZ MOORSOM TONNAGE (Volume / 2.83):</td>
        <td colspan="2" class="px-3 py-2 text-right text-red-700 text-base font-black">${data.forecastle_tonnage.toFixed(2)} Suez Tons</td>
    </tr>
    `;

    tbody.innerHTML = html;
}

// Realtime: forecastle height input
document.addEventListener('DOMContentLoaded', () => {
    const fcH = document.getElementById('fc-height-input');
    if (fcH) {
        fcH.addEventListener('input', () => {
            debounce('forecastle', () => calculateForecastle(), 400);
        });
    }
    // Realtime: bulbous bow inputs
    ['bb-len','bb-dx-body','bb-l-nose','bb-dy'].forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.addEventListener('input', () => {
                debounce('bulbous', () => calculateBulbousBow(), 400);
            });
        }
    });
});

// =========================================================================
// HATCH COAMINGS ENGINE
// =========================================================================
let currentHatchesData = null;

function renderHatchInputRows(hatches) {
    const tbody = document.getElementById('hatch-table-body');
    if (!tbody) return;
    let html = '';
    hatches.forEach((h, idx) => {
        const no = idx + 1;
        const l = parseFloat(h.length) || 0;
        const b = parseFloat(h.breadth) || 0;
        const ht = parseFloat(h.height) || 0;
        const vol = (l * b * ht).toFixed(3);
        const ton = (vol / 2.83).toFixed(2);
        html += `
        <tr class="hover:bg-slate-50 transition" data-hatch-index="${idx}">
            <td class="px-3 py-2 text-center font-bold text-slate-500">${no}</td>
            <td class="px-3 py-2">
                <input type="text" class="hatch-input-name w-full text-xs font-semibold text-navy-800 border-slate-300 rounded p-1.5 border bg-white focus:ring-1 focus:ring-navy-800" value="${h.name || 'No. ' + no + ' Cargo Hatchway'}">
            </td>
            <td class="px-3 py-2">
                <input type="number" step="0.01" class="hatch-input-len w-full text-xs text-right font-medium text-slate-800 border-slate-300 rounded p-1.5 border bg-white focus:ring-1 focus:ring-navy-800" value="${l > 0 ? l.toFixed(2) : ''}" placeholder="0.00" oninput="onHatchDimensionInput(${idx})">
            </td>
            <td class="px-3 py-2">
                <input type="number" step="0.01" class="hatch-input-brd w-full text-xs text-right font-medium text-slate-800 border-slate-300 rounded p-1.5 border bg-white focus:ring-1 focus:ring-navy-800" value="${b > 0 ? b.toFixed(2) : ''}" placeholder="0.00" oninput="onHatchDimensionInput(${idx})">
            </td>
            <td class="px-3 py-2">
                <input type="number" step="0.01" class="hatch-input-hgt w-full text-xs text-right font-medium text-slate-800 border-slate-300 rounded p-1.5 border bg-white focus:ring-1 focus:ring-navy-800" value="${ht > 0 ? ht.toFixed(2) : ''}" placeholder="0.00" oninput="onHatchDimensionInput(${idx})">
            </td>
            <td class="px-3 py-2 text-right font-mono font-bold text-slate-800 bg-slate-50 hatch-calc-vol" id="hatch-vol-${idx}">${l > 0 || b > 0 || ht > 0 ? vol : '--'}</td>
            <td class="px-3 py-2 text-right font-mono font-bold text-navy-800 bg-blue-50/30 hatch-calc-ton" id="hatch-ton-${idx}">${l > 0 || b > 0 || ht > 0 ? ton : '--'}</td>
        </tr>`;
    });
    tbody.innerHTML = html;
}

function onHatchDimensionInput(idx) {
    const tr = document.querySelector(`#hatch-table-body tr[data-hatch-index="${idx}"]`);
    if (!tr) return;
    const l = parseFloat(tr.querySelector('.hatch-input-len')?.value) || 0;
    const b = parseFloat(tr.querySelector('.hatch-input-brd')?.value) || 0;
    const h = parseFloat(tr.querySelector('.hatch-input-hgt')?.value) || 0;
    const vol = l * b * h;
    const ton = vol / 2.83;
    const volEl = document.getElementById(`hatch-vol-${idx}`);
    const tonEl = document.getElementById(`hatch-ton-${idx}`);
    if (volEl) volEl.innerText = vol.toFixed(3);
    if (tonEl) tonEl.innerText = ton.toFixed(2);
    // Realtime: trigger hatch summary calc after short debounce
    triggerAutosave(false);
    debounce('hatches', () => calculateHatchCoamings(), 500);
}

function collectHatchInputs() {
    const rows = document.querySelectorAll('#hatch-table-body tr[data-hatch-index]');
    const list = [];
    rows.forEach((tr, idx) => {
        const name = tr.querySelector('.hatch-input-name')?.value || `No. ${idx + 1} Cargo Hatchway`;
        const l = parseFloat(tr.querySelector('.hatch-input-len')?.value) || 0.0;
        const b = parseFloat(tr.querySelector('.hatch-input-brd')?.value) || 0.0;
        const h = parseFloat(tr.querySelector('.hatch-input-hgt')?.value) || 0.0;
        list.push({ name: name, length: l, breadth: b, height: h });
    });
    return list;
}

function onHatchCountChange() {
    const input = document.getElementById('hatch-count-input');
    const newCount = parseInt(input.value) || 1;
    const currentList = collectHatchInputs();

    if (newCount > currentList.length) {
        for (let i = currentList.length + 1; i <= newCount; i++) {
            currentList.push({ name: `No. ${i} Cargo Hatchway`, length: 0, breadth: 0, height: 0 });
        }
    } else if (newCount < currentList.length) {
        currentList.splice(newCount);
    }

    renderHatchInputRows(currentList);
    triggerAutosave(false);
}

async function calculateHatchCoamings() {
    const btn = document.getElementById('btn-calc-hatches');
    if (btn) {
        btn.disabled = true;
        btn.innerText = 'Calculating Hatches...';
    }

    let hatches = collectHatchInputs();
    if (!hatches) hatches = [];

    const payload = { hatches };

    try {
        const resp = await fetch('/api/calculate_hatches', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const res = await resp.json();
        if (res.success) {
            currentHatchesData = res.data;
            renderHatchSummary(res.data);
            if (res.overall_tonnage) updateOverallTonnageTables(res.overall_tonnage);
            triggerAutosave(false);
        } else {
            showToast(res.error || 'Hatch calculation error', 'error');
        }
    } catch (err) {
        // silent
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = `<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z"></path></svg><span>Calculate Hatch Coamings</span>`;
        }
    }
}

function renderHatchSummary(data) {
    const cardVol = document.getElementById('card-hatch-total-vol');
    const cardTon = document.getElementById('card-hatch-total-ton');
    const cardAllow = document.getElementById('card-hatch-allowance-ton');
    const cardExc = document.getElementById('card-hatch-excess-ton');

    if (cardVol) cardVol.innerText = data.total_volume.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    if (cardTon) cardTon.innerText = data.total_tonnage.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    if (cardAllow) cardAllow.innerText = data.allowance_tonnage.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    if (cardExc) cardExc.innerText = data.excess_tonnage.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });

    document.querySelectorAll('#hatch-table-body tr.hatch-summary-row').forEach(el => el.remove());

    const tbody = document.getElementById('hatch-table-body');
    if (!tbody) return;

    const allowVol = (data.allowance_tonnage * 2.83).toFixed(2);
    const excVol = (data.excess_tonnage * 2.83).toFixed(2);

    const summaryHtml = `
    <tr class="hatch-summary-row bg-slate-100 font-bold border-t-2 border-slate-300">
        <td colspan="5" class="px-3 py-2 text-left font-black text-navy-900">TOTAL AGGREGATE CARGO HATCHWAYS:</td>
        <td class="px-3 py-2 text-right font-black text-slate-800">${data.total_volume.toFixed(3)} m3</td>
        <td class="px-3 py-2 text-right font-black text-navy-900">${data.total_tonnage.toFixed(2)} Suez Tons</td>
    </tr>
    <tr class="hatch-summary-row bg-amber-50/70 font-bold">
        <td colspan="5" class="px-3 py-2 text-left text-amber-950">SCA STATUTORY HATCH ALLOWANCE (0.5% / 5 PER 1000 OF GROSS TONNAGE):</td>
        <td class="px-3 py-2 text-right text-amber-900">${allowVol} m3</td>
        <td class="px-3 py-2 text-right text-amber-900 font-black">${data.allowance_tonnage.toFixed(2)} Suez Tons</td>
    </tr>
    <tr class="hatch-summary-row bg-emerald-100 font-black border-t-2 border-emerald-400">
        <td colspan="5" class="px-3 py-2 text-left text-emerald-950 text-sm">CARGO HATCHWAYS EXCESS TONNAGE ADDED TO GROSS TONNAGE:</td>
        <td class="px-3 py-2 text-right text-emerald-900 font-black text-sm">${excVol} m3</td>
        <td class="px-3 py-2 text-right text-emerald-900 text-base font-black">${data.excess_tonnage.toFixed(2)} Suez Tons</td>
    </tr>
    `;

    tbody.insertAdjacentHTML('beforeend', summaryHtml);
}

async function exportHatchExcel() {
    const btn = document.getElementById('btn-export-hatch-excel');
    if (btn) {
        btn.disabled = true;
        btn.innerText = 'Building Hatch Excel...';
    }

    try {
        const payload = { hatches: collectHatchInputs() };
        const resp = await fetch('/api/export_hatch_excel', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const res = await resp.json();
        if (res.success) {
            showToast('Hatch Coaming Tonnage Excel generated successfully!');
            window.location.href = res.download_url;
        } else {
            showToast(res.error || 'Export error', 'error');
        }
    } catch (err) {
        showToast('Error: ' + err, 'error');
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = `<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg><span>Download Hatch Excel (.xlsx)</span>`;
        }
    }
}

// =========================================================================
// SUPERSTRUCTURE / ROUND HOUSES ENGINE
// =========================================================================
let currentSuperstructureData = null;
let DEFAULT_SUPERSTRUCTURE_LIST = [];

function renderSuperstructureRows(list) {
    const tbody = document.getElementById('superstructure-table-body');
    if (!tbody) return;
    let html = '';
    list.forEach((s, idx) => {
        const no = idx + 1;
        const qty = parseInt(s.qty) || 1;
        const l = parseFloat(s.length_m) || 0;
        const b = parseFloat(s.breadth_m) || 0;
        const h = parseFloat(s.height_m) || 0;
        const k = parseFloat(s.form_factor) || 1.0;
        const vol = (qty * l * b * h * k).toFixed(3);
        const ton = (vol / 2.83).toFixed(2);
        const action = (s.action || 'addition').toLowerCase();
        const isAdd = (action === 'addition');
        const cat = s.deduction_category || 'NONE';

        html += `
        <tr class="hover:bg-slate-50 transition" data-super-index="${idx}">
            <td class="px-2 py-1.5 text-center font-bold text-slate-500">${no}</td>
            <td class="px-2 py-1.5">
                <input type="text" class="super-deck w-full text-xs font-semibold text-slate-800 border-slate-300 rounded p-1 border bg-white focus:ring-1 focus:ring-navy-800" value="${s.deck_level || 'Upper Deck'}">
            </td>
            <td class="px-2 py-1.5">
                <input type="text" class="super-group w-full text-xs font-semibold text-navy-800 border-slate-300 rounded p-1 border bg-white focus:ring-1 focus:ring-navy-800" value="${s.space_group || 'Enclosed Space ' + no}">
            </td>
            <td class="px-1 py-1.5">
                <input type="number" min="1" step="1" class="super-qty w-full text-xs text-center font-bold text-slate-800 border-slate-300 rounded p-1 border bg-white focus:ring-1 focus:ring-navy-800" value="${qty}" oninput="onSuperDimensionInput(${idx})">
            </td>
            <td class="px-1 py-1.5">
                <input type="number" step="0.01" class="super-len w-full text-xs text-right font-medium text-slate-800 border-slate-300 rounded p-1 border bg-white focus:ring-1 focus:ring-navy-800" value="${l > 0 ? l.toFixed(2) : ''}" placeholder="0.00" oninput="onSuperDimensionInput(${idx})">
            </td>
            <td class="px-1 py-1.5">
                <input type="number" step="0.01" class="super-brd w-full text-xs text-right font-medium text-slate-800 border-slate-300 rounded p-1 border bg-white focus:ring-1 focus:ring-navy-800" value="${b > 0 ? b.toFixed(2) : ''}" placeholder="0.00" oninput="onSuperDimensionInput(${idx})">
            </td>
            <td class="px-1 py-1.5">
                <input type="number" step="0.01" class="super-hgt w-full text-xs text-right font-medium text-slate-800 border-slate-300 rounded p-1 border bg-white focus:ring-1 focus:ring-navy-800" value="${h > 0 ? h.toFixed(2) : ''}" placeholder="0.00" oninput="onSuperDimensionInput(${idx})">
            </td>
            <td class="px-1 py-1.5">
                <input type="number" step="0.001" class="super-factor w-full text-xs text-right font-medium text-slate-800 border-slate-300 rounded p-1 border bg-white focus:ring-1 focus:ring-navy-800" value="${k.toFixed(3)}" oninput="onSuperDimensionInput(${idx})">
            </td>
            <td class="px-2 py-1.5 text-right font-mono font-bold text-slate-800 bg-slate-50" id="super-vol-${idx}">${l > 0 || b > 0 || h > 0 ? vol : '--'}</td>
            <td class="px-1 py-1.5 text-center">
                <button type="button" onclick="toggleSuperAction(${idx})" id="super-action-btn-${idx}" class="super-action-btn px-2 py-0.5 rounded text-[11px] font-bold transition shadow-sm ${isAdd ? 'bg-emerald-100 text-emerald-800 border border-emerald-300 hover:bg-emerald-200' : 'bg-amber-100 text-amber-800 border border-amber-300 hover:bg-amber-200'}" data-action="${isAdd ? 'addition' : 'deduction'}">
                    ${isAdd ? '+ Addition' : '- Deduction'}
                </button>
            </td>
            <td class="px-1 py-1.5">
                <select class="super-cat w-full text-[11px] font-medium border-slate-300 rounded p-1 border bg-white focus:ring-1 focus:ring-navy-800">
                    <option value="NONE" ${cat === 'NONE' ? 'selected' : ''}>NONE (Gross Only)</option>
                    <option value="OFFICER'S ACCOMMODATION" ${cat === "OFFICER'S ACCOMMODATION" ? 'selected' : ''}>Officer's Accom.</option>
                    <option value="CREW'S ACCOMMODATION" ${cat === "CREW'S ACCOMMODATION" ? 'selected' : ''}>Crew's Accom.</option>
                    <option value="USED IN WORKING THE SHIP" ${cat === "USED IN WORKING THE SHIP" ? 'selected' : ''}>Working the Ship</option>
                    <option value="DEDUCTION FOR PROPELLING POWER" ${cat === "DEDUCTION FOR PROPELLING POWER" ? 'selected' : ''}>Propelling Power</option>
                </select>
            </td>
            <td class="px-2 py-1.5 text-right font-mono font-bold text-navy-800 bg-blue-50/30" id="super-ton-${idx}">${l > 0 || b > 0 || h > 0 ? ton : '--'}</td>
            <td class="px-1 py-1.5 text-center">
                <button type="button" onclick="deleteSuperstructureRow(${idx})" class="text-red-500 hover:text-red-700 font-bold p-1" title="Delete space row">
                    <svg class="w-4 h-4 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                </button>
            </td>
        </tr>`;
    });
    tbody.innerHTML = html;
}

function onSuperDimensionInput(idx) {
    const tr = document.querySelector(`#superstructure-table-body tr[data-super-index="${idx}"]`);
    if (!tr) return;
    const qty = parseInt(tr.querySelector('.super-qty')?.value) || 1;
    const l = parseFloat(tr.querySelector('.super-len')?.value) || 0;
    const b = parseFloat(tr.querySelector('.super-brd')?.value) || 0;
    const h = parseFloat(tr.querySelector('.super-hgt')?.value) || 0;
    const k = parseFloat(tr.querySelector('.super-factor')?.value) || 1.0;
    const vol = qty * l * b * h * k;
    const ton = vol / 2.83;
    const volEl = document.getElementById(`super-vol-${idx}`);
    const tonEl = document.getElementById(`super-ton-${idx}`);
    if (volEl) volEl.innerText = vol.toFixed(3);
    if (tonEl) tonEl.innerText = ton.toFixed(2);
    // Realtime totals update
    triggerAutosave(false);
    debounce('superstructure', () => calculateSuperstructures(), 500);
}

function toggleSuperAction(idx) {
    const btn = document.getElementById(`super-action-btn-${idx}`);
    if (!btn) return;
    const current = btn.getAttribute('data-action');
    if (current === 'addition') {
        btn.setAttribute('data-action', 'deduction');
        btn.className = 'super-action-btn px-2 py-0.5 rounded text-[11px] font-bold transition shadow-sm bg-amber-100 text-amber-800 border border-amber-300 hover:bg-amber-200';
        btn.innerText = '- Deduction';
    } else {
        btn.setAttribute('data-action', 'addition');
        btn.className = 'super-action-btn px-2 py-0.5 rounded text-[11px] font-bold transition shadow-sm bg-emerald-100 text-emerald-800 border border-emerald-300 hover:bg-emerald-200';
        btn.innerText = '+ Addition';
    }
    triggerAutosave(false);
    debounce('superstructure', () => calculateSuperstructures(), 300);
}

function collectSuperstructureInputs() {
    const rows = document.querySelectorAll('#superstructure-table-body tr[data-super-index]');
    const list = [];
    rows.forEach((tr, idx) => {
        const deck = tr.querySelector('.super-deck')?.value || 'Upper Deck';
        const group = tr.querySelector('.super-group')?.value || `Space ${idx + 1}`;
        const qty = parseInt(tr.querySelector('.super-qty')?.value) || 1;
        const l = parseFloat(tr.querySelector('.super-len')?.value) || 0.0;
        const b = parseFloat(tr.querySelector('.super-brd')?.value) || 0.0;
        const h = parseFloat(tr.querySelector('.super-hgt')?.value) || 0.0;
        const k = parseFloat(tr.querySelector('.super-factor')?.value) || 1.0;
        const btn = tr.querySelector('.super-action-btn');
        const action = btn ? (btn.getAttribute('data-action') || 'addition') : 'addition';
        const cat = tr.querySelector('.super-cat')?.value || 'NONE';
        list.push({
            deck_level: deck,
            space_group: group,
            qty: qty,
            length_m: l,
            breadth_m: b,
            height_m: h,
            form_factor: k,
            action: action,
            deduction_category: cat
        });
    });
    return list;
}

function addSuperstructureRow() {
    const current = collectSuperstructureInputs();
    current.push({
        deck_level: "Upper Deck",
        space_group: `New Enclosed Space ${current.length + 1}`,
        qty: 1,
        length_m: 0,
        breadth_m: 0,
        height_m: 0,
        form_factor: 1.00,
        action: "addition",
        deduction_category: "NONE"
    });
    renderSuperstructureRows(current);
    triggerAutosave(false);
}

function deleteSuperstructureRow(idx) {
    const current = collectSuperstructureInputs();
    if (current.length <= 1) {
        showToast('At least one space row is required', 'error');
        return;
    }
    current.splice(idx, 1);
    renderSuperstructureRows(current);
    triggerAutosave(false);
    calculateSuperstructures();
    triggerAutosave(false);
}

function loadDefaultSuperstructures() {
    if (DEFAULT_SUPERSTRUCTURE_LIST.length > 0) {
        renderSuperstructureRows(DEFAULT_SUPERSTRUCTURE_LIST);
        calculateSuperstructures();
    triggerAutosave(false);
        showToast('Loaded 53 default GA superstructure spaces');
    } else {
        fetch('/api/get_default_superstructures')
            .then(r => r.json())
            .then(res => {
                if (res.success && res.spaces) {
                    DEFAULT_SUPERSTRUCTURE_LIST = res.spaces;
                    renderSuperstructureRows(res.spaces);
                    calculateSuperstructures();
    triggerAutosave(false);
                    showToast('Loaded 53 default GA superstructure spaces');
                }
            });
    }
}

async function uploadSuperstructureExcel(input) {
    if (!input.files || input.files.length === 0) return;
    const file = input.files[0];
    const formData = new FormData();
    formData.append('file', file);

    showToast('Uploading & parsing ' + file.name + '...');

    try {
        const resp = await fetch('/api/upload_superstructure_excel', {
            method: 'POST',
            body: formData
        });
        const res = await resp.json();
        if (res.success) {
            currentSuperstructureData = res.data;
            DEFAULT_SUPERSTRUCTURE_LIST = res.spaces;
            renderSuperstructureRows(res.spaces);
            renderSuperstructureSummary(res.data);
            if (res.overall_tonnage) updateOverallTonnageTables(res.overall_tonnage);
            triggerAutosave(false);
            showToast(`Loaded ${res.spaces_count} spaces from ${file.name}!`);
        } else {
            showToast(res.error || 'Failed to parse Excel', 'error');
        }
    } catch (err) {
        showToast('Error uploading: ' + err, 'error');
    } finally {
        input.value = '';
    }
}

async function calculateSuperstructures() {
    const btn = document.getElementById('btn-calc-super');
    if (btn) {
        btn.disabled = true;
        btn.innerText = 'Calculating...';
    }

    let spaces = collectSuperstructureInputs();
    if (!spaces) spaces = [];

    const payload = { spaces };

    try {
        const resp = await fetch('/api/calculate_superstructure', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const res = await resp.json();
        if (res.success) {
            currentSuperstructureData = res.data;
            renderSuperstructureSummary(res.data);
            if (res.overall_tonnage) updateOverallTonnageTables(res.overall_tonnage);
            triggerAutosave(false);
        } else {
            showToast(res.error || 'Calculation error', 'error');
        }
    } catch (err) {
        // silent for realtime
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = `<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z"></path></svg><span>Recalculate</span>`;
        }
    }
}

function renderSuperstructureSummary(data) {
    const cardAddVol = document.getElementById('card-super-add-vol');
    const cardAddTon = document.getElementById('card-super-add-ton');
    const cardDedVol = document.getElementById('card-super-ded-vol');
    const cardDedTon = document.getElementById('card-super-ded-ton');
    const cardNetVol = document.getElementById('card-super-net-vol');
    const cardNetTon = document.getElementById('card-super-net-ton');

    const tfAddVol = document.getElementById('tfoot-super-add-vol');
    const tfAddTon = document.getElementById('tfoot-super-add-ton');
    const tfOffVol = document.getElementById('tfoot-super-off-vol');
    const tfOffTon = document.getElementById('tfoot-super-off-ton');
    const tfCrewVol = document.getElementById('tfoot-super-crew-vol');
    const tfCrewTon = document.getElementById('tfoot-super-crew-ton');
    const tfWorkVol = document.getElementById('tfoot-super-work-vol');
    const tfWorkTon = document.getElementById('tfoot-super-work-ton');
    const tfPropVol = document.getElementById('tfoot-super-prop-vol');
    const tfPropTon = document.getElementById('tfoot-super-prop-ton');
    const tfDedVol = document.getElementById('tfoot-super-ded-vol');
    const tfDedTon = document.getElementById('tfoot-super-ded-ton');
    const tfNetVol = document.getElementById('tfoot-super-net-vol');
    const tfNetTon = document.getElementById('tfoot-super-net-ton');

    const addV = data.round_houses_volume || data.total_addition_volume || 0.0;
    const addT = data.round_houses_tonnage || data.total_addition_tonnage || 0.0;
    const offV = data.officer_accommodation_volume || 0.0;
    const offT = data.officer_accommodation_tonnage || 0.0;
    const crewV = data.crew_accommodation_volume || 0.0;
    const crewT = data.crew_accommodation_tonnage || 0.0;
    const workV = data.working_ship_volume || 0.0;
    const workT = data.working_ship_tonnage || 0.0;
    const propV = data.propelling_power_volume || 0.0;
    const propT = data.propelling_power_tonnage || 0.0;
    const dedV = data.total_deduction_volume || 0.0;
    const dedT = data.total_deduction_tonnage || 0.0;
    const netV = data.net_volume || 0.0;
    const netT = data.net_tonnage || 0.0;

    if (cardAddVol) cardAddVol.innerText = addV.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    if (cardAddTon) cardAddTon.innerText = addT.toFixed(2) + ' Tons';
    if (cardDedVol) cardDedVol.innerText = dedV.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    if (cardDedTon) cardDedTon.innerText = dedT.toFixed(2) + ' Tons';
    if (cardNetVol) cardNetVol.innerText = netV.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    if (cardNetTon) cardNetTon.innerText = netT.toFixed(2);

    if (tfAddVol) tfAddVol.innerText = addV.toFixed(3);
    if (tfAddTon) tfAddTon.innerText = addT.toFixed(2);
    if (tfOffVol) tfOffVol.innerText = offV.toFixed(3);
    if (tfOffTon) tfOffTon.innerText = offT.toFixed(2);
    if (tfCrewVol) tfCrewVol.innerText = crewV.toFixed(3);
    if (tfCrewTon) tfCrewTon.innerText = crewT.toFixed(2);
    if (tfWorkVol) tfWorkVol.innerText = workV.toFixed(3);
    if (tfWorkTon) tfWorkTon.innerText = workT.toFixed(2);
    if (tfPropVol) tfPropVol.innerText = propV.toFixed(3);
    if (tfPropTon) tfPropTon.innerText = propT.toFixed(2);
    if (tfDedVol) tfDedVol.innerText = dedV.toFixed(3);
    if (tfDedTon) tfDedTon.innerText = dedT.toFixed(2);
    if (tfNetVol) tfNetVol.innerText = netV.toFixed(3);
    if (tfNetTon) tfNetTon.innerText = netT.toFixed(2);
}

async function exportSuperstructureExcel() {
    const btn = document.getElementById('btn-export-super-excel');
    if (btn) {
        btn.disabled = true;
        btn.innerText = 'Building Excel...';
    }

    try {
        const payload = { spaces: collectSuperstructureInputs() };
        const resp = await fetch('/api/export_superstructure_excel', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const res = await resp.json();
        if (res.success) {
            showToast('Superstructure Tonnage Excel generated successfully!');
            window.location.href = res.download_url;
        } else {
            showToast(res.error || 'Export error', 'error');
        }
    } catch (err) {
        showToast('Error: ' + err, 'error');
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = `<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg><span>Download Excel</span>`;
        }
    }
}

// =========================================================================
// OVERALL TONNAGE SUMMARY TABLE UPDATER
// =========================================================================
function updateOverallTonnageTables(summary) {
    if (!summary) {
        ['gt-row-udt-vol', 'gt-row-udt-ton', 'gt-row-bulb-vol', 'gt-row-bulb-ton',
         'gt-row-fc-vol', 'gt-row-fc-ton', 'gt-row-hatch-vol', 'gt-row-hatch-ton',
         'gt-row-rh-vol', 'gt-row-rh-ton', 'gt-row-total-vol', 'gt-row-total-ton',
         'nt-row-off-vol', 'nt-row-off-ton', 'nt-row-crew-vol', 'nt-row-crew-ton',
         'nt-row-work-vol', 'nt-row-work-ton', 'nt-row-prop-vol', 'nt-row-prop-ton',
         'nt-row-total-vol', 'nt-row-total-ton', 'nt-row-net-vol', 'nt-row-net-ton'
        ].forEach(id => {
            const el = document.getElementById(id);
            if (el) el.innerText = '--';
        });
        const cAddV = document.getElementById('card-super-add-vol'); if (cAddV) cAddV.innerText = '--';
        const cAddT = document.getElementById('card-super-add-ton'); if (cAddT) cAddT.innerText = '-- Tons';
        const cDedV = document.getElementById('card-super-ded-vol'); if (cDedV) cDedV.innerText = '--';
        const cDedT = document.getElementById('card-super-ded-ton'); if (cDedT) cDedT.innerText = '-- Tons';
        const cNetV = document.getElementById('card-super-net-vol'); if (cNetV) cNetV.innerText = '--';
        const cNetT = document.getElementById('card-super-net-ton'); if (cNetT) cNetT.innerText = '--';
        return;
    }

    const fmt3 = n => (typeof n === 'number') ? n.toLocaleString(undefined, { minimumFractionDigits: 3, maximumFractionDigits: 3 }) : '--';
    const fmt2 = n => (typeof n === 'number') ? n.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : '--';

    // 1. Gross Tonnage Addition rows
    const udt = summary.udt || {};
    const bulb = summary.bulbous || {};
    const fc = summary.forecastle || {};
    const hatch = summary.hatches || {};
    const rh = summary.round_houses || {};
    const gt = summary.gross_tonnage || {};

    const elUdtV = document.getElementById('gt-row-udt-vol'); if (elUdtV) elUdtV.innerText = fmt3(udt.volume || 0);
    const elUdtT = document.getElementById('gt-row-udt-ton'); if (elUdtT) elUdtT.innerText = fmt2(udt.tonnage || 0);

    const elBulbV = document.getElementById('gt-row-bulb-vol'); if (elBulbV) elBulbV.innerText = bulb.has_bulbous && bulb.volume > 0 ? fmt3(bulb.volume) : '-';
    const elBulbT = document.getElementById('gt-row-bulb-ton'); if (elBulbT) elBulbT.innerText = bulb.has_bulbous && bulb.tonnage > 0 ? fmt2(bulb.tonnage) : '-';

    const elFcV = document.getElementById('gt-row-fc-vol'); if (elFcV) elFcV.innerText = fc.volume > 0 ? fmt3(fc.volume) : '-';
    const elFcT = document.getElementById('gt-row-fc-ton'); if (elFcT) elFcT.innerText = fc.tonnage > 0 ? fmt2(fc.tonnage) : '-';

    const elHatchV = document.getElementById('gt-row-hatch-vol'); if (elHatchV) elHatchV.innerText = hatch.volume > 0 ? fmt3(hatch.volume) : '-';
    const elHatchT = document.getElementById('gt-row-hatch-ton'); if (elHatchT) elHatchT.innerText = hatch.tonnage > 0 ? fmt2(hatch.tonnage) : '-';

    const elRhV = document.getElementById('gt-row-rh-vol'); if (elRhV) elRhV.innerText = rh.volume > 0 ? fmt3(rh.volume) : '-';
    const elRhT = document.getElementById('gt-row-rh-ton'); if (elRhT) elRhT.innerText = rh.tonnage > 0 ? fmt2(rh.tonnage) : '-';

    const elTotV = document.getElementById('gt-row-total-vol'); if (elTotV) elTotV.innerText = fmt3(gt.volume || 0);
    const elTotT = document.getElementById('gt-row-total-ton'); if (elTotT) elTotT.innerText = fmt2(gt.tonnage || 0) + ' Tons';

    // 2. Net Tonnage Deduction rows
    const ded = summary.deductions || {};
    const off = ded.officers || {};
    const crew = ded.crew || {};
    const work = ded.working_ship || {};
    const prop = ded.propelling_power || {};
    const totDed = ded.total || {};
    const nt = summary.net_tonnage || {};

    const elOffV = document.getElementById('nt-row-off-vol'); if (elOffV) elOffV.innerText = off.volume > 0 ? fmt3(off.volume) : '-';
    const elOffT = document.getElementById('nt-row-off-ton'); if (elOffT) elOffT.innerText = off.tonnage > 0 ? fmt2(off.tonnage) : '-';

    const elCrewV = document.getElementById('nt-row-crew-vol'); if (elCrewV) elCrewV.innerText = crew.volume > 0 ? fmt3(crew.volume) : '-';
    const elCrewT = document.getElementById('nt-row-crew-ton'); if (elCrewT) elCrewT.innerText = crew.tonnage > 0 ? fmt2(crew.tonnage) : '-';

    const elWorkV = document.getElementById('nt-row-work-vol'); if (elWorkV) elWorkV.innerText = work.volume > 0 ? fmt3(work.volume) : '-';
    const elWorkT = document.getElementById('nt-row-work-ton'); if (elWorkT) elWorkT.innerText = work.tonnage > 0 ? fmt2(work.tonnage) : '-';

    const elPropV = document.getElementById('nt-row-prop-vol'); if (elPropV) elPropV.innerText = prop.volume > 0 ? fmt3(prop.volume) : '-';
    const elPropT = document.getElementById('nt-row-prop-ton'); if (elPropT) elPropT.innerText = prop.tonnage > 0 ? fmt2(prop.tonnage) : '-';

    const elTotDedV = document.getElementById('nt-row-total-vol'); if (elTotDedV) elTotDedV.innerText = fmt3(totDed.volume || 0);
    const elTotDedT = document.getElementById('nt-row-total-ton'); if (elTotDedT) elTotDedT.innerText = fmt2(totDed.tonnage || 0) + ' Tons';

    const elNetV = document.getElementById('nt-row-net-vol'); if (elNetV) elNetV.innerText = fmt3(nt.volume || 0);
    const elNetT = document.getElementById('nt-row-net-ton'); if (elNetT) elNetT.innerText = fmt2(nt.tonnage || 0) + ' Tons';

    // 3. Tab 7 KPI Cards (reflecting overall Suez Gross Tonnage and Net Tonnage!)
    const cardAddVol = document.getElementById('card-super-add-vol');
    const cardAddTon = document.getElementById('card-super-add-ton');
    const cardDedVol = document.getElementById('card-super-ded-vol');
    const cardDedTon = document.getElementById('card-super-ded-ton');
    const cardNetVol = document.getElementById('card-super-net-vol');
    const cardNetTon = document.getElementById('card-super-net-ton');

    if (cardAddVol) cardAddVol.innerText = (gt.volume || 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    if (cardAddTon) cardAddTon.innerText = (gt.tonnage || 0).toFixed(2) + ' Tons';
    if (cardDedVol) cardDedVol.innerText = (totDed.volume || 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    if (cardDedTon) cardDedTon.innerText = (totDed.tonnage || 0).toFixed(2) + ' Tons';
    if (cardNetVol) cardNetVol.innerText = (nt.volume || 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    if (cardNetTon) cardNetTon.innerText = (nt.tonnage || 0).toFixed(2);
}

// =========================================================================
// PAGE LOAD: Initialize and Restore Autosaved State
// =========================================================================
window.addEventListener('load', async () => {
    // 1. Attempt to restore autosaved user values from browser storage
    const restored = restoreSavedState();
    applyFeatureToggles();
    setupAutosaveEventListeners();
    updateBulbousDropdowns();
    updateForecastleDropdowns();

    if (restored && webOffsetsData && Object.keys(webOffsetsData.half_breadths || {}).length > 0) {
        renderOffsetGrid();
        updateBulbousDropdowns();
        updateForecastleDropdowns();
        if (currentUdtData) await calculateUDT();
        if (currentBulbData) await calculateBulbousBow(currentBulbCustomData);
        if (currentForecastleData) await calculateForecastle();
        if (currentHatchesData) await calculateHatchCoamings();
        if (currentSuperstructureData) await calculateSuperstructures();
        setAutosaveBadge('saved', '✓ Autosaved');
    } else {
        initCleanOffsetGrid();
        clearTab3();
        clearTab4();
        clearTab5();
        clearTab6();
        clearTab7();
        updateOverallTonnageTables(null);
        setAutosaveBadge('saved', '✓ Ready');
    }
});
