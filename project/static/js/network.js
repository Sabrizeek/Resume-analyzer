function renderSkillNetwork(data) {
    const container = document.getElementById('skill-network');
    if (!container) return;

    const options = {
        nodes: {
            shape: 'dot',
            size: 20,
            font: {
                size: 14,
                color: '#333'
            },
            borderWidth: 2,
        },
        edges: {
            width: 2,
            color: { inherit: 'from' },
            smooth: {
                type: 'continuous'
            }
        },
        physics: {
            enabled: true,
            solver: 'barnesHut',
            barnesHut: {
                gravitationalConstant: -10000,
                centralGravity: 0.1,
                springLength: 150
            }
        },
        interaction: {
            hover: true,
            tooltipDelay: 200
        },
        groups: {
            center: { color: { background: '#0a9396', border: '#005f73' }, font: { color: 'white' } },
            skill: { color: { background: '#e9d8a6', border: '#ee9b00' } },
            category: { color: { background: '#e9f5f5', border: '#94d2bd' } }
        }
    };

    const network = new vis.Network(container, data, options);
}