let globalTargetList = [];
const BRAND_BLUE = '#2a388f';

async function fazerLogin() {
    const user = document.getElementById('username').value;
    const pass = document.getElementById('password').value;
    try {
        const res = await fetch('/api/auth', {
            method: 'POST', headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username: user, password: pass})
        });
        if (res.ok) {
            const data = await res.json();
            sessionStorage.setItem('token', data.token);
            document.getElementById('user-name-display').innerText = `${data.name} (${data.role})`;
            if (data.role === "Administrador") document.getElementById('btn-admin').style.display = 'block';
            document.getElementById('login-overlay').style.display = 'none';
            document.getElementById('main-dashboard').style.display = 'block';
            carregarDepartamentos();
            carregarDashboard();
        } else { document.getElementById('login-error').style.display = 'block'; }
    } catch (e) { console.error(e); }
}

function logout() { sessionStorage.clear(); location.reload(); }

async function carregarDepartamentos() {
    const res = await fetch('/api/departments');
    const deps = await res.json();
    const select = document.getElementById('dep-filter');
    deps.forEach(dep => {
        const opt = document.createElement('option'); opt.value = dep; opt.innerText = dep;
        select.appendChild(opt);
    });
}

async function carregarDashboard() {
    const dep = document.getElementById('dep-filter').value;
    const res = await fetch(`/api/organizational_health?departamento=${dep}`);
    const data = await res.json();
    globalTargetList = data.target_list;

    document.getElementById('kpi-hc').innerText = data.kpis.headcount;
    document.getElementById('kpi-turnover').innerText = data.kpis.taxa_turnover + '%';
    document.getElementById('kpi-evasoes').innerText = data.kpis.evasoes;

    const layoutBase = {
        paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)', font: {color: '#86868B'},
        margin: {t:10, l:50, r:20, b:35}, autosize: true,
        xaxis: { gridcolor: 'rgba(255,255,255,0.05)' }, yaxis: { gridcolor: 'rgba(255,255,255,0.05)' }
    };
    const configPlotly = { displayModeBar: false, responsive: true };

    const salFica=[], tempoFica=[], genFica=[], salSai=[], tempoSai=[], genSai=[];
    data.eda_avancada.status.forEach((st, idx) => {
        if(st===0) { salFica.push(data.eda_avancada.salario[idx]); tempoFica.push(data.eda_avancada.tempo[idx]); genFica.push(data.eda_avancada.genero[idx]); }
        else { salSai.push(data.eda_avancada.salario[idx]); tempoSai.push(data.eda_avancada.tempo[idx]); genSai.push(data.eda_avancada.genero[idx]); }
    });

    const tViolinFica = {type: 'violin', x: genFica, y: salFica, legendgroup: 'Ativos', scalegroup: 'Ativos', name: 'Ativos', side: 'negative', box: {visible: true}, line: {color: '#32D74B', width: 2}, meanline: {visible: true}, spanmode: 'hard'};
    const tViolinSai = {type: 'violin', x: genSai, y: salSai, legendgroup: 'Evasões', scalegroup: 'Evasões', name: 'Evasões', side: 'positive', box: {visible: true}, line: {color: '#FF453A', width: 2}, meanline: {visible: true}, spanmode: 'hard'};
    Plotly.newPlot('chart-salario-genero', [tViolinFica, tViolinSai], {...layoutBase, violingap: 0, violinmode: 'overlay', showlegend: true, legend: {orientation: 'h', y: 1.15}, yaxis: {title: 'Salário (R$)', rangemode: 'nonnegative', gridcolor: 'rgba(255,255,255,0.05)'}}, configPlotly);

    const tBoxFica = {y: tempoFica, type: 'box', name: 'Ativos', marker: {color: '#32D74B'}};
    const tBoxSai = {y: tempoSai, type: 'box', name: 'Evasões', marker: {color: '#FF453A'}};
    Plotly.newPlot('chart-tempo-casa', [tBoxFica, tBoxSai], {...layoutBase, yaxis: {title: 'Meses de Casa', rangemode: 'nonnegative', gridcolor: 'rgba(255,255,255,0.05)'}, showlegend: false}, configPlotly);

    const tScatFica = {x: tempoFica, y: salFica, mode: 'markers', type: 'scatter', name: 'Ativos', marker: {color: 'rgba(255,255,255,0.2)', size: 6}};
    const tScatSai = {x: tempoSai, y: salSai, mode: 'markers', type: 'scatter', name: 'Evasões', marker: {color: '#FF453A', size: 9, symbol: 'diamond'}};
    Plotly.newPlot('chart-bivariada', [tScatFica, tScatSai], {...layoutBase, xaxis: {title: 'Meses de Casa', rangemode: 'nonnegative', gridcolor: 'rgba(255,255,255,0.05)'}, yaxis: {title: 'Salário (R$)', rangemode: 'nonnegative', gridcolor: 'rgba(255,255,255,0.05)'}, showlegend: true, legend: {orientation: 'h', y: 1.15}}, configPlotly);

    const tHC = {x: data.departamentos.nomes, y: data.departamentos.headcount, type: 'bar', name: 'Ativos', marker: {color: BRAND_BLUE}};
    const tEv = {x: data.departamentos.nomes, y: data.departamentos.evasoes, type: 'bar', name: 'Evasões', marker: {color: '#FF453A'}};
    Plotly.newPlot('chart-departamentos', [tHC, tEv], {...layoutBase, barmode: 'group', showlegend: true, legend: {orientation: 'h', y: 1.15}}, configPlotly);

    const tIdadeAtivos = {x: data.demografia.idade_ativos, type: 'histogram', name: 'Ativos', opacity: 0.7, marker: {color: BRAND_BLUE}};
    const tIdadeDemitidos = {x: data.demografia.idade_demitidos, type: 'histogram', name: 'Evasões', opacity: 0.8, marker: {color: '#FF453A'}};
    Plotly.newPlot('chart-demografia', [tIdadeAtivos, tIdadeDemitidos], {...layoutBase, barmode: 'overlay', xaxis: {title: 'Idade', rangemode: 'nonnegative', gridcolor: 'rgba(255,255,255,0.05)'}, showlegend: true, legend: {orientation: 'h', y: 1.15}}, configPlotly);

    const tPerfil = {labels: data.perfil.nomes, values: data.perfil.valores, type: 'pie', hole: 0.6, textinfo: 'percent+label', marker: { colors: [BRAND_BLUE, '#FF453A', '#32D74B', '#FF9F0A', '#BF5AF2'] }};
    Plotly.newPlot('chart-perfil', [tPerfil], {...layoutBase, showlegend: false}, configPlotly);

    const tDep = {x: data.dependentes.fugas, y: data.dependentes.qtd.map(d => `${d} Dep.`), type: 'bar', orientation: 'h', name: 'Evasões', marker: { color: '#FF9F0A' }};
    Plotly.newPlot('chart-dependentes', [tDep], {...layoutBase, yaxis: {title: '', type: 'category'}}, configPlotly);

    const tCorr = {z: data.correlacao.z, x: data.correlacao.eixos, y: data.correlacao.eixos, type: 'heatmap', colorscale: [[0, '#FF453A'], [0.5, '#1c1c1e'], [1, '#32D74B']], zmin: -1, zmax: 1, textTemplate: "%{z}", showscale: true};
    Plotly.newPlot('chart-correlacao', [tCorr], {...layoutBase, margin: {t:20, l:120, r:20, b:60}, yaxis: { autorange: 'reversed' }}, configPlotly);

    const tbody = document.querySelector('#target-table tbody');
    tbody.innerHTML = '';
    data.target_list.forEach(c => {
        tbody.innerHTML += `<tr><td style="font-weight: bold; color: #F5F5F7;">#${c.colaborador_sk}</td>
        <td style="color: #86868B;">${c.departamento_nome_api}</td><td style="color: #86868B;">${c.perfil_comportamental}</td>
        <td style="color: ${c.risco > 70 ? '#FF453A' : '#32D74B'}; font-weight: bold;">${c.risco}%</td></tr>`;
    });
}

