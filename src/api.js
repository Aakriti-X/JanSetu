// api.js — Frontend API client for the SIH25231 RAG backend (http://localhost:8000)
// Auth: backend uses X-User-ID and X-User-PIN headers on all protected routes.

const BASE_URL = "http://localhost:8000";

// Internal helper
async function request(endpoint, options = {}) {
    try {
        const response = await fetch(`${BASE_URL}${endpoint}`, {
            headers: {
                "Content-Type": "application/json",
                ...(options.headers || {}),
            },
            ...options,
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || `Server error: ${response.status}`);
        }

        return data;
    } catch (error) {
        console.error("API Error:", error);
        throw error;
    }
}

// Register a new user. Returns { user_id, display_name, message }
export async function register(userId, displayName, pin) {
    return request("/auth/register", {
        method: "POST",
        body: JSON.stringify({ user_id: userId, display_name: displayName, pin: pin }),
    });
}

// Login and get user info. Returns { user_id, display_name, message }
export async function login(userId, pin) {
    return request("/auth/login", {
        method: "POST",
        body: JSON.stringify({ user_id: userId, pin: pin }),
    });
}

// Ask the RAG a question. Returns { answer, sources }
export async function queryRAG(userId, pin, question) {
    return request("/query", {
        method: "POST",
        headers: { "X-User-ID": userId, "X-User-PIN": pin },
        body: JSON.stringify({ question }),
    });
}

// Upload a file to the user document library. Returns { status, filename, chunks, message }
export async function ingestFile(userId, pin, file) {
    const formData = new FormData();
    formData.append("file", file);
    const response = await fetch(`${BASE_URL}/ingest`, {
        method: "POST",
        headers: { "X-User-ID": userId, "X-User-PIN": pin },
        body: formData,
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || `Upload error: ${response.status}`);
    return data;
}

// List all files in the user library. Returns FileRecord[]
export async function listFiles(userId, pin) {
    return request("/files", { headers: { "X-User-ID": userId, "X-User-PIN": pin } });
}

// Delete a file by its hash ID. Returns { status, id }
export async function deleteFile(userId, pin, fileId) {
    return request(`/files/${fileId}`, {
        method: "DELETE",
        headers: { "X-User-ID": userId, "X-User-PIN": pin },
    });
}

// Get dashboard stats. Returns { total_files, total_chunks, ollama_running, user_id }
export async function getStats(userId, pin) {
    return request("/stats", { headers: { "X-User-ID": userId, "X-User-PIN": pin } });
}

// Liveness probe. Returns { status: "ok" }
export async function healthCheck() {
    return request("/health");
}

export { BASE_URL };
