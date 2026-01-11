import React from 'react';
import './PropertyModal.css';

const PropertyModal = ({ property, onClose }) => {
    if (!property) return null;

    const formatPrice = (price) => {
        if (!price || price === "0") return "N/A";
        return new Intl.NumberFormat('es-CO', {
            style: 'currency',
            currency: 'COP',
            maximumFractionDigits: 0
        }).format(price);
    };

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content" onClick={e => e.stopPropagation()}>
                <button className="modal-close-btn" onClick={onClose}>×</button>

                <div className="modal-header">
                    <span className={`badge badge-${property.source}`}>{property.source}</span>
                    <h2>{property.title}</h2>
                    <p className="modal-location">📍 {property.location}</p>
                </div>

                <div className="modal-body">
                    <div className="modal-stats-grid">
                        <div className="modal-stat">
                            <span className="label">Precio</span>
                            <span className="value price">{formatPrice(property.price)}</span>
                        </div>
                        <div className="modal-stat">
                            <span className="label">Área</span>
                            <span className="value">{property.area ? `${property.area} m²` : '--'}</span>
                        </div>
                        <div className="modal-stat">
                            <span className="label">Habitaciones</span>
                            <span className="value">{property.bedrooms || '--'}</span>
                        </div>
                        <div className="modal-stat">
                            <span className="label">Baños</span>
                            <span className="value">{property.bathrooms || '--'}</span>
                        </div>
                    </div>

                    <div className="modal-description">
                        <h3>Descripción</h3>
                        <p>{property.description || "No hay descripción disponible para esta propiedad."}</p>
                    </div>

                    <div className="modal-actions">
                        <a
                            href={property.link}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="btn-primary"
                        >
                            Ver en Portal Original 🔗
                        </a>
                        <a
                            href={`https://wa.me/?text=${encodeURIComponent(`Hola, vi este inmueble y me interesa: ${property.title}. Link: ${property.link}`)}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="btn-whatsapp"
                        >
                            Consultar por WhatsApp 📱
                        </a>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default PropertyModal;
