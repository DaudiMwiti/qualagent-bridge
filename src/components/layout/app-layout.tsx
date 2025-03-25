
import { Outlet } from "react-router-dom";
import { SidebarNav } from "./sidebar-nav";

export function AppLayout() {
  return (
    <div className="flex min-h-screen">
      {/* Sidebar */}
      <div className="w-64 border-r px-4 py-6 hidden md:block">
        <div className="flex items-center gap-2 px-2 mb-6">
          <div className="rounded-md bg-primary p-1">
            <div className="h-6 w-6 text-primary-foreground flex items-center justify-center font-semibold">
              Q
            </div>
          </div>
          <h1 className="text-xl font-bold">QualAgents</h1>
        </div>
        <SidebarNav />
      </div>
      
      {/* Main content */}
      <div className="flex-1 overflow-auto">
        <div className="mx-auto max-w-6xl p-6">
          <Outlet />
        </div>
      </div>
    </div>
  );
}
