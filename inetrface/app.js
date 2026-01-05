// === Variables Globales ===
let graphData = {
    nodes: [],
    edges: []
};
let network = null;
let communities = [];

// Couleurs pour les communautés (grayscale + accent)
const COLORS = [
    '#1a1a1a', '#4a4a4a', '#7a7a7a', '#2d2d2d', '#5d5d5d',
    '#3d3d3d', '#6d6d6d', '#0d0d0d', '#8a8a8a', '#9a9a9a'
];

// === Initialisation ===
document.addEventListener('DOMContentLoaded', function() {
    setupFileUpload();
});

// === Gestion du fichier CSV ===
function setupFileUpload() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');

    // Click sur la zone
    uploadArea.addEventListener('click', () => fileInput.click());

    // Drag & Drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        const file = e.dataTransfer.files[0];
        if (file && file.name.endsWith('.csv')) {
            handleFile(file);
        }
    });

    // Sélection de fichier
    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            handleFile(file);
        }
    });
}

function handleFile(file) {
    const reader = new FileReader();
    
    reader.onload = function(e) {
        const content = e.target.result;
        parseCSV(content);
        
        // Afficher le nom du fichier
        document.getElementById('fileInfo').style.display = 'flex';
        document.getElementById('fileName').textContent = file.name;
        document.getElementById('uploadArea').style.display = 'none';
    };
    
    reader.readAsText(file);
}

function resetUpload() {
    document.getElementById('fileInfo').style.display = 'none';
    document.getElementById('uploadArea').style.display = 'block';
    document.getElementById('fileInput').value = '';
    
    // Cacher les sections
    document.getElementById('statsSection').style.display = 'none';
    document.getElementById('actionsSection').style.display = 'none';
    document.getElementById('graphSection').style.display = 'none';
    document.getElementById('communitiesSection').style.display = 'none';
    document.getElementById('analysisSection').style.display = 'none';
    
    graphData = { nodes: [], edges: [] };
    communities = [];
}

// === Parsing du CSV ===
function parseCSV(content) {
    const lines = content.trim().split('\n');
    const nodesSet = new Set();
    const edges = [];

    // Ignorer la première ligne (header)
    for (let i = 1; i < lines.length; i++) {
        const line = lines[i].trim();
        if (!line) continue;
        
        const parts = line.split(',');
        if (parts.length >= 2) {
            const user1 = parts[0].trim();
            const user2 = parts[1].trim();
            
            nodesSet.add(user1);
            nodesSet.add(user2);
            edges.push({ from: user1, to: user2 });
        }
    }

    // Créer les noeuds
    const nodes = Array.from(nodesSet).map(name => ({
        id: name,
        label: name,
        color: '#4ECDC4'
    }));

    graphData = { nodes, edges };
    
    // Afficher les stats et le graphe
    updateStats();
    showOriginalGraph();
    
    // Afficher les sections
    document.getElementById('statsSection').style.display = 'block';
    document.getElementById('actionsSection').style.display = 'flex';
    document.getElementById('graphSection').style.display = 'block';
}

// === Statistiques ===
function updateStats() {
    document.getElementById('statNodes').textContent = graphData.nodes.length;
    document.getElementById('statEdges').textContent = graphData.edges.length;
    document.getElementById('statCommunities').textContent = communities.length || '-';
    document.getElementById('statModularity').textContent = communities.length ? 
        calculateModularity().toFixed(3) : '-';
}

// === Visualisation du graphe ===
function showOriginalGraph() {
    // Réinitialiser les couleurs
    const nodes = graphData.nodes.map(n => ({
        ...n,
        color: '#333333'
    }));
    
    renderGraph(nodes, graphData.edges);
    document.getElementById('legend').innerHTML = '';
    communities = [];
    updateStats();
}

function renderGraph(nodes, edges) {
    const container = document.getElementById('graphContainer');
    
    const data = {
        nodes: new vis.DataSet(nodes),
        edges: new vis.DataSet(edges)
    };
    
    const options = {
        nodes: {
            shape: 'dot',
            size: 20,
            font: {
                size: 14,
                color: '#333333',
                face: 'Segoe UI, sans-serif',
                strokeWidth: 3,
                strokeColor: '#ffffff'
            },
            borderWidth: 2,
            borderWidthSelected: 3,
            shadow: {
                enabled: true,
                size: 8,
                x: 2,
                y: 2
            }
        },
        edges: {
            width: 1.5,
            color: {
                color: '#cccccc',
                highlight: '#333333',
                hover: '#999999'
            },
            smooth: {
                type: 'continuous',
                roundness: 0.5
            }
        },
        physics: {
            enabled: true,
            stabilization: {
                enabled: true,
                iterations: 200
            },
            barnesHut: {
                gravitationalConstant: -4000,
                springLength: 120,
                springConstant: 0.04,
                damping: 0.09
            }
        },
        interaction: {
            hover: true,
            tooltipDelay: 100,
            zoomView: true,
            dragView: true,
            navigationButtons: false,
            keyboard: {
                enabled: true
            }
        }
    };
    
    network = new vis.Network(container, data, options);
    
    // Fit to view after stabilization
    network.once('stabilizationIterationsDone', function() {
        network.fit({
            animation: {
                duration: 500,
                easingFunction: 'easeInOutQuad'
            }
        });
    });
}

