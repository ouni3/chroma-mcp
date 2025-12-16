// --- Global Error Handlers for Robustness ---
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const errorLogPath = path.resolve(__dirname, 'server-errors.log');

// Clear previous log file on startup
if (fs.existsSync(errorLogPath)) {
    fs.unlinkSync(errorLogPath);
}

const logErrorSync = (message, error) => {
    const timestamp = new Date().toISOString();
    const logMessage = `${timestamp} - ${message}:\n${error.stack || JSON.stringify(error, null, 2)}\n\n`;
    try {
        fs.appendFileSync(errorLogPath, logMessage);
        console.error(logMessage); // Also log to console
    } catch (e) {
        console.error("FATAL: Could not even write to error log file.", e);
    }
};

process.on('unhandledRejection', (reason, promise) => {
  const error = new Error(`Unhandled Rejection: ${reason}`);
  error.stack += `\nPromise: ${JSON.stringify(promise, null, 2)}`;
  logErrorSync('FATAL: Unhandled Rejection', error);
  process.exit(1);
});

process.on('uncaughtException', (error) => {
  logErrorSync('FATAL: Uncaught Exception', error);
  process.exit(1);
});

import express from 'express';
import * as portedTools from './build/ported_tools.js';
import dotenv from 'dotenv';
import { ChromaClient } from "chromadb";
import axios from "axios";
import { OpenAIEmbeddings } from "@langchain/openai";

// --- Environment Variable Loading ---
dotenv.config({ path: path.resolve(__dirname, '.env') });

const app = express();
app.use(express.json());

const PORT = 8009;

// --- ChromaDB & API Configuration ---
const chroma_host = process.env.CHROMA_HOST || "localhost";
const chroma_port = parseInt(process.env.CHROMA_PORT || "8000", 10);
const collection_name = process.env.CHROMA_collection_name;
const api_key = process.env.OPENAI_API_KEY;
let base_url = process.env.API_BASE_URL;
const embedding_model = process.env.embedding_MODEL;

if (base_url && base_url.endsWith("/chat/completions")) {
    base_url = base_url.slice(0, -"/chat/completions".length);
}

// --- Embedding & ChromaDB Connection ---
const embeddings = new OpenAIEmbeddings({
    openAIApiKey: api_key,
    baseURL: base_url,
    modelName: embedding_model,
    maxRetries: 3,
});

// Create an adapter for the embedding function to match chromadb-ts's expected interface.
const embeddingFunction = {
    generate: async (texts) => {
        return await embeddings.embedDocuments(texts);
    }
};

const client = new ChromaClient({ host: chroma_host, port: chroma_port, ssl: false });
let collection = null;

async function initializeChroma() {
    if (collection) return true;
    if (!collection_name) {
        console.error("FATAL: CHROMA_collection_name is not set in .env.");
        return false;
    }
    try {
        console.log(`Attempting to connect to ChromaDB at http://${chroma_host}:${chroma_port} and get collection '${collection_name}'...`);
        await client.heartbeat();
        // FIX: Pass the embedding function to getCollection
        collection = await client.getCollection({ 
            name: collection_name,
            embeddingFunction: embeddingFunction 
        });
        console.log("Successfully connected to ChromaDB and loaded collection.");
        return true;
    } catch (e) {
        // Attempt to create the collection if it doesn't exist
        if (e.message.includes("does not exist")) {
            console.log(`Collection '${collection_name}' not found. Attempting to create it...`);
            try {
                collection = await client.createCollection({
                    name: collection_name,
                    embeddingFunction: embeddingFunction
                });
                console.log(`Successfully created and loaded collection '${collection_name}'.`);
                return true;
            } catch (create_e) {
                 console.error("----------------------------------------------------------------");
                 console.error(`FATAL: Failed to create collection '${collection_name}'.`, create_e.message);
                 console.error("----------------------------------------------------------------");
                 return false;
            }
        } else {
            console.error("----------------------------------------------------------------");
            console.error("FATAL: Failed to connect to ChromaDB server.", e.message);
            console.error("Please ensure the ChromaDB server is running and accessible.");
            console.error("----------------------------------------------------------------");
            return false;
        }
    }
}

