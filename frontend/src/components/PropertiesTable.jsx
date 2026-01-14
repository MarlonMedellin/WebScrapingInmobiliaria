import React from 'react';

const PropertiesTable = ({ properties, onStatusChange, onSelectProperty }) => {
    if (!properties || properties.length === 0) {
        return <div className="p-4 text-center text-gray-400">No hay propiedades recolectadas aún.</div>;
    }

    const formatPrice = (price) => {
        if (!price || price === "0") return "N/A";
        return new Intl.NumberFormat('es-CO', {
            style: 'currency',
            currency: 'COP',
            maximumFractionDigits: 0
        }).format(price);
    };

    const getSourceBadge = (source) => {
        const badges = {
            'fincaraiz': 'badge-fincaraiz',
            'elcastillo': 'badge-elcastillo',
            'santafe': 'badge-santafe',
            'panda': 'badge-panda',
            'integridad': 'badge-integridad',
            'protebienes': 'badge-protebienes',
            'lacastellana': 'badge-lacastellana',
            'monserrate': 'badge-monserrate',
            'aportal': 'badge-aportal'
        };
        const cls = badges[source] || 'badge-default';
        return <span className={`badge ${cls}`}>{source}</span>;
    };

    return (
        <div className="table-container">
            <table>
                <thead>
                    <tr>
                        <th>Portal</th>
                        <th>Título</th>
                        <th>Ubicación</th>
                        <th>Área</th>
                        <th>Alcobas</th>
                        <th>Precio</th>
                        <th>Días</th>
                        <th>Acción</th>
                    </tr>
                </thead>
                <tbody>
                    {properties.map((prop) => {
                        const isArchived = prop.status === 'ARCHIVED';

                        const getDaysBadge = (days) => {
                            const d = days || 0;
                            let cls = 'badge-days-old';
                            let text = `${d}d`;
                            if (d <= 3) {
                                cls = 'badge-days-new';
                                text = 'Nuevo';
                            } else if (d <= 7) {
                                cls = 'badge-days-recent';
                                text = `${d}d`;
                            }
                            return <span className={`badge-days ${cls}`}>{text}</span>;
                        };

                        return (
                            <tr key={prop.id} className={isArchived ? 'archived-row' : ''}>
                                <td>{getSourceBadge(prop.source)}</td>
                                <td>
                                    <span
                                        className="property-title-clickable"
                                        onClick={() => onSelectProperty(prop)}
                                    >
                                        {prop.title}
                                    </span>
                                </td>
                                <td>
                                    {prop.neighborhood_normalized ? (
                                        <span className="location-normalized" title={`Original: ${prop.location}`}>
                                            📍 {prop.neighborhood_normalized}
                                        </span>
                                    ) : (
                                        <span className="location-original">{prop.location}</span>
                                    )}
                                </td>
                                <td>{prop.area ? `${prop.area} m²` : '--'}</td>
                                <td>{prop.bedrooms || '--'}</td>
                                <td className="price-tag">{formatPrice(prop.price)}</td>
                                <td>{getDaysBadge(prop.days_active)}</td>
                                <td>
                                    <div className="action-row">
                                        <a
                                            href={prop.link}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="property-link"
                                            title="Ver Original"
                                        >
                                            🔗
                                        </a>
                                        <a
                                            href={`https://wa.me/?text=${encodeURIComponent(`Hola, vi este inmueble y me interesa: ${prop.title} en ${prop.location}. Precio: ${formatPrice(prop.price)}. Link: ${prop.link}`)}`}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="action-icon-btn whatsapp"
                                            title="Consultar por WhatsApp"
                                        >
                                            📱
                                        </a>
                                        {isArchived ? (
                                            <button
                                                className="action-icon-btn restore"
                                                onClick={() => onStatusChange(prop.id, 'NEW')}
                                                title="Restaurar"
                                            >
                                                ⟲
                                            </button>
                                        ) : (
                                            <button
                                                className="action-icon-btn archive"
                                                onClick={() => onStatusChange(prop.id, 'ARCHIVED')}
                                                title="Archivar"
                                            >
                                                ✖
                                            </button>
                                        )}
                                    </div>
                                </td>
                            </tr>
                        );
                    })}
                </tbody>
            </table>
        </div>
    );
};

export default PropertiesTable;

