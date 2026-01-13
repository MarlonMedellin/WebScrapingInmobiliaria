import { useState, useEffect } from 'react'
import './App.css'
import PropertiesTable from './components/PropertiesTable'
import FiltersBar from './components/FiltersBar'
import PropertyModal from './components/PropertyModal'
import { API_BASE_URL, API_KEY } from './config'

const PORTALS = [
  "fincaraiz", "elcastillo", "santafe", "panda",
  "integridad", "protebienes", "lacastellana", "monserrate", "aportal",
  "escalainmobiliaria", "suvivienda", "portofino", "nutibara", "laaldea", "ayura", "albertoalvarez"
];

function App() {
  const [properties, setProperties] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({ total: 0, bySource: {} });
  const [selectedProperty, setSelectedProperty] = useState(null);
  const [scrapingPortals, setScrapingPortals] = useState({});

  // Keep track of current filters for refresh actions
  const [currentFilters, setCurrentFilters] = useState({});

  const fetchProperties = async (filters = {}) => {
    setLoading(true);
    try {
      // Construct Query Params
      const params = new URLSearchParams({ limit: 200 }); // Default limit

      if (filters.source) params.append('source', filters.source);
      if (filters.search) params.append('search', filters.search);
      if (filters.min_price) params.append('min_price', filters.min_price);
      if (filters.max_price) params.append('max_price', filters.max_price);
      if (filters.min_area) params.append('min_area', filters.min_area);
      if (filters.max_area) params.append('max_area', filters.max_area);
      if (filters.neighborhood) params.append('neighborhood', filters.neighborhood);
      if (filters.show_archived) params.append('show_archived', 'true');

      const response = await fetch(`${API_BASE_URL}/properties?${params.toString()}`);
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

  const handleFilterChange = (newFilters) => {
    setCurrentFilters(newFilters);
    fetchProperties(newFilters);
  };

  const handleStatusChange = async (id, newStatus) => {
    try {
      // Optimistic UI update
      setProperties(prev => prev.filter(p => p.id !== id));

      await fetch(`${API_BASE_URL}/properties/${id}/status`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': API_KEY
        },
        body: JSON.stringify({ status: newStatus })
      });
    } catch (e) {
      console.error("Status update failed", e);
      fetchProperties(currentFilters); // Revert on error
    }
  };

  const handleSelectProperty = (property) => {
    setSelectedProperty(property);
  };

  const handleCloseModal = () => {
    setSelectedProperty(null);
  };

  const triggerScrape = async (portal) => {
    setScrapingPortals(prev => ({ ...prev, [portal]: true }));
    try {
      await fetch(`${API_BASE_URL}/scrape/${portal}`, {
        method: 'POST',
        headers: { 'X-API-Key': API_KEY }
      });
      // We don't alert anymore, the button state changes
      setTimeout(() => {
        setScrapingPortals(prev => ({ ...prev, [portal]: false }));
        fetchProperties(currentFilters);
      }, 3000); // Give it some head start
    } catch (e) {
      console.error("Error iniciando scraping", e);
      setScrapingPortals(prev => ({ ...prev, [portal]: false }));
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
            <div className="stat-label">Propiedades Listadas</div>
          </div>
          {PORTALS.map(source => (
            <div className={`stat-card ${scrapingPortals[source] ? 'scraping' : ''}`} key={source}>
              <div className="stat-value">{stats.bySource[source] || 0}</div>
              <div className="stat-label">{source}</div>
              <button
                className={`mini-scrape-btn ${scrapingPortals[source] ? 'loading' : ''}`}
                onClick={() => triggerScrape(source)}
                disabled={scrapingPortals[source]}
              >
                {scrapingPortals[source] ? '⏳' : '▶'}
              </button>
            </div>
          ))}
        </div>
      </section>

      <FiltersBar onFilterChange={handleFilterChange} portals={PORTALS} />

      <main>
        <div className="main-header">
          <h2>Resultados de Búsqueda</h2>
          <div className="actions">
            <button className="action-btn secondary" onClick={() => fetchProperties(currentFilters)}>
              ↻ Actualizar Datos
            </button>
          </div>
        </div>

        {loading ? (
          <div className="loading-state">Cargando datos...</div>
        ) : (
          <PropertiesTable
            properties={properties}
            onStatusChange={handleStatusChange}
            onSelectProperty={handleSelectProperty}
          />
        )}
      </main>

      {selectedProperty && (
        <PropertyModal
          property={selectedProperty}
          onClose={handleCloseModal}
        />
      )}
    </div>
  )
}

export default App

