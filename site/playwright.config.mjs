import { defineConfig } from '@playwright/test';
export default defineConfig({testDir: './tests', use:{baseURL:'http://127.0.0.1:4173'}, webServer:{command:'python3 -m http.server 4173 --bind 127.0.0.1 --directory dist',url:'http://127.0.0.1:4173'}, reporter:'list'});