// === Détection de communautés ===
function detectCommunities(algorithm) {
    if (algorithm === 'louvain') {
        communities = louvainAlgorithm();
    } else {
        communities = girvanNewmanAlgorithm();
    }
    
    // Colorier les noeuds par communauté
    const coloredNodes = graphData.nodes.map(node => {
        const commIndex = findCommunity(node.id);
        return {
            ...node,
            color: COLORS[commIndex % COLORS.length]
        };
    });
    
    renderGraph(coloredNodes, graphData.edges);
    updateLegend();
    displayCommunities();
    displayAnalysis();
    updateStats();
    
    document.getElementById('communitiesSection').style.display = 'block';
    document.getElementById('analysisSection').style.display = 'block';
}

// === Algorithme de Louvain (simplifié) ===
function louvainAlgorithm() {
    // Construction du graphe
    const adjacency = buildAdjacencyList();
    const nodes = Object.keys(adjacency);
    
    // Initialisation: chaque noeud dans sa propre communauté
    let partition = {};
    nodes.forEach((node, i) => partition[node] = i);
    
    let improved = true;
    let iterations = 0;
    const maxIterations = 100;
    
    while (improved && iterations < maxIterations) {
        improved = false;
        iterations++;
        
        for (const node of nodes) {
            const currentComm = partition[node];
            let bestComm = currentComm;
            let bestGain = 0;
            
            // Trouver les communautés voisines
            const neighborComms = new Set();
            for (const neighbor of adjacency[node]) {
                neighborComms.add(partition[neighbor]);
            }
            
            // Essayer chaque communauté voisine
            for (const comm of neighborComms) {
                if (comm === currentComm) continue;
                
                const gain = calculateModularityGain(node, comm, partition, adjacency);
                if (gain > bestGain) {
                    bestGain = gain;
                    bestComm = comm;
                }
            }
            
            if (bestComm !== currentComm) {
                partition[node] = bestComm;
                improved = true;
            }
        }
    }
    
    // Convertir en liste de communautés
    return partitionToCommunities(partition);
}

// === Algorithme de Girvan-Newman (simplifié) ===
function girvanNewmanAlgorithm() {
    // Copie des arêtes
    let edges = [...graphData.edges];
    const nodes = graphData.nodes.map(n => n.id);
    
    // Nombre de communautés souhaité
    const targetCommunities = Math.min(5, Math.ceil(nodes.length / 4));
    
    while (edges.length > 0) {
        const components = findConnectedComponents(nodes, edges);
        
        if (components.length >= targetCommunities) {
            return components;
        }
        
        // Calculer la betweenness de chaque arête
        const betweenness = calculateEdgeBetweenness(nodes, edges);
        
        // Supprimer l'arête avec la plus grande betweenness
        let maxBetweenness = 0;
        let edgeToRemove = 0;
        
        for (let i = 0; i < edges.length; i++) {
            const key = `${edges[i].from}-${edges[i].to}`;
            const keyReverse = `${edges[i].to}-${edges[i].from}`;
            const bet = betweenness[key] || betweenness[keyReverse] || 0;
            
            if (bet > maxBetweenness) {
                maxBetweenness = bet;
                edgeToRemove = i;
            }
        }
        
        edges.splice(edgeToRemove, 1);
    }
    
    // Chaque noeud dans sa propre communauté si aucune arête
    return nodes.map(n => new Set([n]));
}

// === Fonctions utilitaires ===
function buildAdjacencyList() {
    const adj = {};
    
    graphData.nodes.forEach(n => adj[n.id] = []);
    
    graphData.edges.forEach(e => {
        adj[e.from].push(e.to);
        adj[e.to].push(e.from);
    });
    
    return adj;
}

function calculateModularityGain(node, targetComm, partition, adjacency) {
    let gain = 0;
    
    for (const neighbor of adjacency[node]) {
        if (partition[neighbor] === targetComm) {
            gain += 1;
        }
    }
    
    return gain;
}

function partitionToCommunities(partition) {
    const commMap = {};
    
    for (const [node, comm] of Object.entries(partition)) {
        if (!commMap[comm]) {
            commMap[comm] = new Set();
        }
        commMap[comm].add(node);
    }
    
    return Object.values(commMap);
}

function findConnectedComponents(nodes, edges) {
    const visited = new Set();
    const components = [];
    
    // Construire la liste d'adjacence
    const adj = {};
    nodes.forEach(n => adj[n] = []);
    edges.forEach(e => {
        adj[e.from].push(e.to);
        adj[e.to].push(e.from);
    });
    
    // BFS pour trouver les composantes
    for (const node of nodes) {
        if (visited.has(node)) continue;
        
        const component = new Set();
        const queue = [node];
        
        while (queue.length > 0) {
            const current = queue.shift();
            if (visited.has(current)) continue;
            
            visited.add(current);
            component.add(current);
            
            for (const neighbor of adj[current]) {
                if (!visited.has(neighbor)) {
                    queue.push(neighbor);
                }
            }
        }
        
        components.push(component);
    }
    
    return components;
}

