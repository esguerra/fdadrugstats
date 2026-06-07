/* Client-side rendering of interactive charts using Plotly and PapaParse.
   This runs on GitHub Pages (static) and loads CSV files from the `docs/results/` folder.
*/

(function () {
  'use strict';

  const CHART_IDS = [
    'approvals_plot',
    'comparison_plot',
    'company_plot',
    'adverse_plot',
    'top_drugs_plot',
    'top_reactions_plot',
  ];

  const COLORS = {
    blue: '#2563eb',
    orange: '#f97316',
    green: '#059669',
    red: '#dc2626',
    purple: '#7c3aed',
    brown: '#92400e',
    grid: '#e5e7eb',
  };

  const plotConfig = {
    responsive: true,
    displaylogo: false,
    modeBarButtonsToRemove: ['select2d', 'lasso2d'],
  };

  function baseLayout(extra) {
    return Object.assign({
      paper_bgcolor: 'rgba(0,0,0,0)',
      plot_bgcolor: '#ffffff',
      font: { family: "Inter, system-ui, -apple-system, 'Segoe UI', sans-serif", color: '#1f2937' },
      margin: { t: 54, r: 28, b: 58, l: 70 },
      hovermode: 'closest',
      legend: { orientation: 'h', y: 1.08, x: 0, bgcolor: 'rgba(255,255,255,.8)' },
      xaxis: { gridcolor: COLORS.grid, zerolinecolor: COLORS.grid, automargin: true },
      yaxis: { gridcolor: COLORS.grid, zerolinecolor: COLORS.grid, automargin: true },
    }, extra || {});
  }

  function parseCsv(url) {
    return new Promise((resolve, reject) => {
      Papa.parse(url, {
        download: true,
        header: true,
        dynamicTyping: true,
        skipEmptyLines: true,
        complete: (res) => resolve(res.data),
        error: (err) => reject(err),
      });
    });
  }

  function safeNumber(v) {
    if (v === null || v === undefined || v === '') return 0;
    return Number(v) || 0;
  }

  function byYear(a, b) {
    return safeNumber(a.Year) - safeNumber(b.Year);
  }

  function compactNumber(v) {
    return safeNumber(v).toLocaleString();
  }

  function fail(id, message) {
    const el = document.getElementById(id);
    if (el) el.innerText = message;
  }

  function text(value) {
    if (value === null || value === undefined || value === '') return '—';
    return String(value);
  }

  function escapeHtml(value) {
    return text(value)
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;')
      .replaceAll('"', '&quot;')
      .replaceAll("'", '&#039;');
  }

  async function renderCurrentYearApprovals() {
    const title = document.getElementById('current_year_approvals_title');
    const summary = document.getElementById('current_year_approvals_summary');
    const body = document.getElementById('current_year_approvals_body');
    if (!body) return;

    const year = new Date().getFullYear();
    if (title) title.innerText = `${year} approvals so far`;

    try {
      const data = await parseCsv('results/approved_drugs_all.csv');
      const approvals = data
        .filter((r) => safeNumber(r.approval_year) === year)
        .sort((a, b) => text(a.brand_name).localeCompare(text(b.brand_name)));

      if (summary) {
        const nmeCount = approvals.filter((r) => text(r.submission_class).includes('Type 1')).length;
        summary.innerText = `${approvals.length.toLocaleString()} approvals listed for ${year}, including ${nmeCount.toLocaleString()} new molecular entities.`;
      }

      if (approvals.length === 0) {
        body.innerHTML = `<tr><td colspan="5">No ${year} approvals are listed in the current data.</td></tr>`;
        return;
      }

      body.innerHTML = approvals.map((r) => `
        <tr>
          <td>${escapeHtml(r.application_number)}</td>
          <td>${escapeHtml(r.brand_name)}</td>
          <td>${escapeHtml(r.generic_name)}</td>
          <td>${escapeHtml(r.company)}</td>
          <td>${escapeHtml(r.submission_class)}</td>
        </tr>
      `).join('');
    } catch (err) {
      console.error('Error rendering current year approvals:', err);
      if (summary) summary.innerText = 'Error loading current year approval table';
      body.innerHTML = '<tr><td colspan="5">Error loading approval table.</td></tr>';
    }
  }

  async function renderApprovals() {
    try {
      const data = (await parseCsv('results/drug_approvals_by_year.csv')).sort(byYear);
      const years = data.map((r) => String(r.Year));
      const all = data.map((r) => safeNumber(r.All_Approvals_Type1to4_10));
      const nme = data.map((r) => safeNumber(r.NME_Approvals_Type1));

      const traceAll = {
        x: years,
        y: all,
        name: 'All approvals (Type 1-4, 10)',
        type: 'bar',
        marker: { color: COLORS.blue, line: { color: '#1d4ed8', width: 0.5 } },
        hovertemplate: '<b>%{x}</b><br>All approvals: %{y:,}<extra></extra>',
      };

      const traceNME = {
        x: years,
        y: nme,
        name: 'NME approvals (Type 1)',
        type: 'scatter',
        mode: 'lines+markers',
        yaxis: 'y2',
        line: { color: COLORS.orange, width: 3 },
        marker: { color: COLORS.orange, size: 7, line: { color: '#fff', width: 1 } },
        hovertemplate: '<b>%{x}</b><br>NME approvals: %{y:,}<extra></extra>',
      };

      const layout = baseLayout({
        title: { text: 'FDA approvals by year', x: 0, xanchor: 'left' },
        hovermode: 'x unified',
        yaxis: { title: 'All approvals', gridcolor: COLORS.grid, rangemode: 'tozero' },
        yaxis2: {
          title: 'NME approvals',
          overlaying: 'y',
          side: 'right',
          rangemode: 'tozero',
          showgrid: false,
        },
        xaxis: { title: 'Year', gridcolor: COLORS.grid, tickangle: -45, automargin: true },
        margin: { t: 58, r: 76, b: 76, l: 76 },
      });

      Plotly.newPlot('approvals_plot', [traceAll, traceNME], layout, plotConfig);

      const last = 15;
      const recent = data.slice(-last);
      const ryears = recent.map((r) => String(r.Year));
      const rall = recent.map((r) => safeNumber(r.All_Approvals_Type1to4_10));
      const rnme = recent.map((r) => safeNumber(r.NME_Approvals_Type1));

      const t1 = {
        x: ryears,
        y: rall,
        name: 'All approvals',
        type: 'bar',
        marker: { color: COLORS.blue },
        hovertemplate: '<b>%{x}</b><br>All approvals: %{y:,}<extra></extra>',
      };
      const t2 = {
        x: ryears,
        y: rnme,
        name: 'NME approvals',
        type: 'bar',
        marker: { color: COLORS.orange },
        hovertemplate: '<b>%{x}</b><br>NME approvals: %{y:,}<extra></extra>',
      };
      const layout2 = baseLayout({
        barmode: 'group',
        title: { text: `Recent approvals: last ${last} years`, x: 0, xanchor: 'left' },
        hovermode: 'x unified',
        yaxis: { title: 'Approvals', gridcolor: COLORS.grid, rangemode: 'tozero' },
        xaxis: { title: 'Year', gridcolor: COLORS.grid },
      });
      Plotly.newPlot('comparison_plot', [t1, t2], layout2, plotConfig);
    } catch (err) {
      console.error('Error rendering approvals:', err);
      fail('approvals_plot', 'Error loading approvals chart');
      fail('comparison_plot', 'Error loading comparison chart');
    }
  }

  async function renderCompany() {
    try {
      const data = await parseCsv('results/approved_drugs_all.csv');
      const counts = {};
      data.forEach((r) => {
        const company = (r.company || '').trim();
        if (!company || company.toUpperCase() === 'N/A') return;
        counts[company] = (counts[company] || 0) + 1;
      });

      const items = Object.entries(counts).sort((a, b) => b[1] - a[1]).slice(0, 30).reverse();
      const companies = items.map((i) => i[0]);
      const vals = items.map((i) => i[1]);

      const trace = {
        x: vals,
        y: companies,
        text: vals.map(compactNumber),
        textposition: 'outside',
        cliponaxis: false,
        type: 'bar',
        orientation: 'h',
        marker: { color: vals, colorscale: 'Viridis', reversescale: false },
        hovertemplate: '<b>%{y}</b><br>Approved drugs: %{x:,}<extra></extra>',
      };
      const layout = baseLayout({
        title: { text: 'Top 30 companies by approved drug count', x: 0, xanchor: 'left' },
        showlegend: false,
        margin: { l: 250, r: 72, t: 58, b: 48 },
        xaxis: { title: 'Approved drugs', gridcolor: COLORS.grid, rangemode: 'tozero' },
        yaxis: { automargin: true },
      });
      Plotly.newPlot('company_plot', [trace], layout, plotConfig);
    } catch (err) {
      console.error('Error rendering companies:', err);
      fail('company_plot', 'Error loading company chart');
    }
  }

  async function renderAdverse() {
    try {
      const data = (await parseCsv('results/adverse_events_by_year.csv')).sort(byYear);
      const years = data.map((r) => String(r.Year));
      const counts = data.map((r) => safeNumber(r.Count));
      const trace = {
        x: years,
        y: counts,
        type: 'scatter',
        mode: 'lines+markers',
        fill: 'tozeroy',
        fillcolor: 'rgba(220,38,38,.12)',
        line: { color: COLORS.red, width: 3 },
        marker: { color: COLORS.red, size: 7, line: { color: '#fff', width: 1 } },
        hovertemplate: '<b>%{x}</b><br>Reports: %{y:,}<extra></extra>',
      };
      const layout = baseLayout({
        title: { text: 'Adverse event reports by year', x: 0, xanchor: 'left' },
        showlegend: false,
        hovermode: 'x unified',
        xaxis: { title: 'Year', gridcolor: COLORS.grid },
        yaxis: { title: 'Reports', gridcolor: COLORS.grid, rangemode: 'tozero' },
      });
      Plotly.newPlot('adverse_plot', [trace], layout, plotConfig);
    } catch (err) {
      console.error('Error rendering adverse events:', err);
      fail('adverse_plot', 'Error loading adverse events chart');
    }
  }

  async function renderTopLists() {
    try {
      const drugs = (await parseCsv('results/top_reported_drugs.csv')).slice(0, 25).reverse();
      const rx = (await parseCsv('results/top_reactions.csv')).slice(0, 25).reverse();

      const dnames = drugs.map((r) => r.Drug);
      const dreports = drugs.map((r) => safeNumber(r.Reports));
      const tdr = {
        x: dreports,
        y: dnames,
        text: dreports.map(compactNumber),
        textposition: 'outside',
        cliponaxis: false,
        orientation: 'h',
        type: 'bar',
        marker: { color: COLORS.purple },
        hovertemplate: '<b>%{y}</b><br>Reports: %{x:,}<extra></extra>',
      };
      const layoutDr = baseLayout({
        title: { text: 'Top reported drugs (top 25)', x: 0, xanchor: 'left' },
        showlegend: false,
        margin: { l: 250, r: 82, t: 58, b: 48 },
        xaxis: { title: 'Reports', gridcolor: COLORS.grid, rangemode: 'tozero' },
      });
      Plotly.newPlot('top_drugs_plot', [tdr], layoutDr, plotConfig);

      const rnames = rx.map((r) => r.Reaction);
      const rcounts = rx.map((r) => safeNumber(r.Reports));
      const tr = {
        x: rcounts,
        y: rnames,
        text: rcounts.map(compactNumber),
        textposition: 'outside',
        cliponaxis: false,
        orientation: 'h',
        type: 'bar',
        marker: { color: COLORS.brown },
        hovertemplate: '<b>%{y}</b><br>Reports: %{x:,}<extra></extra>',
      };
      const layoutRx = baseLayout({
        title: { text: 'Top reactions (top 25)', x: 0, xanchor: 'left' },
        showlegend: false,
        margin: { l: 250, r: 82, t: 58, b: 48 },
        xaxis: { title: 'Reports', gridcolor: COLORS.grid, rangemode: 'tozero' },
      });
      Plotly.newPlot('top_reactions_plot', [tr], layoutRx, plotConfig);
    } catch (err) {
      console.error('Error rendering top lists:', err);
      fail('top_drugs_plot', 'Error loading top drugs chart');
      fail('top_reactions_plot', 'Error loading top reactions chart');
    }
  }

  function getStoredStaticPreference() {
    try {
      return (localStorage.getItem('useStaticCharts') || '0') === '1';
    } catch (e) {
      return false;
    }
  }

  function setUseStatic(useStatic) {
    if (useStatic) {
      document.body.classList.add('use-static');
    } else {
      document.body.classList.remove('use-static');
    }
    try {
      localStorage.setItem('useStaticCharts', useStatic ? '1' : '0');
    } catch (e) {
      // ignore storage errors
    }
  }

  function purgeCharts() {
    CHART_IDS.forEach((id) => {
      try { Plotly.purge(id); } catch (e) { /* no-op */ }
    });
  }

  function renderAll() {
    renderApprovals();
    renderCompany();
    renderAdverse();
    renderTopLists();
  }

  document.addEventListener('DOMContentLoaded', function () {
    const checkbox = document.getElementById('toggle_static');
    const stored = getStoredStaticPreference();
    if (checkbox) checkbox.checked = stored;
    setUseStatic(stored);

    if (checkbox) {
      checkbox.addEventListener('change', (e) => {
        const useStatic = !!e.target.checked;
        setUseStatic(useStatic);
        if (useStatic) purgeCharts();
        else renderAll();
      });
    }

    renderCurrentYearApprovals();
    if (!stored) renderAll();
  });
})();
