import { defineConfig } from 'vite'
import path from 'path'
import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
	plugins: [
		// The React and Tailwind plugins are both required for Make, even if
		// Tailwind is not being actively used – do not remove them
		react(),
		tailwindcss(),
	],
	resolve: {
		alias: {
			// Alias @ to the src directory
			'@': path.resolve(__dirname, './src'),
		},
	},

	server: {
		proxy: {
			'/api': {
				target: ' https://41a26052-7573-46b7-9b89-99db3c39f378.tunnel4.com',
				changeOrigin: true,
				secure: false,
			},
		},
	},

	// File types to support raw imports. Never add .css, .tsx, or .ts files to this.
	assetsInclude: ['**/*.svg', '**/*.csv'],
})
