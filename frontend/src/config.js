// Configuración centralizada de la API
// Detecta automáticamente el entorno y usa la URL correcta

const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8000'
    : `${window.location.protocol}//${window.location.host}/api`;

const API_KEY = import.meta.env.VITE_API_KEY || 'dev-secret-key';

export { API_BASE_URL, API_KEY };
export default API_BASE_URL;
