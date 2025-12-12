import psycopg2
import uuid

# Veritabanı Bağlantısı
def get_db_connection():
    conn_string = "postgresql://postgres:mypassword@localhost:5432/nomad?sslmode=disable"
    return psycopg2.connect(conn_string)

MOCK_DATA = [
    {
        "content": "DeepMind AlphaFold 3 Announced | Tags: AI, SCIENCE, TECH | Insight: Protein folding solved with higher accuracy, massive implications for drug discovery. | Link: https://deepmind.google/technologies/alphafold/",
        "embedding": str([0.1]*768) # Fake embedding
    },
    {
        "content": "OpenAI GPT-5 Rumors | Tags: AI, TECH | Insight: Expected to reach AGI levels, multimodal capabilities enhanced. | Link: https://openai.com/blog",
        "embedding": str([0.1]*768)
    },
    {
        "content": "NVIDIA Blackwell B200 Chip | Tags: TECH, AI, HARDWARE | Insight: 30x performance increase for inference, crucial for next-gen models. | Link: https://nvidianews.nvidia.com/",
        "embedding": str([0.1]*768)
    },
    {
        "content": "Quantum Supremacy Achieved by Google | Tags: SCIENCE, QUANTUM, TECH | Insight: Sycamore processor solves problem extensively faster than Frontier supercomputer. | Link: https://research.google/teams/applied-science/quantum/",
        "embedding": str([0.1]*768)
    },
    {
        "content": "Zero-Day Exploit found in iOS 18 | Tags: CYBERSEC, APPLE, TECH | Insight: Critical vulnerability allowing remote code execution via iMessage. | Link: https://support.apple.com/en-us/HT201222",
        "embedding": str([0.1]*768)
    },
    {
        "content": "Bitcoin Halving Event 2024 | Tags: CRYPTO, FINANCE | Insight: Supply shock expected to drive price volatility in Q4. | Link: https://www.coindesk.com/learn/bitcoin-halving-explained/",
        "embedding": str([0.1]*768)
    },
    {
        "content": "SpaceX Starship Successful Orbit | Tags: SCIENCE, SPACE, TECH | Insight: Reusability demonstrated, cost to orbit drops significantly. | Link: https://www.spacex.com/vehicles/starship/",
        "embedding": str([0.1]*768)
    },
    {
        "content": "Meta Llama 3 Open Source Release | Tags: AI, DEV, OPENSOURCE | Insight: Shifts power dynamic away from closed models, allowing local fine-tuning. | Link: https://ai.meta.com/llama/",
        "embedding": str([0.1]*768)
    },
    {
        "content": "Rust Linux Kernel Integration | Tags: DEV, LINUX, TECH | Insight: Memory safety improvements for OS level programming becoming standard. | Link: https://rust-for-linux.com/",
        "embedding": str([0.1]*768)
    },
    {
        "content": "EU AI Act Passed | Tags: AI, LAW, GOV | Insight: First major regulatory framework for AI, restricting high-risk use cases. | Link: https://artificialintelligenceact.eu/",
        "embedding": str([0.1]*768)
    },
    {
        "content": "Solar Storm Hits Earth | Tags: SCIENCE, SPACE | Insight: G5 geomagnetic storm caused radio blackouts and aurora, infrastructure risks assessed. | Link: https://www.swpc.noaa.gov/",
        "embedding": str([0.1]*768)
    },
    {
        "content": "Python 3.13 Remove GIL | Tags: DEV, PYTHON, TECH | Insight: True multi-threading support coming, massive performance boost for CPU bound tasks. | Link: https://docs.python.org/3.13/whatsnew/3.13.html",
        "embedding": str([0.1]*768)
    },
    {
        "content": "Solana Congestion Fix | Tags: CRYPTO, DEV | Insight: v1.18 patch addresses transaction failures, network stability returns. | Link: https://solana.com/news",
        "embedding": str([0.1]*768)
    },
    {
        "content": "LockBit Ransomware Takedown | Tags: CYBERSEC, CRIME | Insight: International law enforcement operation seized infrastructure, decryptors released. | Link: https://www.europol.europa.eu/media-press/newsroom/news/law-enforcement-disrupt-worlds-biggest-ransomware-operation",
        "embedding": str([0.1]*768)
    },
    {
        "content": "Neuralink Human Patient Update | Tags: SCIENCE, AI, BIOTECH | Insight: Patient controlling mouse with thoughts, telepathy interface viable. | Link: https://neuralink.com/blog/",
        "embedding": str([0.1]*768)
    },
    {
        "content": "Docker Desktop Pricing Changes | Tags: DEV, TECH | Insight: Enterprise licensing costs increasing, alternatives like Podman gaining traction. | Link: https://www.docker.com/pricing/",
        "embedding": str([0.1]*768)
    },
    {
        "content": "React 19 Compiler Beta | Tags: DEV, REACT, TECH | Insight: Auto-memoization removes need for useMemo/useCallback, checking out. | Link: https://react.dev/blog/2024/02/15/react-labs-what-we-have-been-working-on-february-2024",
        "embedding": str([0.1]*768)
    },
    {
        "content": "Google Gemini 1.5 Pro | Tags: AI, GOOGLE, TECH | Insight: 1M token context window allows analyzing entire codebases or books at once. | Link: https://blog.google/technology/ai/google-gemini-next-generation-model-february-2024/",
        "embedding": str([0.1]*768)
    },
    {
        "content": "Apple Vision Pro VisionOS 2 | Tags: TECH, VR, APPLE | Insight: Spatial computing adoption slow but software ecosystem growing. | Link: https://www.apple.com/apple-vision-pro/",
        "embedding": str([0.1]*768)
    },
    {
        "content": "PostgreSQL Vector Search Perf | Tags: DEV, DB, AI | Insight: pgvector 0.7.0 adds HNSW indexing speedups, competitive with Pinecone. | Link: https://github.com/pgvector/pgvector",
        "embedding": str([0.1]*768)
    }
]

def load_data():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        print(f"Loading {len(MOCK_DATA)} mock records...")
        
        for item in MOCK_DATA:
            cursor.execute(
                "INSERT INTO agent_memory (content, embedding) VALUES (%s, %s)",
                (item["content"], item["embedding"])
            )
        
        conn.commit()
        cursor.close()
        conn.close()
        print("SUCCESS: Mock data loaded successfully! 🦅")
        
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    load_data()