// --- Tool Registry ---
const toolsRegistry = {
    // Ported Tools
    "google_search": {
        name: "google_search",
        description: "Performs an online search using the Google Search API.",
        input_schema: { type: "object", properties: { query: { type: "string" } }, required: ["query"] },
        execute: (args) => portedTools.googleSearch(args.query),
    },
    "get_webpage_content": {
        name: "get_webpage_content",
        description: "Extracts text content from a given URL.",
        input_schema: { type: "object", properties: { url: { type: "string" } }, required: ["url"] },
        execute: (args) => portedTools.getWebpageContent(args.url),
    },
    "execute_shell_command": {
        name: "execute_shell_command",
        description: "Executes a command in the system's default shell.",
        input_schema: { type: "object", properties: { command: { type: "string" } }, required: ["command"] },
        execute: (args) => portedTools.executeShellCommand(args.command),
    },
    "execute_powershell_command": {
        name: "execute_powershell_command",
        description: "Executes a PowerShell command on a Windows system.",
        input_schema: { type: "object", properties: { command: { type: "string" } }, required: ["command"] },
        execute: (args) => portedTools.executePowershellCommand(args.command),
    },
    "get_current_weather": {
        name: "get_current_weather",
        description: "Gets the current weather for a specified city.",
        input_schema: { type: "object", properties: { city: { type: "string" } }, required: ["city"] },
        execute: (args) => portedTools.getCurrentWeather(args.city),
    },
    "get_current_time": {
        name: "get_current_time",
        description: "Gets the current date and time in Beijing.",
        input_schema: { type: "object", properties: {} },
        execute: portedTools.getCurrentTime,
    },
    "get_running_processes": {
        name: "get_running_processes",
        description: "Gets a list of currently running non-system processes.",
        input_schema: { type: "object", properties: {} },
        execute: portedTools.getRunningProcesses,
    },
    "text_to_speech": {
        name: "text_to_speech",
        description: "Converts text to speech and returns a Base64 audio string.",
        input_schema: { type: "object", properties: { text: { type: "string" }, voice_name: { type: "string" } }, required: ["text"] },
        execute: (args) => portedTools.textToSpeech(args.text, args.voice_name),
    },
    // ChromaDB Tools
    "embed_texts": {
        name: "embed_texts",
        description: "Generate embeddings for a list of texts.",
        input_schema: { type: "object", properties: { texts: { type: "array", items: { type: "string" } } }, required: ["texts"] },
        execute: async (args) => {
            const result_embeddings = await embeddings.embedDocuments(args.texts);
            return { embeddings: result_embeddings };
        },
    },
    "search_chromadb": {
        name: "search_chromadb",
        description: "Search the ChromaDB collection. Supports 'keyword', 'vector', and 'mmr' search types.",
        input_schema: { type: "object", properties: { query: { type: "string" }, search_type: { type: "string", enum: ["keyword", "vector", "mmr"] } }, required: ["query", "search_type"] },
        execute: async (args) => {
            const { query, search_type } = args;
            const searchResults = [];
            if (search_type === 'keyword') {
                const all_data = await collection.get({ include: ["documents"] });
                if (all_data.documents) {
                    for (let i = 0; i < all_data.documents.length; i++) {
                        if (all_data.documents[i]?.toLowerCase().includes(query.toLowerCase())) {
                            searchResults.push({ id: all_data.ids[i], document: all_data.documents[i] });
                        }
                    }
                }
            } else if (search_type === 'vector') {
                const results = await collection.query({
                    queryTexts: [query],
                    nResults: 3,
                    include: ["documents"]
                });
                if (results.ids.length > 0 && results.ids[0].length > 0) {
                    for (let i = 0; i < results.ids[0].length; i++) {
                        searchResults.push({ id: results.ids[0][i], document: results.documents[0][i] });
                    }
                }
            } else if (search_type === 'mmr') {
                // The where: { "$mmr": {} } clause is a way to trigger MMR in some versions.
                const results = await collection.query({
                    queryTexts: [query],
                    nResults: 3,
                    include: ["documents"],
                    where: { "$mmr": {} }
                });
                if (results.ids.length > 0 && results.ids[0].length > 0) {
                    for (let i = 0; i < results.ids[0].length; i++) {
                        searchResults.push({ id: results.ids[0][i], document: results.documents[0][i] });
                    }
                }
            }
            return { results: searchResults };
        },
    },
    "upsert_document": {
        name: "upsert_document",
        description: "Upsert a document into the ChromaDB collection.",
        input_schema: { type: "object", properties: { document_id: { type: "string" }, content: { type: "string" } }, required: ["document_id", "content"] },
        execute: async (args) => {
            const { document_id, content } = args;
            await collection.upsert({ ids: [document_id], documents: [content] });
            return { success: true, message: `Document '${document_id}' upserted.` };
        },
    },
};

