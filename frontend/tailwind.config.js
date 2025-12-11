/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                cyber: {
                    bg: '#020617', // Çok koyu lacivert/siyah
                    panel: '#0f172a', // Panel arka planı
                    border: '#1e293b',
                    primary: '#06b6d4', // Cyan (Neon Mavi)
                    accent: '#f43f5e', // Neon Kırmızı (Alertler için)
                    text: '#94a3b8', // Sönük metin
                    textLight: '#e2e8f0', // Parlak metin
                }
            },
            fontFamily: {
                mono: ['"JetBrains Mono"', 'monospace'], // Terminal havası için
                sans: ['Inter', 'sans-serif'],
            }
        },
    },
    plugins: [],
}
