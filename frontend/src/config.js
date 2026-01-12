// Configuración centralizada de la API
// Detecta automáticamente el entorno y usa la URL correcta

const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8000'
    : `${window.location.protocol}//${window.location.host}/api`;

export default API_BASE_URL;
