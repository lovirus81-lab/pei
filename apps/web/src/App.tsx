import { useEffect, useState, useRef } from 'react';
import { Toaster } from 'react-hot-toast';
import type { Project } from './services/diagram-api';
import type { DiagramCanonical } from './types/canonical';
import PidCanvas from './components/canvas/PidCanvas';
import SymbolPalette from './components/panels/SymbolPalette';
import ProblemsPanel from './components/panels/ProblemsPanel';
import ValidationPanel from './components/panels/ValidationPanel';
import { ToastProvider, useToast } from './components/ui/Toast';
import { useProjectStore } from './stores/project-store';
import { useCanvasStore } from './stores/canvas-store';
import { useValidationStore } from './stores/useValidationStore';
import TemplateLoader from './components/panels/TemplateLoader';
import { TooltipProvider } from './components/ui/tooltip';
import { ResizableHandle, ResizablePanel, ResizablePanelGroup } from './components/ui/resizable';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
import PropertyPanel from './components/panels/PropertyPanel';

function ProjectCard({ project }: { project: Project }) {
  const { selectProject, updateProject, deleteProject } = useProjectStore();
  const { addToast } = useToast();

  const [isEditing, setIsEditing] = useState(false);
  const [editName, setEditName] = useState(project.name);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isEditing && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isEditing]);

  const handleSave = async () => {
    if (editName.trim() === '') {
      setEditName(project.name);
      setIsEditing(false);
      return;
    }
    if (editName !== project.name) {
      try {
        await updateProject(project.id, editName, project.description ?? undefined);
        addToast("프로젝트명이 변경되었습니다", "success");
      } catch (e) {
        addToast("이름 변경 실패", "error");
        setEditName(project.name);
      }
    }
    setIsEditing(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSave();
    } else if (e.key === 'Escape') {
      setEditName(project.name);
      setIsEditing(false);
    }
  };

  const handleDelete = async (e: React.MouseEvent) => {
    e.stopPropagation();
    if (window.confirm(`'${project.name}' 프로젝트를 삭제하시겠습니까?`)) {
      try {
        await deleteProject(project.id);
        addToast("삭제되었습니다", "success");
      } catch (err) {
        addToast("삭제 실패", "error");
      }
    }
  };

  return (
    <div
      onClick={() => !isEditing && selectProject(project.id)}
      className="p-6 bg-white border border-gray-200 rounded-lg shadow-sm cursor-pointer hover:shadow-md hover:border-blue-500 transition-all relative group"
    >
      <div className="flex justify-between items-start mb-2">
        {isEditing ? (
          <input
            ref={inputRef}
            value={editName}
            onChange={e => setEditName(e.target.value)}
            onBlur={handleSave}
            onKeyDown={handleKeyDown}
            onClick={e => e.stopPropagation()}
            className="text-lg font-bold text-gray-800 border-b-2 border-blue-500 focus:outline-none w-full mr-6"
          />
        ) : (
          <h3
            onDoubleClick={(e) => { e.stopPropagation(); setIsEditing(true); }}
            className="text-lg font-bold text-gray-800 flex-1 truncate pr-2 group-hover:text-blue-600"
          >
            {project.name}
          </h3>
        )}

        <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
          {!isEditing && (
            <button
              onClick={(e) => { e.stopPropagation(); setIsEditing(true); }}
              className="text-gray-400 hover:text-blue-500 transition-colors"
              title="Rename Project"
            >
              ✏️
            </button>
          )}
          <button
            onClick={handleDelete}
            className="text-gray-400 hover:text-red-500 transition-colors"
            title="Delete Project"
          >
            🗑️
          </button>
        </div>
      </div>

      <p className="text-sm text-gray-500 line-clamp-2">{project.description || "No description"}</p>
      <div className="mt-4 flex justify-between items-center text-xs text-gray-400">
        <span>ID: {project.id.substring(0, 8)}...</span>
        <span>{new Date(project.created_at).toLocaleDateString()}</span>
      </div>
    </div>
  );
}