// --- Express Endpoints ---
app.get('/tools', (req, res) => {
    console.log('Received request for /tools');
    const toolMetas = Object.values(toolsRegistry).map(({ execute, ...meta }) => meta);
    res.json(toolMetas);
});

app.post('/invoke', async (req, res) => {
    const { tool_name, args } = req.body;
    console.log(`Received request to invoke: ${tool_name} with args:`, args);

    const tool = toolsRegistry[tool_name];
    if (!tool) {
        return res.status(404).json({ detail: `Tool '${tool_name}' not found` });
    }
    if (!collection && tool_name.includes('chromadb')) {
         return res.status(503).json({ detail: "ChromaDB is not initialized. Check server logs." });
    }

    try {
        const result = await tool.execute(args);
        res.json({ status: "success", output: result });
    } catch (error) {
        console.error(`Error invoking tool '${tool_name}':`, error);
        res.status(500).json({ detail: error.message });
    }
});

let activeServer = null; // Keep a global reference to the server

// --- Graceful Shutdown ---
function closeServer(signal) {
    console.log(`\nReceived ${signal}. Shutting down gracefully...`);
    if (activeServer) {
        activeServer.close(() => {
            console.log("Server has been closed. Exiting process.");
            process.exit(0);
        });

        // Force close after a timeout if server hangs
        setTimeout(() => {
            console.error("Could not close connections in time, forcefully shutting down.");
            process.exit(1);
        }, 10000); // 10 seconds
    } else {
        console.log("No active server to shut down. Exiting.");
        process.exit(0);
    }
}

// --- Server Startup ---
async function startServer() {
    const chromaReady = await initializeChroma();
    if (!chromaReady) {
        console.error("Server cannot start because ChromaDB initialization failed.");
        // In a test environment, we don't want to exit the process
        if (process.env.NODE_ENV !== 'test') {
            process.exit(1);
        }
        // Allow tests to handle the failure
        return null; 
    }

    const server = app.listen(PORT, () => {
        console.log(`JavaScript MCP tool server running on http://localhost:${PORT}`);
        console.log('Available tools:');
        Object.keys(toolsRegistry).forEach(name => console.log(`- ${name}`));
    });
    return server;
}

// Export for testing purposes
export { app, startServer, toolsRegistry, initializeChroma };

// This is a helper for testing to reset the module-level state.
export function __for_testing_only_reset_collection__() {
    collection = null;
}


// Start the server only if the script is run directly
if (import.meta.url.startsWith('file://') && process.argv[1] === fileURLToPath(import.meta.url)) {
    (async () => {
        try {
            const server = await startServer();
            if (server) {
                activeServer = server;
                console.log("Server startup successful. Process will remain active.");

                // DEBUGGING: Force the event loop to stay active.
                // This is a workaround for an issue where the process exits unexpectedly,
                // likely due to a dependency not holding the event loop open.
                setInterval(() => {}, 1000 * 60 * 60); // Run an empty function every hour.

                // Listen for termination signals
                process.on('SIGINT', () => closeServer('SIGINT'));
                process.on('SIGTERM', () => closeServer('SIGTERM'));
            } else {
                console.error("Server startup failed as reported in previous logs. Process exiting.");
                process.exit(1);
            }
        } catch (err) {
            logErrorSync('FATAL: Unhandled error during server startup process', err);
            process.exit(1);
        }
    })();
}
