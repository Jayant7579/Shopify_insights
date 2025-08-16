
import { useState } from "react";
import axios from "axios";

export default function App() {
  const [url, setUrl] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchInsights = async () => {
    setLoading(true);
    try {
      const res = await axios.get(
        `http://127.0.0.1:8000/fetch-insights/`,
        { params: { website_url: url } }
      );
      setResult(res.data);
    } catch (err) {
      alert(err.response?.data?.detail || "Error fetching insights");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: "800px", margin: "0 auto", padding: "2rem" }}>
      <h1>Shopify Insights Fetcher</h1>
      <input
        type="text"
        placeholder="Enter Shopify URL (e.g. https://memy.co.in)"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        style={{ width: "70%", padding: "8px" }}
      />
      <button onClick={fetchInsights} disabled={loading} style={{ marginLeft: "10px" }}>
        {loading ? "Loading..." : "Fetch"}
      </button>

      {result && (
        <pre style={{ textAlign: "left", background: "#f5f5f5", padding: "1rem", marginTop: "2rem" }}>
          {JSON.stringify(result, null, 2)}
        </pre>
      )}
    </div>
  );
}
