#!/usr/bin/env node
import { Server } from '@modelcontextprotocol/sdk';
import { StdioServerTransport } from '@modelcontextprotocol/sdk';
import { CallToolRequestSchema, ErrorCode, ListToolsRequestSchema, McpError, } from '@modelcontextprotocol/sdk';
class DateTimeServer {
    constructor() {
        this.server = new Server({
            name: 'datetime-server',
            version: '0.1.0',
        }, {
            capabilities: {
                tools: {},
            },
        });
        this.setupToolHandlers();
        // Error handling
        this.server.onerror = (error) => console.error('[MCP Error]', error);
        process.on('SIGINT', async () => {
            await this.server.close();
            process.exit(0);
        });
    }
    setupToolHandlers() {
        this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
            tools: [
                {
                    name: 'get_current_datetime',
                    description: 'Get the current date and time in various formats',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            format: {
                                type: 'string',
                                description: 'Format of the date and time (iso, locale, unix)',
                                enum: ['iso', 'locale', 'unix'],
                            },
                            timezone: {
                                type: 'string',
                                description: 'Timezone for the date and time (e.g., "America/New_York", "Europe/London")',
                            }
                        },
                        additionalProperties: false,
                    },
                },
            ],
        }));
        this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
            if (request.params.name !== 'get_current_datetime') {
                throw new McpError(ErrorCode.MethodNotFound, `Unknown tool: ${request.params.name}`);
            }
            const format = request.params.arguments?.format || 'iso';
            const timezone = request.params.arguments?.timezone;
            try {
                const now = new Date();
                let result;
                switch (format) {
                    case 'iso':
                        result = now.toISOString();
                        break;
                    case 'locale':
                        if (timezone) {
                            result = new Intl.DateTimeFormat('en-US', {
                                dateStyle: 'full',
                                timeStyle: 'long',
                                timeZone: timezone
                            }).format(now);
                        }
                        else {
                            result = now.toLocaleString();
                        }
                        break;
                    case 'unix':
                        result = Math.floor(now.getTime() / 1000).toString();
                        break;
                    default:
                        result = now.toISOString();
                }
                return {
                    content: [
                        {
                            type: 'text',
                            text: JSON.stringify({
                                datetime: result,
                                format,
                                timezone: timezone || 'UTC',
                                timestamp: now.getTime()
                            }, null, 2),
                        },
                    ],
                };
            }
            catch (error) {
                return {
                    content: [
                        {
                            type: 'text',
                            text: `Error getting date and time: ${error instanceof Error ? error.message : String(error)}`,
                        },
                    ],
                    isError: true,
                };
            }
        });
    }
    async run() {
        const transport = new StdioServerTransport();
        await this.server.connect(transport);
        console.error('DateTime MCP server running on stdio');
    }
}
const server = new DateTimeServer();
server.run().catch(console.error);
