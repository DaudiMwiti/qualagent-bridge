
import { useState, useEffect } from "react";
import { Bell } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export type Notification = {
  id: string;
  title: string;
  message: string;
  timestamp: Date;
  read: boolean;
  type: "info" | "success" | "warning" | "error";
  link?: string;
};

// Mock notifications service that would be replaced with actual API calls
const useNotifications = () => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  
  // Load notifications (mock implementation)
  useEffect(() => {
    // This would be replaced with an API call in a real implementation
    const mockNotifications: Notification[] = [
      {
        id: "1",
        title: "Analysis Complete",
        message: "Your text analysis for 'Customer Feedback Q1' has completed.",
        timestamp: new Date(Date.now() - 1000 * 60 * 30), // 30 mins ago
        read: false,
        type: "success",
        link: "/dashboard/projects/1/analysis/1"
      },
      {
        id: "2",
        title: "Export Ready",
        message: "Your data export for 'Interview Transcripts' is ready for download.",
        timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2), // 2 hours ago
        read: false,
        type: "info",
        link: "/dashboard/exports"
      }
    ];
    
    setNotifications(mockNotifications);
    
    // In a real app, we would set up real-time notifications via WebSockets here
    // This could be connected to the SSE stream endpoint from your analysis API
  }, []);
  
  const markAsRead = (id: string) => {
    setNotifications(prev => 
      prev.map(notification => 
        notification.id === id 
          ? { ...notification, read: true } 
          : notification
      )
    );
  };
  
  const markAllAsRead = () => {
    setNotifications(prev => 
      prev.map(notification => ({ ...notification, read: true }))
    );
  };
  
  const removeNotification = (id: string) => {
    setNotifications(prev => prev.filter(notification => notification.id !== id));
  };
  
  return {
    notifications,
    markAsRead,
    markAllAsRead,
    removeNotification,
    unreadCount: notifications.filter(n => !n.read).length
  };
};

export function NotificationsPopover() {
  const { notifications, markAsRead, markAllAsRead, removeNotification, unreadCount } = useNotifications();
  const [open, setOpen] = useState(false);
  
  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button variant="ghost" size="icon" className="relative">
          <Bell className="h-5 w-5" />
          {unreadCount > 0 && (
            <Badge 
              className="absolute -top-1 -right-1 px-1.5 py-0.5 min-w-[18px] min-h-[18px] flex items-center justify-center rounded-full"
              variant="destructive"
            >
              {unreadCount > 9 ? "9+" : unreadCount}
            </Badge>
          )}
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-80" align="end">
        <div className="flex justify-between items-center border-b pb-2 mb-2">
          <h3 className="font-medium">Notifications</h3>
          {unreadCount > 0 && (
            <Button 
              variant="ghost" 
              size="sm" 
              className="text-xs h-auto py-1"
              onClick={markAllAsRead}
            >
              Mark all as read
            </Button>
          )}
        </div>
        <div className="max-h-80 overflow-y-auto space-y-2">
          {notifications.length === 0 ? (
            <div className="text-center py-6 text-muted-foreground">
              No notifications
            </div>
          ) : (
            notifications.map(notification => (
              <div 
                key={notification.id} 
                className={cn(
                  "p-2 rounded-md border relative",
                  !notification.read && "bg-primary/5 border-primary/20",
                  notification.read && "bg-background border-muted"
                )}
              >
                <div className="flex justify-between items-start">
                  <h4 className="font-medium text-sm">{notification.title}</h4>
                  <Button 
                    variant="ghost" 
                    size="icon" 
                    className="h-5 w-5" 
                    onClick={() => removeNotification(notification.id)}
                  >
                    <span className="sr-only">Remove</span>
                    <span aria-hidden>×</span>
                  </Button>
                </div>
                <p className="text-sm text-muted-foreground">{notification.message}</p>
                <div className="flex justify-between items-center mt-2">
                  <span className="text-xs text-muted-foreground">
                    {notification.timestamp.toLocaleTimeString(undefined, {
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </span>
                  <div className="flex gap-2">
                    {!notification.read && (
                      <Button 
                        variant="ghost" 
                        size="sm" 
                        className="text-xs h-auto py-1"
                        onClick={() => markAsRead(notification.id)}
                      >
                        Mark read
                      </Button>
                    )}
                    {notification.link && (
                      <Button 
                        variant="default" 
                        size="sm" 
                        className="text-xs h-auto py-1"
                        onClick={() => {
                          markAsRead(notification.id);
                          setOpen(false);
                          window.location.href = notification.link!;
                        }}
                      >
                        View
                      </Button>
                    )}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </PopoverContent>
    </Popover>
  );
}
