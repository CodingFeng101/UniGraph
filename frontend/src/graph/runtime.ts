import cytoscape from 'cytoscape';
import coseBilkent from 'cytoscape-cose-bilkent';
import dagre from 'cytoscape-dagre';
import fcose from 'cytoscape-fcose';

let initialized = false;

export function ensureGraphRuntime() {
  if (initialized) return;
  cytoscape.use(coseBilkent);
  cytoscape.use(dagre);
  cytoscape.use(fcose);
  window.cytoscape = cytoscape;
  initialized = true;
}
