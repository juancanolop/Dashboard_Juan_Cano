import Dashboard from "@/components/Dashboard";
import { getProjects } from "@/lib/data";

export const revalidate = 300;

export default async function Page() {
  const { projects } = await getProjects();
  return <Dashboard projects={projects} />;
}
