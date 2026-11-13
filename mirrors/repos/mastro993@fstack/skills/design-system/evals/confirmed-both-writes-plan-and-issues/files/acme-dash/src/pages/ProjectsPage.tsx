import { useState } from "react";
import { ProjectCard, type Project } from "../features/projects/ProjectCard";
import { ConfirmModal } from "../features/projects/ConfirmModal";
import { Button } from "../features/billing/Button";

const projects: Project[] = [
  { id: "p1", name: "Website relaunch", owner: "Dana Ortiz", openTasks: 12 },
  { id: "p2", name: "Q3 invoicing", owner: "Sam Lee", openTasks: 3 },
];

export function ProjectsPage() {
  const [archiving, setArchiving] = useState<Project | null>(null);
  return (
    <main className="mx-auto max-w-5xl p-8">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Projects</h1>
        <Button>New project</Button>
      </div>
      <div className="mt-6 grid grid-cols-2 gap-4">
        {projects.map((p) => (
          <ProjectCard key={p.id} project={p} onArchive={() => setArchiving(p)} />
        ))}
      </div>
      <ConfirmModal
        open={archiving !== null}
        title="Archive project?"
        message={`${archiving?.name} will move to the archive.`}
        onConfirm={() => setArchiving(null)}
        onCancel={() => setArchiving(null)}
      />
    </main>
  );
}
