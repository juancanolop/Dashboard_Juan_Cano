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
        <div className="flex flex-wrap gap-2">
          {skills.map((skill) => (
            <span
              key={skill}
              className="skill-badge min-w-[90px] rounded-full px-3.5 py-2.5 text-center text-sm font-bold text-white shadow-lg"
              style={{
                backgroundColor: skillColor(skill),
                border: "2px solid rgba(255,255,255,0.1)",
                textShadow: "1px 1px 2px rgba(0,0,0,0.3)",
              }}
            >
              {skill}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
