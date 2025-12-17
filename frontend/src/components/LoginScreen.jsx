import { useState } from 'react';

const LoginScreen = ({ onLogin }) => {
    const [code, setCode] = useState('');
    const [error, setError] = useState(false);
    const [loading, setLoading] = useState(false);

    // Bu şifreyi .env dosyasından da çekebilirsin: import.meta.env.VITE_ACCESS_CODE
    const CORRECT_CODE = "NOMAD_2025";

    const handleAccess = (e) => {
        e.preventDefault();
        setLoading(true);
        setError(false);

        // Yapay bir gecikme ekleyelim ki "Decrypting..." hissi versin
        setTimeout(() => {
            if (code === CORRECT_CODE) {
                localStorage.setItem('nomad_auth', 'GRANTED'); // Tarayıcıya kaydet
                onLogin();
            } else {
                setError(true);
                setCode(''); // Şifreyi temizle
            }
            setLoading(false);
        }, 800);
    };

    return (
        <div className="h-screen w-full bg-[#050510] flex items-center justify-center font-mono text-white overflow-hidden relative">
            {/* Arka Plan Efekti (Scanlines) */}
            <div className="absolute inset-0 bg-[url('https://media.giphy.com/media/Hp4lpBKvI7vD8Wj3lV/giphy.gif')] opacity-5 pointer-events-none"></div>

            <div className="z-10 w-full max-w-md p-8 border border-gray-800 bg-black/80 backdrop-blur-md rounded-xl shadow-[0_0_50px_rgba(0,243,255,0.1)]">
                <div className="text-center mb-8">
                    <h1 className="text-4xl font-bold font-orbitron tracking-widest text-white mb-2">
                        NOMAD <span className="text-neon-blue">OS</span>
                    </h1>
                    <div className="h-px w-24 bg-neon-blue mx-auto mb-4 shadow-[0_0_10px_#00f3ff]"></div>
                    <p className="text-xs text-gray-500 tracking-[0.3em]">SECURE INTELLIGENCE UPLINK</p>
                </div>

                <form onSubmit={handleAccess} className="space-y-6">
                    <div className="relative group">
                        <input
                            type="password"
                            value={code}
                            onChange={(e) => setCode(e.target.value)}
                            placeholder="ENTER CLEARANCE CODE"
                            className={`w-full bg-[#0a0a15] border ${error ? 'border-red-500 animate-pulse' : 'border-gray-700 focus:border-neon-blue'} text-center text-xl py-4 rounded outline-none transition-all placeholder-gray-700 tracking-widest`}
                            autoFocus
                        />
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className={`w-full py-4 font-bold tracking-widest text-sm transition-all duration-300 
              ${error
                                ? 'bg-red-900/20 text-red-500 border border-red-500'
                                : 'bg-neon-blue/10 text-neon-blue border border-neon-blue hover:bg-neon-blue hover:text-black hover:shadow-[0_0_20px_#00f3ff]'
                            }`}
                    >
                        {loading ? 'DECRYPTING...' : error ? 'ACCESS DENIED // RETRY' : 'ESTABLISH UPLINK'}
                    </button>
                </form>

                <div className="mt-8 text-center">
                    <p className="text-[10px] text-gray-600">
                        SYSTEM ID: 0x84F1 // ENCRYPTION: AES-256
                        <br />UNAUTHORIZED ACCESS IS A FELONY.
                    </p>
                </div>
            </div>
        </div>
    );
};

export default LoginScreen;