function AppContent() {
  const {
    projects,
    currentProject,
    currentDiagram,
    createProject,
    createDiagram,
    saveCurrentDiagram,
    isLoading
  } = useProjectStore();

  const { toCanonical } = useCanvasStore();
  const { runValidation, isValidating } = useValidationStore();
  const { addToast } = useToast();

  useEffect(() => {
    useProjectStore.getState().fetchProjects();
  }, []);

  // Sync canvas store when current diagram changes
  useEffect(() => {
    if (currentDiagram) {
      useCanvasStore.getState().loadCanonical(currentDiagram.canonical_json as unknown as DiagramCanonical);
      useValidationStore.getState().clearReport();
    }
  }, [currentDiagram]);

  const handleCreateProject = async () => {
    const name = prompt("Enter project name:");
    if (name) {
      try {
        await createProject(name);
        // Automatically create a default diagram to enter the workspace
        await createDiagram("Main P&ID");
        addToast("Project and default diagram created", "success");
      } catch (e) {
        addToast("Failed to create project", "error");
      }
    }
  };

  const handleCreateDiagram = async () => {
    const name = prompt("Enter diagram name:");
    if (name) {
      await createDiagram(name);
      addToast("Diagram created", "success");
    }
  };

  const handleSave = async () => {
    const canonical = toCanonical();
    await saveCurrentDiagram(canonical);
    addToast("Diagram saved successfully", "success");
  };

  const handleValidate = async () => {
    const canonical = toCanonical();
    if (canonical.nodes.length === 0) {
      addToast("캔버스에 설비를 먼저 배치하세요", "warning");
      return;
    }
    await runValidation(canonical);
    addToast("Validation complete", "info");
  };

  const handleExport = async () => {
    if (currentDiagram) {
      try {
        const canonical = toCanonical();
        const blob = new Blob([JSON.stringify(canonical, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `${currentDiagram.name}.json`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
        addToast("Export complete", "success");
      } catch (e) {
        addToast("Export failed", "error");
      }
    }
  };

  const handleClear = () => {
    if (window.confirm("캔버스를 초기화하시겠습니까? (이 작업은 되돌릴 수 없습니다)")) {
      // Clear Zustand stores directly
      useCanvasStore.setState({ nodes: [], edges: [] });
      clearReport();
      addToast("캔버스가 초기화되었습니다", "info");
    }
  };

  return (
    <div className="h-screen w-screen flex flex-col overflow-hidden bg-gray-50">
      {/* Header */}
      <header className="h-12 bg-gray-800 text-white flex items-center px-4 justify-between shrink-0 z-10 shadow-md">
        <div className="font-bold flex items-center gap-4">
          <span className="text-xl tracking-tight">PEI Prototype</span>
          <div className="h-4 w-px bg-gray-600"></div>
          <span className="text-gray-300 text-sm font-medium">
            {currentProject ? currentProject.name : 'Select Project'}
            {currentDiagram ? ` / ${currentDiagram.name} (v${currentDiagram.version})` : ''}
          </span>
        </div>
        <div className="flex gap-3">
          {!currentProject && (
            <button onClick={handleCreateProject} className="px-3 py-1 bg-blue-600 rounded hover:bg-blue-500 text-sm transition-colors">
              + New Project
            </button>
          )}
          {currentProject && !currentDiagram && (
            <button onClick={handleCreateDiagram} className="px-3 py-1 bg-green-600 rounded hover:bg-green-500 text-sm transition-colors">
              + New Diagram
            </button>
          )}
          {currentDiagram && (
            <>
              <TemplateLoader />
              <button disabled={isValidating} onClick={handleValidate} className="px-3 py-1 bg-yellow-600 rounded hover:bg-yellow-500 disabled:opacity-50 text-sm transition-colors font-medium flex items-center gap-2">
                {isValidating ? (
                  <>
                    <svg className="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Validating...
                  </>
                ) : 'Validate'}
              </button>
              <button onClick={handleClear} className="px-3 py-1 bg-red-600 rounded hover:bg-red-500 text-sm transition-colors font-medium">
                Clear
              </button>
              <button onClick={handleExport} className="px-3 py-1 bg-gray-600 rounded hover:bg-gray-500 text-sm transition-colors font-medium border border-gray-500">
                Export JSON
              </button>
              <button onClick={handleSave} className="px-3 py-1 bg-indigo-600 rounded hover:bg-indigo-500 text-sm transition-colors font-medium">
                Save Diagram
              </button>
            </>
          )}
        </div>
      </header>

      {/* Main Layout */}
      <div className="flex-1 flex overflow-hidden">
        {/* Project Selector (if no project selected) */}
        {!currentProject && (
          <div className="flex-1 p-8 flex flex-col items-center justify-center">
            <h2 className="text-2xl font-bold mb-6 text-gray-700">Select a Project</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 w-full max-w-4xl">
              {projects.map(p => (
                <ProjectCard key={p.id} project={p} />
              ))}
            </div>
            {projects.length === 0 && !isLoading && (
              <div className="mt-8 text-gray-500 text-lg">No projects found. Create one to start.</div>
            )}
            {isLoading && <div className="mt-8 text-blue-500">Loading projects...</div>}
          </div>
        )}

        {/* Workspace */}
        {currentProject && !currentDiagram && (
          <div className="flex-1 flex items-center justify-center bg-gray-100 text-gray-400">
            <div className="text-center">
              <p className="text-lg mb-4">No diagram selected</p>
              <button onClick={handleCreateDiagram} className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-500">
                Create New Diagram
              </button>
            </div>
          </div>
        )}

        {currentDiagram && (
          <>
            <SymbolPalette />
            <div className="flex-1 flex flex-col w-full relative h-full bg-gray-100">
              <div className="flex-1 relative">
                <PidCanvas />
              </div>
            </div>
            {/* Right Side Panel */}
            <div className="w-[340px] border-l border-gray-200 bg-white flex flex-col h-full shrink-0 shadow-sm z-10">
              <ResizablePanelGroup orientation="vertical">
                <ResizablePanel defaultSize={50} minSize={20}>
                  <PropertyPanel />
                </ResizablePanel>
                <ResizableHandle withHandle />
                <ResizablePanel defaultSize={50} minSize={20} className="flex flex-col">
                  <Tabs defaultValue="validation" className="w-full h-full flex flex-col pt-1">
                    <TabsList className="w-full justify-start rounded-none border-b border-gray-200 bg-transparent p-0 h-10 px-3 gap-3 flex-shrink-0">
                      <TabsTrigger value="validation" className="text-xs h-8 data-[state=active]:border-b-2 data-[state=active]:border-blue-600 data-[state=active]:shadow-none rounded-none px-1">Validation</TabsTrigger>
                      <TabsTrigger value="problems" className="text-xs h-8 data-[state=active]:border-b-2 data-[state=active]:border-blue-600 data-[state=active]:shadow-none rounded-none px-1">Problems Console</TabsTrigger>
                    </TabsList>
                    <div className="flex-1 overflow-hidden">
                      <TabsContent value="validation" className="m-0 h-full border-none outline-none overflow-hidden">
                        <ValidationPanel />
                      </TabsContent>
                      <TabsContent value="problems" className="m-0 h-full border-none outline-none overflow-hidden bg-gray-50/50">
                        <ProblemsPanel />
                      </TabsContent>
                    </div>
                  </Tabs>
                </ResizablePanel>
              </ResizablePanelGroup>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default function App() {
  return (
    <TooltipProvider>
      <ToastProvider>
        <Toaster position="bottom-right" />
        <AppContent />
      </ToastProvider>
    </TooltipProvider>
  );
}