function calculateEdgeBetweenness(nodes, edges) {
    const betweenness = {};
    
    // Initialiser
    edges.forEach(e => {
        betweenness[`${e.from}-${e.to}`] = 0;
    });
    
    // Construire la liste d'adjacence
    const adj = {};
    nodes.forEach(n => adj[n] = []);
    edges.forEach(e => {
        adj[e.from].push(e.to);
        adj[e.to].push(e.from);
    });
    
    // Pour chaque paire de noeuds, trouver le plus court chemin
    for (const source of nodes) {
        const distances = {};
        const predecessors = {};
        const queue = [source];
        
        nodes.forEach(n => {
            distances[n] = Infinity;
            predecessors[n] = [];
        });
        distances[source] = 0;
        
        // BFS
        while (queue.length > 0) {
            const current = queue.shift();
            
            for (const neighbor of adj[current]) {
                if (distances[neighbor] === Infinity) {
                    distances[neighbor] = distances[current] + 1;
                    queue.push(neighbor);
                }
                
                if (distances[neighbor] === distances[current] + 1) {
                    predecessors[neighbor].push(current);
                }
            }
        }
        
        // Calculer la contribution aux arêtes
        for (const target of nodes) {
            if (target === source) continue;
            
            for (const pred of predecessors[target]) {
                const key1 = `${pred}-${target}`;
                const key2 = `${target}-${pred}`;
                
                if (betweenness[key1] !== undefined) {
                    betweenness[key1] += 1;
                } else if (betweenness[key2] !== undefined) {
                    betweenness[key2] += 1;
                }
            }
        }
    }
    
    return betweenness;
}

function findCommunity(nodeId) {
    for (let i = 0; i < communities.length; i++) {
        if (communities[i].has(nodeId)) {
            return i;
        }
    }
    return 0;
}

function calculateModularity() {
    if (communities.length === 0) return 0;
    
    const m = graphData.edges.length;
    if (m === 0) return 0;
    
    const adj = buildAdjacencyList();
    let Q = 0;
    
    for (const community of communities) {
        const members = Array.from(community);
        
        for (const i of members) {
            for (const j of members) {
                const aij = adj[i].includes(j) ? 1 : 0;
                const ki = adj[i].length;
                const kj = adj[j].length;
                
                Q += aij - (ki * kj) / (2 * m);
            }
        }
    }
    
    return Q / (2 * m);
}

// === Affichage ===
function updateLegend() {
    const legend = document.getElementById('legend');
    legend.innerHTML = '';
    
    communities.forEach((comm, i) => {
        const item = document.createElement('div');
        item.className = 'legend-item';
        item.innerHTML = `
            <span class="legend-color" style="background: ${COLORS[i % COLORS.length]}"></span>
            <span>Communauté ${i + 1} (${comm.size} membres)</span>
        `;
        legend.appendChild(item);
    });
}

function displayCommunities() {
    const grid = document.getElementById('communitiesGrid');
    grid.innerHTML = '';
    
    communities.forEach((comm, i) => {
        const card = document.createElement('div');
        card.className = 'community-card';
        card.style.borderLeftColor = COLORS[i % COLORS.length];
        
        const members = Array.from(comm).sort();
        const membersHtml = members.map(m => 
            `<span class="member-tag">${m}</span>`
        ).join('');
        
        card.innerHTML = `
            <h3>Communauté ${i + 1}</h3>
            <div class="community-members">${membersHtml}</div>
        `;
        
        grid.appendChild(card);
    });
}

function displayAnalysis() {
    const tbody = document.getElementById('analysisTableBody');
    tbody.innerHTML = '';
    
    const adj = buildAdjacencyList();
    
    communities.forEach((comm, i) => {
        const members = Array.from(comm);
        const size = members.length;
        
        // Arêtes internes
        let internal = 0;
        for (const m1 of members) {
            for (const m2 of members) {
                if (m1 < m2 && adj[m1].includes(m2)) {
                    internal++;
                }
            }
        }
        
        // Arêtes externes
        let external = 0;
        for (const member of members) {
            for (const neighbor of adj[member]) {
                if (!comm.has(neighbor)) {
                    external++;
                }
            }
        }
        external = external / 2; // Comptées deux fois
        
        // Densité
        const possibleEdges = size * (size - 1) / 2;
        const density = possibleEdges > 0 ? (internal / possibleEdges).toFixed(2) : '0.00';
        
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>
                <span class="legend-color" style="background: ${COLORS[i % COLORS.length]}; display: inline-block; margin-right: 8px;"></span>
                Communauté ${i + 1}
            </td>
            <td>${size}</td>
            <td>${internal}</td>
            <td>${Math.round(external)}</td>
            <td>${density}</td>
        `;
        
        tbody.appendChild(row);
    });
}
