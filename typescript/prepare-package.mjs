import {copyFile} from 'node:fs/promises';
await copyFile(new URL('../LICENSE', import.meta.url), new URL('LICENSE', import.meta.url));
