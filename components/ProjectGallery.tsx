"use client";

import { useMemo, useState } from "react";
import type { Project } from "@/lib/types";
import { seededShuffle } from "@/lib/shuffle";
import Lightbox from "./Lightbox";

interface Props {
  projects: Project[];
  highlightYear: number;
}

function isActiveInYear(p: Project, year: number): boolean {
  return p.OriginalYear <= year && year <= p.EndYear;
}

function GalleryCard({
  project,
  starred,
  onOpen,
}: {
  project: Project;
  starred: boolean;
  onOpen: (project: Project) => void;
}) {
  const [failed, setFailed] = useState(false);
  const caption =
    project.DurationDisplay || (project.ProjectSpan !== String(project.Year) ? project.ProjectSpan : String(project.Year));

  return (
    <div className="overflow-hidden rounded-lg border border-border bg-panel">
      {failed ? (
        <div className="image-placeholder flex h-40 items-center justify-center">🖼️ Not Available</div>
      ) : (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          src={project.ImageLink}
          alt={project.Project_Name}
          className="h-40 w-full cursor-zoom-in object-cover transition hover:opacity-90"
          onError={() => setFailed(true)}
          onClick={() => onOpen(project)}
        />
      )}
      <div className="p-2">
        <p className="text-sm font-medium text-white">
          {starred ? "⭐ " : ""}
          {project.Project_Name}
          <span className="ml-1 text-xs font-normal text-muted">[{caption}]</span>
        </p>
        {project.BlogLink && (
          <a
            href={project.BlogLink}
            target="_blank"
            rel="noreferrer"
            className="text-xs text-accent hover:underline"
          >
            📖 More Information
          </a>
        )}
      </div>
    </div>
  );
}

export default function ProjectGallery({ projects, highlightYear }: Props) {
  const [showMore, setShowMore] = useState(false);
  const [lightboxProject, setLightboxProject] = useState<Project | null>(null);
  const perPage = 8;

  const { timelineProjects, otherProjects } = useMemo(() => {
    const validImages = projects.filter((p) => p.ImageLink && p.ImageLink.startsWith("http"));
    const seen = new Set<string>();
    const uniqueImages: Project[] = [];
    for (const p of validImages) {
      if (!seen.has(p.Project_Name)) {
        seen.add(p.Project_Name);
        uniqueImages.push(p);
      }
    }
    const timeline = uniqueImages.filter((p) => isActiveInYear(p, highlightYear));
    const others = uniqueImages.filter((p) => !isActiveInYear(p, highlightYear));
    return { timelineProjects: timeline, otherProjects: seededShuffle(others, "gallery-42") };
  }, [projects, highlightYear]);

  if (timelineProjects.length === 0 && otherProjects.length === 0) {
    return (
      <div>
        <h3 className="section-header">Project Gallery</h3>
        <p className="text-sm text-muted">No valid image links available for selected filters.</p>
      </div>
    );
  }

  const visibleOthers = otherProjects.slice(0, showMore ? perPage * 2 : perPage);

  return (
    <div>
      <h3 className="section-header">Project Gallery</h3>

      {timelineProjects.length > 0 && (
        <div className="mb-6">
          <h4 className="mb-3 text-base font-semibold text-white">🎯 Projects Active in {highlightYear}</h4>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
            {timelineProjects.slice(0, 8).map((p) => (
              <GalleryCard key={p.Project_Name} project={p} starred onOpen={setLightboxProject} />
            ))}
          </div>
        </div>
      )}

      {otherProjects.length > 0 && (
        <div>
          <h4 className="mb-3 text-base font-semibold text-white">📸 Other Projects</h4>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
            {visibleOthers.map((p) => (
              <GalleryCard key={p.Project_Name} project={p} starred={false} onOpen={setLightboxProject} />
            ))}
          </div>
          {otherProjects.length > perPage && !showMore && (
            <button
              onClick={() => setShowMore(true)}
              className="mt-4 rounded-lg border border-[#1557b0] bg-[#2d3436] px-4 py-2 text-sm font-medium text-white transition hover:bg-[#1557b0]"
            >
              🔍 Load More Projects
            </button>
          )}
        </div>
      )}

      {lightboxProject && (
        <Lightbox
          imageUrl={lightboxProject.ImageLink}
          caption={`${lightboxProject.Project_Name} — ${
            lightboxProject.DurationDisplay || lightboxProject.ProjectSpan
          }`}
          onClose={() => setLightboxProject(null)}
        />
      )}
    </div>
  );
}
