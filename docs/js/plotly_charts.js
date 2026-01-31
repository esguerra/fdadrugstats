/* Client-side rendering of interactive charts using Plotly and PapaParse.
   This runs on GitHub Pages (static) and loads CSV files from the `docs/results/` folder.
*/

(function () {
  'use strict';

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

  async function renderApprovals() {
    try {
      const data = await parseCsv('results/drug_approvals_by_year.csv');
      const years = data.map((r) => String(r.Year));
      const all = data.map((r) => safeNumber(r.All_Approvals_Type1to4_10));
      const nme = data.map((r) => safeNumber(r.NME_Approvals_Type1));

      const traceAll = {
        x: years,
        y: all,
        name: 'All approvals (Type 1-4, 10)',
        type: 'bar',
        marker: { color: '#1f77b4' },
      };

      const traceNME = {
        x: years,
        y: nme,
        name: 'NME (Type 1)',
        type: 'scatter',
        mode: 'lines+markers',
        yaxis: 'y2',
        line: { color: '#ff7f0e' },
      };

      const layout = {
        title: 'FDA Approvals by Year (All vs NME)',
        xaxis: { title: 'Year' },
        yaxis: { title: 'All approvals (count)' },
        yaxis2: {
          title: 'NME (count)',
          overlaying: 'y',
          side: 'right',
        },
        legend: { orientation: 'h' },
        margin: { t: 40, l: 50, r: 50 },
      };

      Plotly.newPlot('approvals_plot', [traceAll, traceNME], layout, { responsive: true });

      // Smaller recent comparison
      const last = 15;
      const recent = data.slice(-last);
      const ryears = recent.map((r) => String(r.Year));
      const rall = recent.map((r) => safeNumber(r.All_Approvals_Type1to4_10));
      const rnme = recent.map((r) => safeNumber(r.NME_Approvals_Type1));

      const t1 = { x: ryears, y: rall, name: 'All approvals', type: 'bar' };
      const t2 = { x: ryears, y: rnme, name: 'NME', type: 'bar' };
      const layout2 = { barmode: 'group', title: `Last ${last} years: All vs NME`, margin: { t: 40 } };
      Plotly.newPlot('comparison_plot', [t1, t2], layout2, { responsive: true });
    } catch (err) {
      console.error('Error rendering approvals:', err);
      document.getElementById('approvals_plot').innerText = 'Error loading approvals chart';
      document.getElementById('comparison_plot').innerText = 'Error loading comparison chart';
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

      const items = Object.entries(counts).sort((a, b) => b[1] - a[1]).slice(0, 30);
      const companies = items.map((i) => i[0]);
      const vals = items.map((i) => i[1]);

      const trace = { x: vals.reverse(), y: companies.reverse(), type: 'bar', orientation: 'h', marker: { color: '#2ca02c' } };
      const layout = { title: 'Top 30 companies by approved drug count', margin: { l: 220, t: 40 } };
      Plotly.newPlot('company_plot', [trace], layout, { responsive: true });
    } catch (err) {
      console.error('Error rendering companies:', err);
      document.getElementById('company_plot').innerText = 'Error loading company chart';
    }
  }

  async function renderAdverse() {
    try {
      const data = await parseCsv('results/adverse_events_by_year.csv');
      const years = data.map((r) => String(r.Year));
      const counts = data.map((r) => safeNumber(r.Count));
      const trace = { x: years, y: counts, type: 'scatter', mode: 'lines+markers', marker: { color: '#d62728' } };
      const layout = { title: 'Adverse events reported by year', xaxis: { title: 'Year' }, yaxis: { title: 'Reports' }, margin: { t: 40 } };
      Plotly.newPlot('adverse_plot', [trace], layout, { responsive: true });
    } catch (err) {
      console.error('Error rendering adverse events:', err);
      document.getElementById('adverse_plot').innerText = 'Error loading adverse events chart';
    }
  }

  async function renderTopLists() {
    try {
      const drugs = await parseCsv('results/top_reported_drugs.csv');
      const rx = await parseCsv('results/top_reactions.csv');

      const dnames = drugs.map((r) => r.Drug);
      const dreports = drugs.map((r) => safeNumber(r.Reports));
      const tdr = { x: dreports.reverse(), y: dnames.reverse(), orientation: 'h', type: 'bar', marker: { color: '#9467bd' } };
      const layoutDr = { title: 'Top reported drugs', margin: { l: 220, t: 40 } };
      Plotly.newPlot('top_drugs_plot', [tdr], layoutDr, { responsive: true });

      const rnames = rx.map((r) => r.Reaction);
      const rcounts = rx.map((r) => safeNumber(r.Reports));
      const tr = { x: rcounts.slice(0, 25).reverse(), y: rnames.slice(0, 25).reverse(), orientation: 'h', type: 'bar', marker: { color: '#8c564b' } };
      const layoutRx = { title: 'Top reactions (top 25)', margin: { l: 220, t: 40 } };
      Plotly.newPlot('top_reactions_plot', [tr], layoutRx, { responsive: true });
    } catch (err) {
      console.error('Error rendering top lists:', err);
      document.getElementById('top_drugs_plot').innerText = 'Error loading top drugs chart';
      document.getElementById('top_reactions_plot').innerText = 'Error loading top reactions chart';
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

  // Initialize all charts (respect stored preference to avoid loading CSVs if static)
  document.addEventListener('DOMContentLoaded', function () {
    const checkbox = document.getElementById('toggle_static');
    const stored = (localStorage.getItem('useStaticCharts') || '0') === '1';
    if (checkbox) checkbox.checked = stored;
    setUseStatic(stored);

    checkbox && checkbox.addEventListener('change', (e) => {
      const useStatic = !!e.target.checked;
      setUseStatic(useStatic);
      if (!useStatic) {
        // switched to interactive: render charts on demand
        renderApprovals();
        renderCompany();
        renderAdverse();
        renderTopLists();
      } else {
        // switched to static: purge interactive charts from DOM to save resources
        try {
          ['approvals_plot', 'comparison_plot', 'company_plot', 'adverse_plot', 'top_drugs_plot', 'top_reactions_plot'].forEach((id) => {
            try { Plotly.purge(id); } catch (e) { /* no-op */ }
          });
        } catch (err) {
          // ignore
        }
      }
    });

    if (!stored) {
      // default: interactive mode — render charts
      renderApprovals();
      renderCompany();
      renderAdverse();
      renderTopLists();
    }
  });
})();
