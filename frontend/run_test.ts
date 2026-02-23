import { toReactFlow } from './src/converters/to-reactflow';
import { toCanonical } from './src/converters/to-canonical';

async function main() {
    const d = await fetch('http://localhost:8000/generate/template', {
        method: 'POST', body: JSON.stringify({ template_type: 'simple_pump_loop' }),
        headers: { 'Content-Type': 'application/json' }
    }).then(r => r.json());

    const { nodes, edges } = toReactFlow(d.diagram);
    const newCanonical = toCanonical(nodes, edges, { id: 'test', name: 'test', diagram_type: 'pid' });

    const res = await fetch('http://localhost:8000/validate', {
        method: 'POST', body: JSON.stringify({ diagram: newCanonical }),
        headers: { 'Content-Type': 'application/json' }
    }).then(r => r.json());

    console.log("Violations:");
    res.violations.forEach((v: any) => {
        console.log(`- ${v.rule_code}: ${v.message}`);
    });
} main();
