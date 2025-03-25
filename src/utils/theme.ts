
// Simple utility to handle dark mode theme toggle

// Function to initialize theme based on user preference or localStorage
export function initializeTheme() {
  // Check if theme is stored in localStorage
  const storedTheme = localStorage.getItem("theme");
  
  // Check user preference if no stored theme
  if (!storedTheme) {
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    setTheme(prefersDark ? "dark" : "light");
    return;
  }
  
  // Apply stored theme
  setTheme(storedTheme);
}

// Function to set the theme
export function setTheme(theme: "dark" | "light") {
  if (theme === "dark") {
    document.documentElement.classList.add("dark");
  } else {
    document.documentElement.classList.remove("dark");
  }
  
  // Store the user preference
  localStorage.setItem("theme", theme);
}

// Function to toggle the theme
export function toggleTheme() {
  const isDark = document.documentElement.classList.contains("dark");
  setTheme(isDark ? "light" : "dark");
  return !isDark;
}
