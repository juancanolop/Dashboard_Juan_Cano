"use client";

import { useState } from "react";

const CLOUDINARY_BASE = "https://res.cloudinary.com/dmf2pbdlq/image/upload/";

function candidateUrls(software: string): string[] {
  return [
    `${CLOUDINARY_BASE}logos/${software}.png`,
    `${CLOUDINARY_BASE}logos/${software}.jpg`,
    `${CLOUDINARY_BASE}${software}.png`,
    `${CLOUDINARY_BASE}${software}.jpg`,
  ];
}

function SoftwareLogo({ software }: { software: string }) {
  const urls = candidateUrls(software);
  const [attempt, setAttempt] = useState(0);
  const [failed, setFailed] = useState(false);

  if (failed) {
    return <div className="text-center text-[0.7rem] text-muted">{software}</div>;
  }

  return (
    // eslint-disable-next-line @next/next/no-img-element
    <img
      src={urls[attempt]}
      alt={software}
      width={80}
      height={80}
      className="mx-auto h-20 w-20 object-contain"
      onError={() => {
        if (attempt < urls.length - 1) {
          setAttempt(attempt + 1);
        } else {
          setFailed(true);
        }
      }}
    />
  );
}

export default function SoftwareLogos({ software }: { software: string[] }) {
  return (
    <div>
      <h3 className="section-header">Software</h3>
      {software.length === 0 ? (
        <p className="text-sm text-muted">No software available for selected filters.</p>
      ) : (
        <div className="flex flex-wrap gap-4">
          {software.map((item) => (
            <SoftwareLogo key={item} software={item} />
          ))}
        </div>
      )}
    </div>
  );
}
