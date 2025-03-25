
import { ReactNode } from "react";
import { BreadcrumbNav } from "./breadcrumb-nav";

type PageHeaderProps = {
  title: string;
  description?: string;
  breadcrumbs?: Array<{ label: string; href: string }>;
  actions?: ReactNode;
};

export function PageHeader({ title, description, breadcrumbs = [], actions }: PageHeaderProps) {
  return (
    <div className="pb-4 border-b mb-6">
      {breadcrumbs.length > 0 && <BreadcrumbNav items={breadcrumbs} />}
      
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold">{title}</h1>
          {description && <p className="text-muted-foreground mt-1">{description}</p>}
        </div>
        
        {actions && <div className="flex items-center space-x-2">{actions}</div>}
      </div>
    </div>
  );
}
