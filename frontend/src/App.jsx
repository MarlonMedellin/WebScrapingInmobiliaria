import { useState, useEffect } from 'react'
import './App.css'
import PropertiesTable from './components/PropertiesTable'

const PORTALS = [
  "fincaraiz", "elcastillo", "santafe", "panda",
  "integridad", "protebienes", "lacastellana", "monserrate", "aportal"
];

function App() {
  const [properties, setProperties] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({ total: 0, bySource: {} });

  const fetchProperties = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/properties?limit=200');
      const data = await response.json();

      setProperties(data);

      const total = data.length;
      const bySource = data.reduce((acc, curr) => {
        acc[curr.source] = (acc[curr.source] || 0) + 1;
        return acc;
      }, {});

      setStats({ total, bySource });
    } catch (error) {
      console.error("Error fetching properties:", error);
    } finally {
      setLoading(false);
    }
  };

  const triggerScrape = async (portal) => {
    try {
      await fetch(`http://localhost:8000/scrape/${portal}`, { method: 'POST' });
      alert(`Scraping iniciado para ${portal}. Actualiza en unos segundos.`);
    } catch (e) {
      alert("Error iniciando scraping");
    }
  };

  useEffect(() => {
    fetchProperties();
  }, []);

  return (
    <div className="dashboard-container">
      <header>
        <h1>Medellín Real Estate Monitor</h1>
        <p className="subtitle">Monitoreo de mercado en tiempo real - {PORTALS.length} portales integrados</p>
      </header>

      <section className="controls-section">
        <div className="stats-grid">
          <div className="stat-card summary">
            <div className="stat-value">{stats.total}</div>
            <div className="stat-label">Total Propiedades</div>
          </div>
          {PORTALS.map(source => (
            <div className="stat-card" key={source}>
              <div className="stat-value">{stats.bySource[source] || 0}</div>
              <div className="stat-label">{source}</div>
              <button className="mini-scrape-btn" onClick={() => triggerScrape(source)}>▶</button>
            </div>
          ))}
        </div>
      </section>

      <main>
        <div className="main-header">
          <h2>Últimos Ingresos</h2>
          <div className="actions">
            <button className="action-btn secondary" onClick={fetchProperties}>
              ↻ Actualizar Datos
            </button>
          </div>
        </div>

        {loading ? (
          <div className="loading-state">Cargando datos...</div>
        ) : (
          <PropertiesTable properties={properties} />
        )}
      </main>
    </div>
  )
}

export default App

