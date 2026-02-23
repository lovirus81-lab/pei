import { create } from 'zustand';
import { type Project, type Diagram, diagramApi } from '../services/diagram-api';

interface ProjectState {
    projects: Project[];
    currentProject: Project | null;
    currentDiagram: Diagram | null;
    isLoading: boolean;
    error: string | null;

    fetchProjects: () => Promise<void>;
    createProject: (name: string, description?: string) => Promise<Project | undefined>;
    selectProject: (id: string) => Promise<void>;
    updateProject: (id: string, name: string, description?: string) => Promise<void>;
    deleteProject: (id: string) => Promise<void>;
    createDiagram: (name: string) => Promise<Diagram | undefined>;
    loadDiagram: (id: string) => Promise<void>;
    saveCurrentDiagram: (canonical: any) => Promise<void>;
}

export const useProjectStore = create<ProjectState>((set, get) => ({
    projects: [],
    currentProject: null,
    currentDiagram: null,
    isLoading: false,
    error: null,

    fetchProjects: async () => {
        set({ isLoading: true });
        try {
            const projects = await diagramApi.getProjects();
            set({ projects, isLoading: false });
        } catch (err: any) {
            set({ error: err.message, isLoading: false });
        }
    },

    createProject: async (name: string, description?: string) => {
        set({ isLoading: true });
        try {
            const project = await diagramApi.createProject(name, description);
            set(state => ({
                projects: [...state.projects, project],
                currentProject: project,
                isLoading: false,
                error: null
            }));
            return project;
        } catch (err: any) {
            console.error("Create project failed:", err);
            set({ error: err.message, isLoading: false });
            throw err;
        }
    },

    selectProject: async (id: string) => {
        set({ isLoading: true });
        try {
            const project = await diagramApi.getProject(id);
            const diagrams = await diagramApi.getProjectDiagrams(id);
            let currentDiagram = null;
            if (diagrams.length > 0) {
                currentDiagram = await diagramApi.getDiagram(diagrams[0].id);
            }
            set({ currentProject: project, currentDiagram, isLoading: false });
        } catch (err: any) {
            set({ error: err.message, isLoading: false });
        }
    },

    updateProject: async (id: string, name: string, description?: string) => {
        try {
            const updatedProject = await diagramApi.updateProject(id, name, description);
            set(state => ({
                projects: state.projects.map(p => p.id === id ? updatedProject : p),
                currentProject: state.currentProject?.id === id ? updatedProject : state.currentProject
            }));
        } catch (err: any) {
            set({ error: err.message });
            throw err;
        }
    },

    deleteProject: async (id: string) => {
        try {
            await diagramApi.deleteProject(id);
            set(state => ({
                projects: state.projects.filter(p => p.id !== id),
                currentProject: state.currentProject?.id === id ? null : state.currentProject,
                currentDiagram: state.currentProject?.id === id ? null : state.currentDiagram
            }));
        } catch (err: any) {
            set({ error: err.message });
            throw err;
        }
    },

    createDiagram: async (name: string) => {
        const { currentProject } = get();
        if (!currentProject) return;

        set({ isLoading: true });
        try {
            const diagram = await diagramApi.createDiagram(currentProject.id, name);
            set({ currentDiagram: diagram, isLoading: false });
            return diagram;
        } catch (err: any) {
            set({ error: err.message, isLoading: false });
            throw err;
        }
    },

    loadDiagram: async (id: string) => {
        set({ isLoading: true });
        try {
            const diagram = await diagramApi.getDiagram(id);
            set({ currentDiagram: diagram, isLoading: false });
        } catch (err: any) {
            set({ error: err.message, isLoading: false });
        }
    },

    saveCurrentDiagram: async (canonical: any) => {
        const { currentDiagram } = get();
        if (!currentDiagram) return;

        // Optimistic update or waiting? Let's wait.
        try {
            const updated = await diagramApi.updateDiagram(currentDiagram.id, canonical);
            set({ currentDiagram: updated });
            console.log('Saved version:', updated.version);
        } catch (err: any) {
            console.error('Failed to save', err);
            // set({ error: err.message });
        }
    }
}));
