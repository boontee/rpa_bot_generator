#!/usr/bin/env node
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import * as fs from "fs";
import * as readline from "readline";
import * as path from "path";
import * as os from "os";
// Resolve log path dynamically on access: supports RPA_STUDIO_LOG, STUDIO_LOG_PATH, or STUDIO_LOG env vars
const DEFAULT_LOG_PATH = path.join(os.homedir(), "AppData", "Local", "IBM Robotic Process Automation", "Studio.log");
function getLogPath() {
    return (process.env.RPA_STUDIO_LOG ||
        process.env.STUDIO_LOG_PATH ||
        process.env.STUDIO_LOG ||
        DEFAULT_LOG_PATH);
}
const server = new McpServer({ name: "rpa-studio-log", version: "0.1.0" });
// ── Tool: read_studio_log ──────────────────────────────────────────────────
server.registerTool("read_studio_log", {
    description: "Read the last N lines of the IBM RPA Studio log file to diagnose WAL script errors. " +
        "Returns lines containing ERROR, Exception, ParseException, or ProtoException highlighted " +
        "at the top, followed by the raw tail for full context.",
    inputSchema: z.object({
        lines: z
            .number()
            .int()
            .min(1)
            .max(500)
            .default(50)
            .describe("Number of lines to read from the end of the log (default 50, max 500)"),
        filter: z
            .string()
            .optional()
            .describe("Optional substring filter — only return lines containing this text (case-insensitive)"),
    }),
}, async ({ lines, filter }) => {
    const logPath = getLogPath();
    if (!fs.existsSync(logPath)) {
        return {
            content: [
                {
                    type: "text",
                    text: `Log file not found: ${logPath}\n\nSet the RPA_STUDIO_LOG, STUDIO_LOG_PATH, or STUDIO_LOG environment variable to override the path.`,
                },
            ],
            isError: true,
        };
    }
    try {
        const tail = await readTailLines(logPath, lines);
        // Extract error lines for quick summary
        const errorPattern = /error|exception|not found|invalid wire/i;
        const errorLines = tail.filter((l) => errorPattern.test(l));
        let output = "";
        if (errorLines.length > 0) {
            output += `=== ERRORS / EXCEPTIONS (${errorLines.length} lines) ===\n`;
            output += errorLines.join("\n");
            output += "\n\n";
        }
        let displayLines = tail;
        if (filter) {
            const lowerFilter = filter.toLowerCase();
            displayLines = tail.filter((l) => l.toLowerCase().includes(lowerFilter));
            output += `=== FILTERED (containing "${filter}") — ${displayLines.length} of ${tail.length} lines ===\n`;
        }
        else {
            output += `=== LAST ${tail.length} LINES of ${logPath} ===\n`;
        }
        output += displayLines.join("\n");
        return { content: [{ type: "text", text: output }] };
    }
    catch (err) {
        return {
            content: [
                {
                    type: "text",
                    text: `Failed to read log: ${err instanceof Error ? err.message : String(err)}`,
                },
            ],
            isError: true,
        };
    }
});
// ── Tool: get_log_path ─────────────────────────────────────────────────────
server.registerTool("get_log_path", {
    description: "Returns the Studio.log path this server is currently watching.",
    inputSchema: z.object({}),
}, async () => {
    const logPath = getLogPath();
    const exists = fs.existsSync(logPath);
    return {
        content: [
            {
                type: "text",
                text: `Log path : ${logPath}\nExists   : ${exists}\nOverride : set RPA_STUDIO_LOG, STUDIO_LOG_PATH, or STUDIO_LOG env var to change`,
            },
        ],
    };
});
// ── Helper: read last N lines efficiently ─────────────────────────────────
async function readTailLines(filePath, n) {
    return new Promise((resolve, reject) => {
        const results = [];
        const stream = fs.createReadStream(filePath, { encoding: "utf8" });
        const rl = readline.createInterface({ input: stream, crlfDelay: Infinity });
        rl.on("line", (line) => {
            results.push(line);
            if (results.length > n)
                results.shift();
        });
        rl.on("close", () => resolve(results));
        rl.on("error", reject);
        stream.on("error", reject);
    });
}
// ── Start ──────────────────────────────────────────────────────────────────
async function main() {
    const transport = new StdioServerTransport();
    await server.connect(transport);
    console.error(`rpa-studio-log running — watching: ${getLogPath()}`);
}
main().catch((err) => {
    console.error("Fatal error:", err);
    process.exit(1);
});
