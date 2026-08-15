"use client";

import Image from "next/image";
import YearFilter from "./YearFilter";
import FilterCheckboxGroup from "./FilterCheckboxGroup";

interface Props {
  years: number[];
  selectedYearsSidebar: string[];
  onYearsChange: (next: string[]) => void;
  industries: string[];
  selectedIndustries: string[];
  onIndustriesChange: (next: string[]) => void;
  categories: string[];
  selectedCategories: string[];
  onCategoriesChange: (next: string[]) => void;
  roles: string[];
  selectedRoles: string[];
  onRolesChange: (next: string[]) => void;
}

const NAV_LINKS = [
  { label: "LinkedIn", href: "https://www.linkedin.com/in/juan-david-cano/" },
  { label: "Blog", href: "https://news.kronosgmt.com/" },
  { label: "Contact Me", href: "https://calendly.com/juancano-kronosgmt/introduction-meeting" },
];

export default function Sidebar(props: Props) {
  return (
    <aside className="w-full shrink-0 border-border bg-panel p-4 lg:w-72 lg:border-r">
      <div className="mb-4 text-center">
        <a href="https://www.juandavidcano.com/" target="_blank" rel="noreferrer">
          <Image
            src="https://res.cloudinary.com/dmf2pbdlq/image/upload/v1756601724/Profile_zwgeyn.png"
            alt="Juan David Cano"
            width={280}
            height={280}
            className="mx-auto rounded-3xl transition-transform hover:scale-[1.03]"
          />
        </a>
      </div>

      <nav className="mb-4 space-y-1.5">
        {NAV_LINKS.map((link) => (
          <a
            key={link.label}
            href={link.href}
            target="_blank"
            rel="noreferrer"
            className="block rounded-lg border border-[#1557b0] bg-[#2d3436] px-4 py-2.5 text-sm font-medium text-white transition hover:-translate-y-px hover:bg-[#1557b0]"
          >
            {link.label}
          </a>
        ))}
      </nav>

      <hr className="mb-4 border-border" />

      <p className="mb-3 text-sm font-bold text-white">🎯 Filters</p>
      <YearFilter years={props.years} selected={props.selectedYearsSidebar} onChange={props.onYearsChange} />
      <FilterCheckboxGroup
        label="🏢 Industries"
        options={props.industries}
        selected={props.selectedIndustries}
        onChange={props.onIndustriesChange}
      />
      <FilterCheckboxGroup
        label="📂 Categories"
        options={props.categories}
        selected={props.selectedCategories}
        onChange={props.onCategoriesChange}
      />
      <FilterCheckboxGroup
        label="👤 Role"
        options={props.roles}
        selected={props.selectedRoles}
        onChange={props.onRolesChange}
      />
    </aside>
  );
}
