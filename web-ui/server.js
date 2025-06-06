const express = require('express');
const path = require('path');
const app = express();

app.use(express.json());
app.use(express.static(__dirname));

// Simple in-memory game state
const state = {
    minerals: 100,
    energy: 50,
    buildings: []
};

app.get('/api/state', (req, res) => {
    res.json(state);
});

app.post('/api/action', (req, res) => {
    const { action, payload } = req.body;
    if (action === 'build') {
        state.buildings.push({ x: Math.random()*4-2, z: Math.random()*4-2, type: payload.type });
        state.minerals -= 10;
    } else if (action === 'upgrade') {
        state.energy -= 5;
    } else if (action === 'research') {
        state.minerals -= 5;
        state.energy -= 5;
    }
    res.json({ success: true });
});

app.listen(3000, () => console.log('Web UI running on http://localhost:3000'));
