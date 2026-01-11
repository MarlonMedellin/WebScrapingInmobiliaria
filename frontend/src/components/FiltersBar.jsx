import React, { useState, useEffect } from 'react';
import './FiltersBar.css';

const FiltersBar = ({ onFilterChange, portals }) => {
    const [filters, setFilters] = useState({
        search: '',
        source: '',
        min_price: '',
        max_price: '',
        min_area: '',
        max_area: '',
        show_archived: false
    });

    const [savedSearches, setSavedSearches] = useState([]);
    const [searchName, setSearchName] = useState('');
    const [isSaving, setIsSaving] = useState(false);

    useEffect(() => {
        loadSavedSearches();
    }, []);

    const loadSavedSearches = async () => {
        try {
            const res = await fetch('http://localhost:8000/searches');
            if (res.ok) setSavedSearches(await res.json());
        } catch (e) {
            console.error("Error loading searches", e);
        }
    };

    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFilters(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }));
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        onFilterChange(filters);
    };

    const handleReset = () => {
        const resetState = {
            search: '',
            source: '',
            min_price: '',
            max_price: '',
            min_area: '',
            max_area: '',
            show_archived: false
        };
        setFilters(resetState);
        onFilterChange(resetState);
    };

    const handleSaveSearch = async () => {
        if (!searchName) return alert("Ponle un nombre a tu búsqueda");
        try {
            const res = await fetch('http://localhost:8000/searches', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: searchName, criteria: filters })
            });
            if (res.ok) {
                alert("Búsqueda guardada");
                setIsSaving(false);
                setSearchName('');
                loadSavedSearches();
            }
        } catch (e) {
            alert("Error al guardar");
        }
    };

    const loadSearch = (searchItem) => {
        setFilters(searchItem.criteria);
        // Automatically trigger filter
        onFilterChange(searchItem.criteria);
    };

    const deleteSearch = async (id, e) => {
        e.stopPropagation();
        if (!confirm("¿Borrar búsqueda?")) return;
        await fetch(`http://localhost:8000/searches/${id}`, { method: 'DELETE' });
        loadSavedSearches();
    }

    return (
        <div className="filters-container">
            <div className="saved-searches-row">
                {savedSearches.length > 0 && (
                    <div className="saved-chips">
                        <span className="chips-label">Mis Búsquedas:</span>
                        {savedSearches.map(s => (
                            <button key={s.id} onClick={() => loadSearch(s)} className="search-chip">
                                {s.name}
                                <span className="delete-chip" onClick={(e) => deleteSearch(s.id, e)}>×</span>
                            </button>
                        ))}
                    </div>
                )}
            </div>

            <form className="filters-bar" onSubmit={handleSubmit}>
                <div className="filter-group search-group">
                    <input
                        type="text"
                        name="search"
                        placeholder="🔍 Buscar por ubicación, título..."
                        value={filters.search}
                        onChange={handleChange}
                        className="filter-input search-input"
                    />
                </div>

                <div className="filter-group">
                    <select name="source" value={filters.source} onChange={handleChange} className="filter-select">
                        <option value="">Todos los Portales</option>
                        {portals.map(p => (
                            <option key={p} value={p}>{p}</option>
                        ))}
                    </select>
                </div>

                <div className="filter-group range-group">
                    <input
                        type="number"
                        name="min_price"
                        placeholder="Precio Min"
                        value={filters.min_price}
                        onChange={handleChange}
                        className="filter-input"
                    />
                    <span className="separator">-</span>
                    <input
                        type="number"
                        name="max_price"
                        placeholder="Precio Max"
                        value={filters.max_price}
                        onChange={handleChange}
                        className="filter-input"
                    />
                </div>

                <div className="filter-group range-group">
                    <input
                        type="number"
                        name="min_area"
                        placeholder="Área Min (m²)"
                        value={filters.min_area}
                        onChange={handleChange}
                        className="filter-input"
                    />
                    <span className="separator">-</span>
                    <input
                        type="number"
                        name="max_area"
                        placeholder="Max"
                        value={filters.max_area}
                        onChange={handleChange}
                        className="filter-input"
                    />
                </div>

                <div className="filter-group">
                    <label className="checkbox-label">
                        <input
                            type="checkbox"
                            name="show_archived"
                            checked={filters.show_archived}
                            onChange={handleChange}
                        />
                        Ver Archivados
                    </label>
                </div>

                <div className="filter-actions">
                    <button type="submit" className="action-btn primary small">Filtrar</button>
                    <button type="button" onClick={handleReset} className="action-btn secondary small">Limpiar</button>

                    {isSaving ? (
                        <div className="save-popover">
                            <input
                                autoFocus
                                placeholder="Nombre de búsqueda..."
                                value={searchName}
                                onChange={(e) => setSearchName(e.target.value)}
                                className="filter-input small-input"
                            />
                            <button type="button" onClick={handleSaveSearch} className="action-btn primary small">💾 OK</button>
                            <button type="button" onClick={() => setIsSaving(false)} className="action-btn text small">✖</button>
                        </div>
                    ) : (
                        <button type="button" onClick={() => setIsSaving(true)} className="action-btn ghost small">💾 Guardar</button>
                    )}

                </div>
            </form>
        </div>
    );
};

export default FiltersBar;
