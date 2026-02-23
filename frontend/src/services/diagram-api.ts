import axios from 'axios';
import type { DiagramCanonical } from '../types/canonical';
import type { Violation } from '../stores/useValidationStore';

const API_BASE_URL = 'http://localhost:8000';

export interface Project {
    id: string;
    name: string;
    description?: string;
    created_at: string;
    updated_at: string;
}

export interface Diagram {
    id: string;
    project_id: string;
    name: string;
    diagram_type: string;
    version: number;
    status: string;
    canonical_json: DiagramCanonical;
    created_at: string;
    updated_at: string;
}

export const diagramApi = {
    // Projects
    getProjects: async () => {
        const response = await axios.get<Project[]>(`${API_BASE_URL}/projects`);
        return response.data;
    },

    createProject: async (name: string, description?: string) => {
        const response = await axios.post<Project>(`${API_BASE_URL}/projects`, { name, description });
        return response.data;
    },

    getProject: async (id: string) => {
        const response = await axios.get<Project>(`${API_BASE_URL}/projects/${id}`);
        return response.data;
    },

    updateProject: async (id: string, name: string, description?: string) => {
        const response = await axios.put<Project>(`${API_BASE_URL}/projects/${id}`, { name, description });
        return response.data;
    },

    deleteProject: async (id: string) => {
        await axios.delete(`${API_BASE_URL}/projects/${id}`);
    },

    // Diagrams
    getProjectDiagrams: async (projectId: string) => {
        const response = await axios.get<Diagram[]>(`${API_BASE_URL}/projects/${projectId}/diagrams`);
        return response.data;
    },

    createDiagram: async (projectId: string, name: string, type: string = 'PID') => {
        const initialCanonical: DiagramCanonical = {
            canonical_schema_version: 1,
            nodes: [],
            edges: []
        };

        const response = await axios.post<Diagram>(`${API_BASE_URL}/projects/${projectId}/diagrams`, {
            name,
            diagram_type: type,
            canonical_json: initialCanonical
        });
        return response.data;
    },

    getDiagram: async (id: string) => {
        const response = await axios.get<Diagram>(`${API_BASE_URL}/diagrams/${id}`);
        return response.data;
    },

    updateDiagram: async (id: string, canonical: DiagramCanonical) => {
        const response = await axios.put<Diagram>(`${API_BASE_URL}/diagrams/${id}`, {
            canonical_json: canonical
        });
        return response.data;
    },

    exportDiagram: async (id: string, name: string) => {
        const response = await axios.get(`${API_BASE_URL}/diagrams/${id}/export`, {
            responseType: 'blob'
        });

        // Trigger download
        const url = window.URL.createObjectURL(new Blob([JSON.stringify(response.data, null, 2)]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `${name}.json`);
        document.body.appendChild(link);
        link.click();
        link.remove();
    },

    validateDiagram: async (canonical: DiagramCanonical, rulesetId?: string) => {
        const payload: any = { diagram: canonical };
        if (rulesetId) {
            payload.ruleset_id = rulesetId;
        }
        const response = await axios.post(`${API_BASE_URL}/validate`, payload);
        return response.data;
    },

    generateTemplate: async (templateId: string): Promise<{ diagram: DiagramCanonical }> => {
        const response = await axios.post(`${API_BASE_URL}/generate/template`, {
            template_type: templateId
        });
        return response.data;
    },

    autoLayout: async (diagram: DiagramCanonical): Promise<{ diagram: DiagramCanonical }> => {
        const response = await axios.post(`${API_BASE_URL}/generate/layout`, {
            diagram: diagram
        });
        return response.data;
    },

    autoRepair: async (diagram: DiagramCanonical, violations: Violation[]): Promise<{ diagram: DiagramCanonical, repairs: any[], remaining_violations: Violation[] }> => {
        const response = await axios.post(`${API_BASE_URL}/generate/repair`, {
            diagram,
            violations
        });
        return response.data;
    }
};
