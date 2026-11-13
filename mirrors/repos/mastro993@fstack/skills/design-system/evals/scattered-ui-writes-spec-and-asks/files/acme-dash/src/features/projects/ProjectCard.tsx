import { Avatar } from "./Avatar";

export type Project = { id: string; name: string; owner: string; openTasks: number };

export function ProjectCard({ project, onArchive }: { project: Project; onArchive: () => void }) {
  return (
    <div className="rounded-xl border border-[#E3E5EA] bg-white p-[18px] shadow-sm">
      <div className="flex items-center gap-3">
        <Avatar name={project.owner} />
        <h3 className="text-[15px] font-semibold">{project.name}</h3>
      </div>
      <p className="mt-2 text-sm text-gray-500">{project.openTasks} open tasks</p>
      <button className="mt-4 text-sm text-[#C8372D]" onClick={onArchive}>Archive</button>
    </div>
  );
}