function toggleAdminPanel() {
    const p = document.getElementById('admin-panel'), d = document.getElementById('dashboard-content');
    if (p.style.display === 'none') { p.style.display = 'block'; d.style.display = 'none'; listarUsuarios(); }
    else { p.style.display = 'none'; d.style.display = 'grid'; }
}

async function listarUsuarios() {
    const users = await (await fetch('/api/users')).json();
    const tbody = document.querySelector('#users-table tbody'); tbody.innerHTML = '';
    users.forEach(u => { tbody.innerHTML += `<tr><td>${u.id}</td><td>${u.username}</td><td>${u.role}</td><td><button class="btn-danger" onclick="deletarUsuario(${u.id})">Remover</button></td></tr>`; });
}

async function criarUsuario() {
    const user = document.getElementById('new-user').value, pass = document.getElementById('new-pass').value, role = document.getElementById('new-role').value;
    if(user && pass) { await fetch('/api/users', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({username: user, password: pass, role: role})}); listarUsuarios(); }
}

async function deletarUsuario(id) { await fetch(`/api/users/${id}`, { method: 'DELETE' }); listarUsuarios(); }

function exportarTargetList() {
    if(!globalTargetList.length) return alert("Base vazia.");
    const ws = XLSX.utils.json_to_sheet(globalTargetList);
    XLSX.writeFile(XLSX.utils.book_append_sheet(XLSX.utils.book_new(), ws, "Risco"), "Enterprise_TargetList.xlsx");
}

async function dispararRetreino() {
    const btn = document.getElementById('btn-retrain');
    btn.innerText = "⏳ Treinando Megazord... Aguarde";
    btn.style.backgroundColor = "#FF9F0A";
    btn.disabled = true;

    try {
        const res = await fetch('/api/retrain', { method: 'POST' });
        if (res.ok) {
            const data = await res.json();
            alert(data.msg);
            carregarDashboard();
        } else { alert("❌ Falha crítica na esteira de MLOps. Verifique os logs."); }
    } catch (e) { console.error(e); alert("❌ Erro de conexão com o servidor."); }
    finally { btn.innerText = "🔄 Retreinar IA (Atualizar Base)"; btn.style.backgroundColor = "#32D74B"; btn.disabled = false; }
}