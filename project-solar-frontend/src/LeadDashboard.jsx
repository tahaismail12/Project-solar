import React, { useEffect, useState } from "react";
import { Bar } from "react-chartjs-2";
import "chart.js/auto"; // required for Chart.js to auto register components

export default function LeadDashboard() {
  const [data, setData] = useState(null);
  const [view, setView] = useState("daily");

  useEffect(() => {
    fetch("https://project-solar-y8zx.onrender.com/leads")

      .then((res) => res.json())
      .then(setData)
      .catch(console.error);
  }, []);

  const getChartData = () => {
    if (!data) return { labels: [], datasets: [] };

    const viewMap = {
      daily: data.daily_leads,
      weekly: data.weekly_leads,
      monthly: data.monthly_leads,
    };

    const labels = Object.keys(viewMap[view] || {});
    const counts = Object.values(viewMap[view] || {});

    return {
      labels,
      datasets: [
        {
          label: `${view.charAt(0).toUpperCase() + view.slice(1)} Leads`,
          data: counts,
          backgroundColor: "#4B9CD3",
        },
      ],
    };
  };

  return (
    <div style={{ padding: "2rem", fontFamily: "Arial" }}>
      <h1 style={{ fontSize: "28px", fontWeight: "bold", marginBottom: "20px" }}>
        📊 Lead Analytics Dashboard
      </h1>

      {data ? (
        <>
          {/* Stat cards */}
          <div style={{ display: "flex", gap: "20px", marginBottom: "30px", flexWrap: "wrap" }}>
            <StatCard title="Total Leads" value={data.total_leads} />
            <StatCard title="Open Leads" value={data.open_leads} />
            <StatCard title="Qualified Leads" value={data.qualified_leads} />
            <StatCard title="Disqualified Leads" value={data.disqualified_leads} />
          </div>

          {/* Chart view toggle */}
          <div style={{ marginBottom: "10px" }}>
            <button onClick={() => setView("daily")}>Daily</button>{" "}
            <button onClick={() => setView("weekly")}>Weekly</button>{" "}
            <button onClick={() => setView("monthly")}>Monthly</button>
          </div>

          {/* Bar chart */}
          <div style={{ maxWidth: "1000px", marginBottom: "40px" }}>
            <Bar data={getChartData()} />
          </div>

          {/* Leads by Program */}
          <h2 style={{ fontSize: "20px", fontWeight: "bold", marginBottom: "10px" }}>
            📦 Leads by Program
          </h2>
          <ul>
            {Object.entries(data.program_classification).map(([prog, count]) => (
              <li key={prog}>{prog}: {count}</li>
            ))}
          </ul>

          {/* Leads by Brand */}
          <h2 style={{ fontSize: "20px", fontWeight: "bold", marginTop: "30px", marginBottom: "10px" }}>
            🎯 Leads by Brand
          </h2>
          <ul>
            {Object.entries(data.brand_classification).map(([brand, count]) => (
              <li key={brand}>{brand}: {count}</li>
            ))}
          </ul>

          {/* Leads by UTM Medium */}
          <h2 style={{ fontSize: "20px", fontWeight: "bold", marginTop: "30px", marginBottom: "10px" }}>
            📬 Leads by UTM Medium
          </h2>
          <ul>
            {Object.entries(data.utm_medium_classification).map(([utm, count]) => (
              <li key={utm}>{utm}: {count}</li>
            ))}
          </ul>
        </>
      ) : (
        <p>Loading data...</p>
      )}
    </div>
  );
}

function StatCard({ title, value }) {
  return (
    <div
      style={{
        padding: "20px",
        border: "1px solid #ddd",
        borderRadius: "8px",
        minWidth: "180px",
        backgroundColor: "#f9f9f9",
      }}
    >
      <p style={{ fontSize: "14px", color: "#555" }}>{title}</p>
      <h3 style={{ fontSize: "22px", fontWeight: "bold" }}>{value}</h3>
    </div>
  );
}
