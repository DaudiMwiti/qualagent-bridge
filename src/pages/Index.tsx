
import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

export default function Index() {
  const navigate = useNavigate();
  
  useEffect(() => {
    // Redirect to the new dashboard
    navigate("/");
  }, [navigate]);
  
  return null;
}
