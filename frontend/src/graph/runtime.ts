import cytoscape from 'cytoscape';
import coseBilkent from 'cytoscape-cose-bilkent';
import fcose from 'cytoscape-fcose';

let initialized = false;

export function ensureGraphRuntime() {
  if (initialized) return;
  cytoscape.use(coseBilkent);
  cytoscape.use(fcose);
  window.cytoscape = cytoscape;
  initialized = true;
}
