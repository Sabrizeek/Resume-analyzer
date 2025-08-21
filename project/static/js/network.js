/**
 * Enhanced Skill Network Visualization
 * Renders an interactive network graph showing skill relationships
 */

function renderSkillNetwork(data) {
    const container = document.getElementById('skill-network');
    if (!container || !data) {
        console.warn('Skill network container or data not available');
        return;
    }

    // Enhanced network options for better visualization
    const options = {
        nodes: {
            shape: 'dot',
            size: 25,
            font: {
                size: 14,
                face: 'Inter, sans-serif',
                color: '#2d3748',
                strokeWidth: 0,
                strokeColor: '#ffffff'
            },
            borderWidth: 3,
            shadow: {
                enabled: true,
                color: 'rgba(0,0,0,0.1)',
                size: 10,
                x: 5,
                y: 5
            },
            scaling: {
                min: 20,
                max: 40,
                label: {
                    enabled: true,
                    min: 14,
                    max: 18,
                    maxVisible: 20
                }
            }
        },
        edges: {
            width: 3,
            color: {
                color: '#e2e8f0',
                highlight: '#0a9396',
                hover: '#005f73',
                opacity: 0.8
            },
            smooth: {
                type: 'continuous',
                forceDirection: 'none',
                roundness: 0.5
            },
            shadow: {
                enabled: true,
                color: 'rgba(0,0,0,0.1)',
                size: 5,
                x: 2,
                y: 2
            },
            selectionWidth: 4,
            hoverWidth: 4
        },
        physics: {
            enabled: true,
            solver: 'forceAtlas2Based',
            forceAtlas2Based: {
                gravitationalConstant: -50,
                centralGravity: 0.01,
                springLength: 200,
                springConstant: 0.08,
                damping: 0.4,
                avoidOverlap: 0.5
            },
            stabilization: {
                enabled: true,
                iterations: 1000,
                updateInterval: 100,
                fit: true
            }
        },
        interaction: {
            hover: true,
            tooltipDelay: 200,
            zoomView: true,
            dragView: true,
            selectable: true,
            selectConnectedEdges: true,
            multiselect: false,
            navigationButtons: true,
            keyboard: {
                enabled: true,
                speed: {
                    x: 10,
                    y: 10,
                    zoom: 0.1
                }
            }
        },
        layout: {
            improvedLayout: true,
            hierarchical: {
                enabled: false,
                levelSeparation: 150,
                nodeSpacing: 100,
                treeSpacing: 200,
                blockShifting: true,
                edgeMinimization: true,
                parentCentralization: true,
                direction: 'UD',
                sortMethod: 'hubsize'
            }
        },
        groups: {
            center: {
                color: {
                    background: '#0a9396',
                    border: '#005f73',
                    highlight: {
                        background: '#0a9396',
                        border: '#005f73'
                    },
                    hover: {
                        background: '#0a9396',
                        border: '#005f73'
                    }
                },
                font: { color: '#ffffff', size: 16, face: 'Inter, sans-serif' },
                size: 30,
                shape: 'star'
            },
            skill: {
                color: {
                    background: '#ee9b00',
                    border: '#b45309',
                    highlight: {
                        background: '#f59e0b',
                        border: '#d97706'
                    },
                    hover: {
                        background: '#f59e0b',
                        border: '#d97706'
                    }
                },
                font: { color: '#ffffff', size: 14, face: 'Inter, sans-serif' },
                size: 25,
                shape: 'circle'
            },
            category: {
                color: {
                    background: '#e9d8a6',
                    border: '#9b6d00',
                    highlight: {
                        background: '#f4e4aa',
                        border: '#a17c1a'
                    },
                    hover: {
                        background: '#f4e4aa',
                        border: '#a17c1a'
                    }
                },
                font: { color: '#9b6d00', size: 13, face: 'Inter, sans-serif' },
                size: 22,
                shape: 'diamond'
            }
        }
    };

    try {
        // Create and configure the network
        const network = new vis.Network(container, data, options);
        
        // Enhanced event handling
        network.on('stabilizationProgress', function(params) {
            // Show stabilization progress
            const progress = Math.round(params.iterations / params.total * 100);
            if (progress < 100) {
                container.style.opacity = '0.7';
            }
        });

        network.on('stabilizationIterationsDone', function() {
            // Network is stable, show full opacity
            container.style.opacity = '1';
        });

        network.on('click', function(params) {
            if (params.nodes.length > 0) {
                const nodeId = params.nodes[0];
                const node = data.nodes.find(n => n.id === nodeId);
                if (node) {
                    highlightConnectedNodes(network, nodeId);
                }
            }
        });

        network.on('hoverNode', function(params) {
            // Add hover effects
            const node = data.nodes.find(n => n.id === params.node);
            if (node) {
                showNodeTooltip(node, params.event);
            }
        });

        network.on('blurNode', function() {
            hideNodeTooltip();
        });

        // Add zoom controls
        addZoomControls(container, network);

        // Auto-fit the network after a short delay
        setTimeout(() => {
            network.fit({
                animation: {
                    duration: 1000,
                    easingFunction: 'easeInOutQuad'
                }
            });
        }, 500);

        return network;

    } catch (error) {
        console.error('Error rendering skill network:', error);
        showNetworkError(container);
    }
}

