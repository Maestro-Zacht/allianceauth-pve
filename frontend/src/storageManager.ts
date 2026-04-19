const STORAGE_VERSION = "1";
const VERSION_KEY = 'allianceauth_pve_version';

console.log("env", import.meta.env);

function clearOldStorage() {
    for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key && key.startsWith('new-entry-form')) {
            localStorage.removeItem(key);
        }
    }
}

export function runStorageMigrations() {
    const storedVersion = localStorage.getItem(VERSION_KEY);
    if (storedVersion !== STORAGE_VERSION) {
        clearOldStorage();
        localStorage.setItem(VERSION_KEY, STORAGE_VERSION);
    }
}