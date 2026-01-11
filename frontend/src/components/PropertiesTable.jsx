import React from 'react';

const PropertiesTable = ({ properties }) => {
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
                        <th>Acción</th>
                    </tr>
                </thead>
                <tbody>
                    {properties.map((prop) => (
                        <tr key={prop.id}>
                            <td>{getSourceBadge(prop.source)}</td>
                            <td>{prop.title}</td>
                            <td>{prop.location}</td>
                            <td>{prop.area ? `${prop.area} m²` : '--'}</td>
                            <td>{prop.bedrooms || '--'}</td>
                            <td className="price-tag">{formatPrice(prop.price)}</td>
                            <td>
                                <a
                                    href={prop.link}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="property-link"
                                >
                                    Ver Original →
                                </a>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default PropertiesTable;