/**
 * Highlight nodes connected to the selected node
 */
function highlightConnectedNodes(network, nodeId) {
    const connectedNodes = new Set();
    const connectedEdges = new Set();
    
    // Find all connected nodes and edges
    network.getConnectedNodes(nodeId).forEach(connectedId => {
        connectedNodes.add(connectedId);
        network.getConnectedEdges(connectedId).forEach(edgeId => {
            connectedEdges.add(edgeId);
        });
    });
    
    // Highlight connected elements
    network.selectNodes(Array.from(connectedNodes));
    network.selectEdges(Array.from(connectedEdges));
}

/**
 * Show tooltip for node on hover
 */
function showNodeTooltip(node, event) {
    // Remove existing tooltip
    hideNodeTooltip();
    
    const tooltip = document.createElement('div');
    tooltip.className = 'network-tooltip';
    tooltip.innerHTML = `
        <div class="tooltip-header">
            <strong>${node.label}</strong>
        </div>
        <div class="tooltip-content">
            <div>Type: ${node.group || 'Unknown'}</div>
            ${node.level ? `<div>Level: ${node.level}</div>` : ''}
            ${node.experience ? `<div>Experience: ${node.experience}</div>` : ''}
        </div>
    `;
    
    // Position tooltip
    tooltip.style.position = 'absolute';
    tooltip.style.left = (event.center.x + 10) + 'px';
    tooltip.style.top = (event.center.y - 10) + 'px';
    tooltip.style.zIndex = '1000';
    
    document.body.appendChild(tooltip);
}

/**
 * Hide the node tooltip
 */
function hideNodeTooltip() {
    const existingTooltip = document.querySelector('.network-tooltip');
    if (existingTooltip) {
        existingTooltip.remove();
    }
}

/**
 * Add zoom controls to the network container
 */
function addZoomControls(container, network) {
    const controls = document.createElement('div');
    controls.className = 'network-controls';
    controls.innerHTML = `
        <button class="zoom-btn zoom-in" title="Zoom In">+</button>
        <button class="zoom-btn zoom-out" title="Zoom Out">−</button>
        <button class="zoom-btn zoom-fit" title="Fit to View">⌂</button>
        <button class="zoom-btn zoom-reset" title="Reset View">↺</button>
    `;
    
    // Style controls
    controls.style.cssText = `
        position: absolute;
        top: 10px;
        right: 10px;
        display: flex;
        flex-direction: column;
        gap: 5px;
        z-index: 100;
    `;
    
    // Add event listeners
    controls.querySelector('.zoom-in').addEventListener('click', () => {
        network.moveTo({ scale: network.getScale() * 1.2 });
    });
    
    controls.querySelector('.zoom-out').addEventListener('click', () => {
        network.moveTo({ scale: network.getScale() * 0.8 });
    });
    
    controls.querySelector('.zoom-fit').addEventListener('click', () => {
        network.fit({ animation: { duration: 500 } });
    });
    
    controls.querySelector('.zoom-reset').addEventListener('click', () => {
        network.moveTo({ scale: 1, position: { x: 0, y: 0 } });
    });
    
    container.appendChild(controls);
}

/**
 * Show error message when network fails to render
 */
function showNetworkError(container) {
    container.innerHTML = `
        <div class="network-error">
            <div class="error-icon">⚠️</div>
            <h4>Network Visualization Unavailable</h4>
            <p>Unable to render the skill network. This may be due to insufficient data or a technical issue.</p>
        </div>
    `;
    
    // Add error styling
    const style = document.createElement('style');
    style.textContent = `
        .network-error {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100%;
            text-align: center;
            color: #6b7280;
            padding: 2rem;
        }
        .network-error .error-icon {
            font-size: 3rem;
            margin-bottom: 1rem;
        }
        .network-error h4 {
            margin: 0 0 0.5rem 0;
            color: #374151;
        }
        .network-error p {
            margin: 0;
            font-size: 0.875rem;
            line-height: 1.5;
        }
    `;
    document.head.appendChild(style);
}

/**
 * Export network data for debugging
 */
function exportNetworkData(data) {
    if (console && console.log) {
        console.log('Network Data:', data);
    }
}

/**
 * Validate network data structure
 */
function validateNetworkData(data) {
    if (!data || typeof data !== 'object') {
        return false;
    }
    
    if (!Array.isArray(data.nodes) || !Array.isArray(data.edges)) {
        return false;
    }
    
    if (data.nodes.length === 0) {
        return false;
    }
    
    return true;
}

// Export functions for potential external use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        renderSkillNetwork,
        validateNetworkData,
        exportNetworkData
    };
}