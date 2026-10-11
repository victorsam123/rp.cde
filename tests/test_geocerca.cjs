const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

const html = fs.readFileSync('templates/ciudadano.html', 'utf8');
const start = html.indexOf('function puntoEnAnillo');
const end = html.indexOf('let miniMapa', start);
const context = {};
vm.createContext(context);
vm.runInContext(html.slice(start, end), context);
const geojson = JSON.parse(fs.readFileSync('static/ciudad_del_este_boundary.geojson', 'utf8'));
const points = [
    ['Centro CDE', -25.509, -54.611, true],
    ['Area 1', -25.516, -54.633, true],
    ['Km 9', -25.495, -54.691, true],
    ['Presidente Franco', -25.563, -54.611, false],
    ['Hernandarias', -25.407, -54.643, false],
    ['Minga Guazu', -25.505, -54.759, false],
    ['Foz do Iguacu', -25.547, -54.588, false],
];
for (const [name, lat, lon, expected] of points) {
    assert.equal(context.puntoEnGeoJson(lat, lon, geojson), expected, name);
}
const geometry = geojson.features[0].geometry;
const ring = geometry.type === 'Polygon' ? geometry.coordinates[0] : geometry.coordinates[0][0];
assert.equal(context.puntoEnGeoJson(ring[0][1], ring[0][0], geojson), true);
console.log('Geocerca del navegador: 7 ubicaciones y un punto del limite correctos.');
