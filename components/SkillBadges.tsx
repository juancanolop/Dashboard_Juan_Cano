import { skillColor } from "@/lib/skillColor";

interface Props {
  skills: string[];
}

export default function SkillBadges({ skills }: Props) {
  return (
    <div>
      <h3 className="section-header">Skills</h3>
      {skills.length === 0 ? (
        <p className="text-sm text-muted">No skills available for selected filters.</p>
      ) : (
        <div className="flex flex-wrap gap-1.5">
          {skills.map((skill) => {
            const style = skillColor(skill);
            return (
              <span
                key={skill}
                className="rounded-md px-2 py-0.5 text-xs font-medium leading-relaxed"
                style={{
                  backgroundColor: style.background,
                  border: `1px solid ${style.border}`,
                  color: style.color,
                }}
              >
                {skill}
              </span>
            );
          })}
        </div>
      )}
    </div>
  );
}
