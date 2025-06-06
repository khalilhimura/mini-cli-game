import * as THREE from 'three';

let scene, camera, renderer;
const buildings = [];

function initScene() {
    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.set(5, 5, 5);
    camera.lookAt(0, 0, 0);

    const light = new THREE.DirectionalLight(0xffffff, 1);
    light.position.set(5, 10, 7.5);
    scene.add(light);

    const ambient = new THREE.AmbientLight(0x404040);
    scene.add(ambient);

    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.body.appendChild(renderer.domElement);

    const grid = new THREE.GridHelper(10, 10);
    scene.add(grid);

    animate();
    window.addEventListener('resize', onWindowResize);
}

function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
}

function animate() {
    requestAnimationFrame(animate);
    renderer.render(scene, camera);
}

function addBuilding(x, z) {
    const geometry = new THREE.BoxGeometry(1, 1, 1);
    const material = new THREE.MeshLambertMaterial({ color: 0x808080 });
    const cube = new THREE.Mesh(geometry, material);
    cube.position.set(x, 0.5, z);
    scene.add(cube);
    buildings.push({ x, z });
}

// Placeholder API functions
async function fetchState() {
    try {
        const res = await fetch('/api/state');
        return await res.json();
    } catch (e) {
        console.error('Failed to fetch state', e);
        return null;
    }
}

async function sendAction(action, payload) {
    try {
        const res = await fetch('/api/action', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action, payload })
        });
        return await res.json();
    } catch (e) {
        console.error('Failed to send action', e);
        return null;
    }
}

function updateUI(state) {
    const resDiv = document.getElementById('resources');
    if (!state) {
        resDiv.textContent = 'Offline';
        return;
    }
    resDiv.textContent = `Minerals: ${state.minerals} | Energy: ${state.energy}`;

    scene.children.filter(o => o.userData.building).forEach(o => scene.remove(o));
    state.buildings.forEach(b => addBuilding(b.x, b.z));
}

async function pollState() {
    const state = await fetchState();
    updateUI(state);
}

initScene();

setInterval(pollState, 2000);

document.getElementById('buildBtn').onclick = async () => {
    await sendAction('build', { type: 'mine' });
    pollState();
};

document.getElementById('upgradeBtn').onclick = async () => {
    await sendAction('upgrade', {});
    pollState();
};

document.getElementById('researchBtn').onclick = async () => {
    await sendAction('research', {});
    pollState();
};
