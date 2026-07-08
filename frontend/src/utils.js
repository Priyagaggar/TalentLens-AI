import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Merges class names with Tailwind CSS conflict resolution.
 * @param {...(string|undefined|null|false)} inputs
 * @returns {string}
 */
export function cn(...inputs) {
    return twMerge(clsx(inputs));
}

/**
 * Formats a file size in bytes to human-readable string.
 * @param {number} bytes
 * @returns {string}
 */
export function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Robustly resolves the API base URL, supporting local and Render hosting environments.
 * @returns {string}
 */
export function getApiBaseUrl() {
    let url = import.meta.env.VITE_API_URL;
    if (!url) return "/api/v1";
    if (!url.startsWith("http") && !url.startsWith("/")) url = `https://${url}`;
    try {
        const urlObj = new URL(url);
        if (urlObj.hostname !== "localhost" && !urlObj.hostname.includes(".")) {
            url = url.replace(urlObj.hostname, `${urlObj.hostname}.onrender.com`);
        }
    } catch (e) {}
    if (url.endsWith("/")) url = url.slice(0, -1);
    if (!url.endsWith("/api/v1")) url = `${url}/api/v1`;
    return url;
}
