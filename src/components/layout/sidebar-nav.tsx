
import { Link, useLocation } from "react-router-dom";
import { cn } from "@/lib/utils";
import { BarChart, FileText, Home, Settings, UserCircle, HelpCircle, Download } from "lucide-react";

const navItems = [
  {
    title: "Dashboard",
    href: "/dashboard",
    icon: Home,
  },
  {
    title: "Projects",
    href: "/dashboard/projects",
    icon: FileText,
  },
  {
    title: "Agents",
    href: "/dashboard/agents",
    icon: UserCircle,
  },
  {
    title: "Visualizations",
    href: "/dashboard/visualizations",
    icon: BarChart,
  },
  {
    title: "Data Management",
    href: "/dashboard/data",
    icon: Download,
  },
  {
    title: "Help",
    href: "/dashboard/help",
    icon: HelpCircle,
  },
  {
    title: "Settings",
    href: "/dashboard/settings",
    icon: Settings,
  },
];

export function SidebarNav() {
  const location = useLocation();
  
  return (
    <nav className="space-y-1">
      {navItems.map((item) => {
        const isActive = location.pathname === item.href ||
          (item.href !== '/dashboard' && location.pathname.startsWith(item.href));
          
        return (
          <Link
            key={item.href}
            to={item.href}
            className={cn(
              "flex items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors",
              isActive 
                ? "bg-primary text-primary-foreground" 
                : "hover:bg-muted text-muted-foreground hover:text-foreground"
            )}
          >
            <item.icon className="h-4 w-4" />
            <span>{item.title}</span>
          </Link>
        );
      })}
    </nav>
  );
}
