
import { ChevronRight, Home } from "lucide-react";
import { Link, useLocation } from "react-router-dom";

type BreadcrumbItem = {
  label: string;
  href: string;
};

type BreadcrumbNavProps = {
  items: BreadcrumbItem[];
};

export function BreadcrumbNav({ items }: BreadcrumbNavProps) {
  const location = useLocation();
  
  return (
    <nav className="flex items-center space-x-1 text-sm text-muted-foreground mb-4">
      <Link 
        to="/" 
        className={`flex items-center hover:text-foreground transition-colors ${location.pathname === '/' ? 'text-foreground font-medium' : ''}`}
      >
        <Home className="h-4 w-4 mr-1" />
        <span>Home</span>
      </Link>
      
      {items.map((item, index) => (
        <div key={item.href} className="flex items-center">
          <ChevronRight className="h-4 w-4 mx-1" />
          <Link 
            to={item.href} 
            className={`hover:text-foreground transition-colors ${location.pathname === item.href ? 'text-foreground font-medium' : ''}`}
          >
            {item.label}
          </Link>
        </div>
      ))}
    </nav>
  );
}
