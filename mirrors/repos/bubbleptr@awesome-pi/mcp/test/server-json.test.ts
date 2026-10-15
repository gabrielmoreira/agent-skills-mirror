import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { describe, test } from 'node:test';
import Ajv from 'ajv';
import addFormats from 'ajv-formats';

const schemaUrl = 'https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json';

describe('MCP registry server.json', () => {
  test('matches package.json and the official schema', async () => {
    const server = JSON.parse(readFileSync(new URL('../server.json', import.meta.url), 'utf8')) as {
      name: string; description: string; version: string;
      packages: { identifier: string; version: string; transport: { type: string }; registryType: string }[];
    };
    const pkg = JSON.parse(readFileSync(new URL('../package.json', import.meta.url), 'utf8')) as {
      name: string; version: string; mcpName: string;
    };
    assert.equal(server.name, 'io.github.bubbleptr/piindex');
    assert.equal(pkg.mcpName, server.name);
    assert.equal(server.version, pkg.version);
    assert.equal(server.packages[0].identifier, pkg.name);
    assert.equal(server.packages[0].version, pkg.version);
    assert.equal(server.packages[0].registryType, 'npm');
    assert.equal(server.packages[0].transport.type, 'stdio');
    assert.ok(server.description.length > 0 && server.description.length <= 100);

    const response = await fetch(schemaUrl);
    assert.equal(response.ok, true);
    const schema: unknown = await response.json();
    const ajv = new Ajv({ strict: false, allErrors: true, validateSchema: false });
    addFormats(ajv);
    const validate = ajv.compile(schema as object);
    const valid = validate(server);
    assert.equal(valid, true, JSON.stringify(validate.errors, null, 2));
  });
});
