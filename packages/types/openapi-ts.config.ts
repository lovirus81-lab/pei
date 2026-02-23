import { defineConfig } from '@hey-api/openapi-ts';

export default defineConfig({
    client: '@hey-api/client-fetch',
    input: '../../apps/api/openapi.json',
    output: 'src/generated',
});
