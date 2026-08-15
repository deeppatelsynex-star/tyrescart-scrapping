/**
 * IndexedDB Storage Helper for Scraper Working States
 * Decouples ephemeral 'working' runner status from MySQL and stores it in client IndexedDB.
 */
(function () {
  const DB_NAME = 'ScraperDB';
  const DB_VERSION = 1;
  const STORE_NAME = 'working_scrapers';

  let dbPromise = null;

  function openDB() {
    if (dbPromise) return dbPromise;
    dbPromise = new Promise((resolve) => {
      if (!window.indexedDB) {
        console.warn('IndexedDB is not supported in this browser environment.');
        resolve(null);
        return;
      }
      const request = indexedDB.open(DB_NAME, DB_VERSION);
      request.onupgradeneeded = (event) => {
        const db = event.target.result;
        if (!db.objectStoreNames.contains(STORE_NAME)) {
          db.createObjectStore(STORE_NAME, { keyPath: 'fileId' });
        }
      };
      request.onsuccess = () => resolve(request.result);
      request.onerror = (err) => {
        console.error('IndexedDB open error:', err);
        resolve(null);
      };
    });
    return dbPromise;
  }

  const IDBStorage = {
    /**
     * Store or update the working status of a scraper in IndexedDB.
     */
    async setWorkingState(fileId, working, metadata = {}) {
      const db = await openDB();
      if (!db) return false;
      return new Promise((resolve) => {
        try {
          const tx = db.transaction(STORE_NAME, 'readwrite');
          const store = tx.objectStore(STORE_NAME);
          const numericId = Number(fileId);
          store.put({
            fileId: numericId,
            working: Boolean(working),
            updatedAt: Date.now(),
            ...metadata,
          });
          tx.oncomplete = () => resolve(true);
          tx.onerror = () => resolve(false);
        } catch (e) {
          resolve(false);
        }
      });
    },

    /**
     * Get the working state of a specific scraper from IndexedDB.
     */
    async getWorkingState(fileId) {
      const db = await openDB();
      if (!db) return null;
      return new Promise((resolve) => {
        try {
          const tx = db.transaction(STORE_NAME, 'readonly');
          const store = tx.objectStore(STORE_NAME);
          const req = store.get(Number(fileId));
          req.onsuccess = () => resolve(req.result || null);
          req.onerror = () => resolve(null);
        } catch (e) {
          resolve(null);
        }
      });
    },

    /**
     * Get all scrapers and their working states from IndexedDB as a Map<fileId, object>.
     */
    async getAllWorkingStates() {
      const db = await openDB();
      if (!db) return new Map();
      return new Promise((resolve) => {
        try {
          const tx = db.transaction(STORE_NAME, 'readonly');
          const store = tx.objectStore(STORE_NAME);
          const req = store.getAll();
          req.onsuccess = () => {
            const list = req.result || [];
            const map = new Map();
            list.forEach((item) => {
              map.set(Number(item.fileId), item);
            });
            resolve(map);
          };
          req.onerror = () => resolve(new Map());
        } catch (e) {
          resolve(new Map());
        }
      });
    },

    /**
     * Remove the stored working state for a scraper from IndexedDB.
     */
    async clearWorkingState(fileId) {
      const db = await openDB();
      if (!db) return false;
      return new Promise((resolve) => {
        try {
          const tx = db.transaction(STORE_NAME, 'readwrite');
          const store = tx.objectStore(STORE_NAME);
          store.delete(Number(fileId));
          tx.oncomplete = () => resolve(true);
          tx.onerror = () => resolve(false);
        } catch (e) {
          resolve(false);
        }
      });
    },

    /**
     * Clear all working states from IndexedDB.
     */
    async clearAll() {
      const db = await openDB();
      if (!db) return false;
      return new Promise((resolve) => {
        try {
          const tx = db.transaction(STORE_NAME, 'readwrite');
          const store = tx.objectStore(STORE_NAME);
          store.clear();
          tx.oncomplete = () => resolve(true);
          tx.onerror = () => resolve(false);
        } catch (e) {
          resolve(false);
        }
      });
    },
  };

  window.IDBStorage = IDBStorage;
})();
