import createClient from 'openapi-fetch';
import type { paths, components } from '@pei/types';
import type { DiagramCanonical } from '../types/canonical';
import type { Violation } from '../stores/useValidationStore';

const API_BASE_URL = 'http://localhost:8000';

export const client = createClient<paths>({ baseUrl: API_BASE_URL });

export type Project = components['schemas']['Project'];
export type Diagram = components['schemas']['Diagram'];

export const diagramApi = {
    // Projects
    getProjects: async () => {
        const { data, error } = await client.GET('/projects', {});
        if (error) throw error;
        return data as Project[];
    },

    createProject: async (name: string, description?: string) => {
        const { data, error } = await client.POST('/projects', {
            body: { name, description }
        });
        if (error) throw error;
        return data as unknown as Project;
    },

    getProject: async (id: string) => {
        const { data, error } = await client.GET('/projects/{project_id}', {
            params: { path: { project_id: id } }
        });
        if (error) throw error;
        return data as unknown as Project;
    },

    updateProject: async (id: string, name: string, description?: string) => {
        const { data, error } = await client.PUT('/projects/{project_id}', {
            params: { path: { project_id: id } },
            body: { name, description }
        });
        if (error) throw error;
        return data as unknown as Project;
    },

    deleteProject: async (id: string) => {
        const { error } = await client.DELETE('/projects/{project_id}', {
            params: { path: { project_id: id } }
        });
        if (error) throw error;
    },

    // Diagrams
    getProjectDiagrams: async (projectId: string) => {
        const { data, error } = await client.GET('/projects/{project_id}/diagrams', {
            params: { path: { project_id: projectId } }
        });
        if (error) throw error;
        return data as unknown as Diagram[];
    },

    createDiagram: async (projectId: string, name: string, type: string = 'PID') => {
        const initialCanonical = {
            canonical_schema_version: 1,
            nodes: [],
            edges: []
        };

        const { data, error } = await client.POST('/projects/{project_id}/diagrams', {
            params: { path: { project_id: projectId } },
            body: {
                name,
                diagram_type: type,
                canonical_json: initialCanonical as any
            }
        });
        if (error) throw error;
        return data as unknown as Diagram;
    },

    getDiagram: async (id: string) => {
        const { data, error } = await client.GET('/diagrams/{diagram_id}', {
            params: { path: { diagram_id: id } }
        });
        if (error) throw error;
        return data as unknown as Diagram;
    },

    updateDiagram: async (id: string, canonical: DiagramCanonical) => {
        const { data, error } = await client.PUT('/diagrams/{diagram_id}', {
            params: { path: { diagram_id: id } },
            body: { canonical_json: canonical as any }
        });
        if (error) throw error;
        return data as unknown as Diagram;
    },

    exportDiagram: async (id: string, name: string) => {
        const res = await fetch(`${API_BASE_URL}/diagrams/${id}/export`);
        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `${name}.json`);
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);
    },

    validateDiagram: async (canonical: DiagramCanonical, rulesetId?: string) => {
        const payload: any = { diagram: canonical };
        if (rulesetId) {
            payload.ruleset_id = rulesetId;
        }
        const { data, error } = await client.POST('/validate', {
            body: payload
        });
        if (error) throw error;
        return data;
    },

    generateTemplate: async (templateId: string): Promise<{ diagram: DiagramCanonical }> => {
        const { data, error } = await client.POST('/generate/template', {
            body: { template_type: templateId }
        });
        if (error) throw error;
        return data as unknown as { diagram: DiagramCanonical };
    },

    autoRepair: async (diagram: DiagramCanonical, violations: Violation[]): Promise<{ diagram: DiagramCanonical, repairs: any[], remaining_violations: Violation[] }> => {
        const { data, error } = await client.POST('/generate/repair', {
            body: { diagram: diagram as any, violations: violations as any }
        });
        if (error) throw error;
        return data as unknown as { diagram: DiagramCanonical, repairs: any[], remaining_violations: Violation[] };
    }
};
