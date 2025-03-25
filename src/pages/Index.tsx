
import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

export default function Index() {
  const navigate = useNavigate();
  
  useEffect(() => {
    // Redirect to the landing page
    navigate("/");
  }, [navigate]);
  
  return null;
}
