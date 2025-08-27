import streamlit as st
import platform
import json
import psutil
import subprocess

# Try to import GPU detection libraries
try:
    import pynvml
    PYNVML_AVAILABLE = True
except ImportError:
    PYNVML_AVAILABLE = False

try:
    import cpuinfo
    CPUINFO_AVAILABLE = True
except ImportError:
    CPUINFO_AVAILABLE = False

# Set page config
st.set_page_config(
    page_title="GPU Detector Pro",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for modern UI
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 25%, #16213e 50%, #0f3460 75%, #533483 100%);
        padding: 4rem 2rem;
        border-radius: 24px;
        margin-bottom: 3rem;
        text-align: center;
        color: white;
        box-shadow: 
            0 25px 50px rgba(0, 0, 0, 0.4),
            0 0 0 1px rgba(255, 255, 255, 0.1),
            inset 0 1px 0 rgba(255, 255, 255, 0.2);
        position: relative;
        overflow: hidden;
        backdrop-filter: blur(10px);
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: 
            radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
            radial-gradient(circle at 80% 20%, rgba(255, 119, 198, 0.3) 0%, transparent 50%),
            radial-gradient(circle at 40% 40%, rgba(120, 219, 255, 0.2) 0%, transparent 50%);
        animation: float 6s ease-in-out infinite;
    }
    
    .main-header::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="0.5"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
        pointer-events: none;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-10px) rotate(1deg); }
    }
    
    .main-header h1 {
        font-size: 4rem;
        font-weight: 800;
        margin-bottom: 1rem;
        text-shadow: 
            0 0 20px rgba(120, 119, 198, 0.5),
            0 0 40px rgba(120, 119, 198, 0.3),
            0 0 60px rgba(120, 119, 198, 0.1);
        background: linear-gradient(45deg, #fff, #a8a8ff, #fff);
        background-size: 200% 200%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shimmer 3s ease-in-out infinite;
        position: relative;
        z-index: 1;
    }
    
    @keyframes shimmer {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    .main-header p {
        font-size: 1.4rem;
        font-weight: 300;
        opacity: 0.9;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        position: relative;
        z-index: 1;
    }
    
    .metric-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        padding: 2.5rem;
        border-radius: 20px;
        box-shadow: 
            0 8px 32px rgba(0, 0, 0, 0.1),
            0 0 0 1px rgba(255, 255, 255, 0.2),
            inset 0 1px 0 rgba(255, 255, 255, 0.3);
        margin-bottom: 2rem;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    .metric-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 
            0 20px 60px rgba(0, 0, 0, 0.15),
            0 0 0 1px rgba(255, 255, 255, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.4);
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #667eea, #764ba2, #f093fb, #667eea);
        background-size: 200% 100%;
        animation: gradient-shift 3s ease infinite;
    }
    
    @keyframes gradient-shift {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    .gpu-card {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        backdrop-filter: blur(20px);
        color: #333;
        padding: 2.5rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 
            0 8px 32px rgba(102, 126, 234, 0.15),
            0 0 0 1px rgba(102, 126, 234, 0.2),
            inset 0 1px 0 rgba(255, 255, 255, 0.3);
        border: 2px solid rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .gpu-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 
            0 20px 60px rgba(102, 126, 234, 0.25),
            0 0 0 1px rgba(102, 126, 234, 0.4),
            inset 0 1px 0 rgba(255, 255, 255, 0.4);
        border-color: rgba(102, 126, 234, 0.6);
    }
    
    .gpu-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #667eea, #764ba2, #f093fb, #667eea);
        background-size: 200% 100%;
        animation: gradient-shift 3s ease infinite;
    }
    
    .gpu-card h3 {
        color: #667eea;
        font-weight: 700;
        margin-bottom: 1.5rem;
        font-size: 1.4rem;
        text-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }
    
    .detect-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        border: none;
        border-radius: 50px;
        padding: 1.5rem 4rem;
        color: white;
        font-size: 1.4rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 
            0 8px 25px rgba(102, 126, 234, 0.4),
            0 0 0 1px rgba(255, 255, 255, 0.2),
            inset 0 1px 0 rgba(255, 255, 255, 0.3);
        position: relative;
        overflow: hidden;
        font-family: 'JetBrains Mono', monospace;
        letter-spacing: 0.5px;
    }
    
    .detect-button:hover {
        transform: translateY(-4px) scale(1.05);
        box-shadow: 
            0 15px 40px rgba(102, 126, 234, 0.6),
            0 0 0 1px rgba(255, 255, 255, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.4);
    }
    
    .detect-button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
        transition: left 0.6s;
    }
    
    .detect-button:hover::before {
        left: 100%;
    }
    
    .success-message {
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        color: white;
        padding: 2rem;
        border-radius: 16px;
        text-align: center;
        margin: 2rem 0;
        box-shadow: 
            0 8px 25px rgba(76, 175, 80, 0.3),
            0 0 0 1px rgba(255, 255, 255, 0.2);
        font-weight: 600;
        font-size: 1.1rem;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .error-message {
        background: linear-gradient(135deg, #f44336 0%, #d32f2f 100%);
        color: white;
        padding: 2rem;
        border-radius: 16px;
        text-align: center;
        margin: 2rem 0;
        box-shadow: 
            0 8px 25px rgba(244, 67, 54, 0.3),
            0 0 0 1px rgba(255, 255, 255, 0.2);
        font-weight: 600;
        font-size: 1.1rem;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .info-box {
        background: linear-gradient(135deg, rgba(248, 249, 250, 0.9) 0%, rgba(233, 236, 239, 0.9) 100%);
        backdrop-filter: blur(20px);
        border-left: 4px solid #667eea;
        padding: 2.5rem;
        border-radius: 16px;
        margin: 2.5rem 0;
        box-shadow: 
            0 8px 32px rgba(0, 0, 0, 0.08),
            0 0 0 1px rgba(255, 255, 255, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    .info-box h3 {
        color: #667eea;
        font-weight: 700;
        margin-bottom: 1.5rem;
        font-size: 1.4rem;
    }
    
    .progress-container {
        background: rgba(248, 249, 250, 0.8);
        backdrop-filter: blur(10px);
        border-radius: 12px;
        padding: 1rem;
        margin: 1.5rem 0;
        border: 1px solid rgba(233, 236, 239, 0.5);
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        color: #667eea;
        margin-bottom: 0.8rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
        font-family: 'JetBrains Mono', monospace;
        letter-spacing: -0.5px;
    }
    
    .metric-label {
        color: #6c757d;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
        margin-bottom: 0.5rem;
        font-family: 'JetBrains Mono', monospace;
    }
    
    .metric-card h3, .gpu-card h3 {
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 2rem;
        color: #333;
        text-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }
    
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1.5rem;
        margin: 1.5rem 0;
    }
    
    .stat-item {
        background: rgba(102, 126, 234, 0.08);
        backdrop-filter: blur(10px);
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        border: 1px solid rgba(102, 126, 234, 0.2);
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.1);
    }
    
    .stat-item:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.2);
        background: rgba(102, 126, 234, 0.12);
    }
    
    .stat-value {
        font-size: 2rem;
        font-weight: 800;
        color: #667eea;
        font-family: 'JetBrains Mono', monospace;
        text-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }
    
    .stat-label {
        font-size: 0.8rem;
        color: #6c757d;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
        font-family: 'JetBrains Mono', monospace;
        margin-top: 0.5rem;
    }
    
    .footer {
        background: linear-gradient(135deg, rgba(248, 249, 250, 0.9) 0%, rgba(233, 236, 239, 0.9) 100%);
        backdrop-filter: blur(20px);
        padding: 2.5rem;
        border-radius: 16px;
        text-align: center;
        margin-top: 3rem;
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 
            0 8px 32px rgba(0, 0, 0, 0.08),
            0 0 0 1px rgba(255, 255, 255, 0.2);
    }
    
    .footer p {
        color: #6c757d;
        font-weight: 600;
        margin: 0;
        font-size: 1.1rem;
        font-family: 'JetBrains Mono', monospace;
    }
    
    .loading-animation {
        display: inline-block;
        width: 24px;
        height: 24px;
        border: 3px solid rgba(255,255,255,.3);
        border-radius: 50%;
        border-top-color: #fff;
        animation: spin 1s ease-in-out infinite;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 1.5rem;
        display: block;
        filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
    }
    
    .section-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, #667eea, #764ba2, #f093fb, transparent);
        margin: 3rem 0;
        border: none;
        border-radius: 1px;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
    }
    
    /* Particle effect for background */
    .particles {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: -1;
    }
    
    .particle {
        position: absolute;
        width: 2px;
        height: 2px;
        background: rgba(102, 126, 234, 0.3);
        border-radius: 50%;
        animation: float-particle 8s infinite linear;
    }
    
    @keyframes float-particle {
        0% { transform: translateY(100vh) translateX(0); opacity: 0; }
        10% { opacity: 1; }
        90% { opacity: 1; }
        100% { transform: translateY(-100px) translateX(100px); opacity: 0; }
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 2.5rem;
        }
        
        .main-header p {
            font-size: 1.1rem;
        }
        
        .metric-card, .gpu-card {
            padding: 1.5rem;
        }
        
        .stats-grid {
            grid-template-columns: repeat(2, 1fr);
        }
    }
</style>
""", unsafe_allow_html=True)

def get_system_info():
    """Get basic system information"""
    return {
        "platform": platform.system(),
        "platform_version": platform.version(),
        "architecture": platform.machine(),
        "processor": platform.processor(),
        "python_version": platform.python_version()
    }

def get_gpu_info():
    """Get GPU information using available backends"""
    gpu_info = {
        "detected": False,
        "gpus": [],
        "backend": "none",
        "error": None
    }
    
    # Try NVIDIA GPUs first
    if PYNVML_AVAILABLE:
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            
            for i in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                
                # Get GPU name
                name = pynvml.nvmlDeviceGetName(handle)
                if isinstance(name, bytes):
                    name = name.decode('utf-8')
                
                # Get memory info
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                memory_total_gb = memory_info.total // (1024**3)
                
                # Get driver version
                driver_version = pynvml.nvmlSystemGetDriverVersion()
                if isinstance(driver_version, bytes):
                    driver_version = driver_version.decode('utf-8')
                
                gpu_data = {
                    "name": name,
                    "memory_gb": memory_total_gb,
                    "driver_version": driver_version,
                    "type": "NVIDIA"
                }
                
                gpu_info["gpus"].append(gpu_data)
            
            if gpu_info["gpus"]:
                gpu_info["detected"] = True
                gpu_info["backend"] = "nvidia"
            
            pynvml.nvmlShutdown()
            
        except Exception as e:
            gpu_info["error"] = f"NVIDIA detection failed: {str(e)}"
    
    # If no NVIDIA GPUs found, try other methods
    if not gpu_info["detected"]:
        # Try using system commands
        try:
            if platform.system() == "Darwin":  # macOS
                # Try to get GPU info using system_profiler
                result = subprocess.run(['system_profiler', 'SPDisplaysDataType'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    # Parse the output to find GPU info
                    lines = result.stdout.split('\n')
                    gpu_name = None
                    gpu_memory = "Unknown"
                    
                    for line in lines:
                        if 'Chipset Model:' in line:
                            gpu_name = line.split(':')[1].strip()
                        elif 'VRAM' in line and 'Total' in line:
                            # Try to extract memory info
                            memory_match = line.split(':')[1].strip()
                            if memory_match != '':
                                gpu_memory = memory_match
                    
                    # If no specific GPU found, try to detect Apple Silicon
                    if not gpu_name:
                        # Check for Apple Silicon
                        if platform.machine() == 'arm64':
                            # Try to get more specific info
                            try:
                                result = subprocess.run(['sysctl', '-n', 'machdep.cpu.brand_string'], 
                                                      capture_output=True, text=True, timeout=5)
                                if result.returncode == 0 and 'Apple' in result.stdout:
                                    cpu_info = result.stdout.strip()
                                    if 'M1' in cpu_info:
                                        if 'Pro' in cpu_info:
                                            gpu_name = "Apple M1 Pro"
                                        elif 'Max' in cpu_info:
                                            gpu_name = "Apple M1 Max"
                                        elif 'Ultra' in cpu_info:
                                            gpu_name = "Apple M1 Ultra"
                                        else:
                                            gpu_name = "Apple M1"
                                    elif 'M2' in cpu_info:
                                        if 'Pro' in cpu_info:
                                            gpu_name = "Apple M2 Pro"
                                        elif 'Max' in cpu_info:
                                            gpu_name = "Apple M2 Max"
                                        elif 'Ultra' in cpu_info:
                                            gpu_name = "Apple M2 Ultra"
                                        else:
                                            gpu_name = "Apple M2"
                                    elif 'M3' in cpu_info:
                                        if 'Pro' in cpu_info:
                                            gpu_name = "Apple M3 Pro"
                                        elif 'Max' in cpu_info:
                                            gpu_name = "Apple M3 Max"
                                        elif 'Ultra' in cpu_info:
                                            gpu_name = "Apple M3 Ultra"
                                        else:
                                            gpu_name = "Apple M3"
                            except:
                                gpu_name = "Apple Silicon GPU"
                    
                    if gpu_name:
                        gpu_info["gpus"].append({
                            "name": gpu_name,
                            "memory_gb": gpu_memory,
                            "driver_version": "macOS",
                            "type": "Apple/AMD/Intel"
                        })
                        gpu_info["detected"] = True
                        gpu_info["backend"] = "system_profiler"
            
            elif platform.system() == "Windows":
                # Try using wmic for Windows
                result = subprocess.run(['wmic', 'path', 'win32_VideoController', 'get', 'name'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')[1:]  # Skip header
                    for line in lines:
                        if line.strip():
                            gpu_info["gpus"].append({
                                "name": line.strip(),
                                "memory_gb": "Unknown",
                                "driver_version": "Windows",
                                "type": "Unknown"
                            })
                            gpu_info["detected"] = True
                            gpu_info["backend"] = "wmic"
            
            elif platform.system() == "Linux":
                # Try using lspci for Linux
                result = subprocess.run(['lspci', '-v'], capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    lines = result.stdout.split('\n')
                    for line in lines:
                        if 'VGA compatible controller' in line or '3D controller' in line:
                            gpu_name = line.split(':')[2].strip()
                            gpu_info["gpus"].append({
                                "name": gpu_name,
                                "memory_gb": "Unknown",
                                "driver_version": "Linux",
                                "type": "Unknown"
                            })
                            gpu_info["detected"] = True
                            gpu_info["backend"] = "lspci"
                            
        except Exception as e:
            gpu_info["error"] = f"System detection failed: {str(e)}"
    
    return gpu_info

def get_cpu_info():
    """Get CPU information"""
    cpu_info = {
        "name": "Unknown",
        "cores": psutil.cpu_count(),
        "physical_cores": psutil.cpu_count(logical=False),
        "frequency": "Unknown"
    }
    
    # Try to get CPU frequency safely
    try:
        cpu_freq = psutil.cpu_freq()
        if cpu_freq and cpu_freq.current:
            cpu_info["frequency"] = f"{cpu_freq.current:.0f}"
    except:
        pass
    
    # Try multiple methods to get CPU name
    if CPUINFO_AVAILABLE:
        try:
            info = cpuinfo.get_cpu_info()
            cpu_info["name"] = info.get('brand_raw', 'Unknown')
        except:
            pass
    
    # If cpuinfo failed, try system-specific methods
    if cpu_info["name"] == "Unknown":
        try:
            if platform.system() == "Darwin":  # macOS
                result = subprocess.run(['sysctl', '-n', 'machdep.cpu.brand_string'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    cpu_info["name"] = result.stdout.strip()
            elif platform.system() == "Linux":
                # Try reading from /proc/cpuinfo
                try:
                    with open('/proc/cpuinfo', 'r') as f:
                        for line in f:
                            if line.startswith('model name'):
                                cpu_info["name"] = line.split(':')[1].strip()
                                break
                except:
                    pass
        except:
            pass
    
    return cpu_info

def get_memory_info():
    """Get memory information"""
    memory = psutil.virtual_memory()
    return {
        "total_gb": round(memory.total / (1024**3), 2),
        "available_gb": round(memory.available / (1024**3), 2),
        "used_gb": round(memory.used / (1024**3), 2),
        "percent_used": memory.percent
    }

# Main Streamlit UI
st.markdown("""
<div class="main-header">
    <h1>🚀 GPU Detector Pro</h1>
    <p>Advanced Hardware Analysis & System Diagnostics</p>
</div>

<script>
// Create floating particles
function createParticles() {
    const particlesContainer = document.createElement('div');
    particlesContainer.className = 'particles';
    document.body.appendChild(particlesContainer);
    
    for (let i = 0; i < 20; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        particle.style.left = Math.random() * 100 + '%';
        particle.style.animationDelay = Math.random() * 8 + 's';
        particle.style.animationDuration = (Math.random() * 4 + 6) + 's';
        particlesContainer.appendChild(particle);
    }
}

// Initialize particles when page loads
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', createParticles);
} else {
    createParticles();
}
</script>
""", unsafe_allow_html=True)

# Add some spacing
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# Detection button with modern styling
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🔍 Detect My Hardware", type="primary", use_container_width=True):
        with st.spinner("🔍 Analyzing your system..."):
            try:
                # Get all system information
                system_info = get_system_info()
                gpu_info = get_gpu_info()
                cpu_info = get_cpu_info()
                memory_info = get_memory_info()
                
                # Success message
                st.markdown("""
                <div class="success-message">
                    ✅ Hardware detection completed successfully!
                </div>
                """, unsafe_allow_html=True)
                
                # Display results in modern cards
                col1, col2 = st.columns(2)
                
                with col1:
                    # GPU Information Card
                    if gpu_info["detected"] and gpu_info["gpus"]:
                        for i, gpu in enumerate(gpu_info["gpus"]):
                            st.markdown(f"""
                            <div class="gpu-card">
                                <h3>🎮 GPU {i+1}</h3>
                                <div class="metric-value">{gpu['name']}</div>
                                <div class="metric-label">Memory: {gpu['memory_gb']} GB</div>
                                <div class="metric-label">Driver: {gpu['driver_version']}</div>
                                <div class="metric-label">Type: {gpu['type']}</div>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <div class="error-message">
                            ❌ No GPU detected
                        </div>
                        """, unsafe_allow_html=True)
                        if gpu_info["error"]:
                            st.caption(f"Error: {gpu_info['error']}")
                    
                    # Memory Information Card
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>💾 Memory</h3>
                        <div class="metric-value">{memory_info['total_gb']} GB</div>
                        <div class="metric-label">Total RAM</div>
                        <div class="progress-container">
                            <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); 
                                        width: {memory_info['percent_used']}%; 
                                        height: 8px; 
                                        border-radius: 4px;"></div>
                        </div>
                        <div class="metric-label">Used: {memory_info['used_gb']} GB ({memory_info['percent_used']}%)</div>
                        <div class="metric-label">Available: {memory_info['available_gb']} GB</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    # System Information Card
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>🖥️ System</h3>
                        <div class="metric-value">{system_info['platform']}</div>
                        <div class="metric-label">Platform</div>
                        <div class="metric-label">Architecture: {system_info['architecture']}</div>
                        <div class="metric-label">Python: {system_info['python_version']}</div>
                        <div class="metric-label">Processor: {system_info['processor']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # CPU Information Card
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>⚡ CPU</h3>
                        <div class="metric-value">{cpu_info['name']}</div>
                        <div class="metric-label">Model</div>
                        <div class="metric-label">Cores: {cpu_info['cores']} ({cpu_info['physical_cores']} physical)</div>
                        <div class="metric-label">Frequency: {cpu_info['frequency']} MHz</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Add a stats summary section
                st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
                st.markdown(f"""
                <div class="info-box">
                    <h3>📊 System Summary</h3>
                    <div class="stats-grid">
                        <div class="stat-item">
                            <div class="stat-value">{memory_info['total_gb']} GB</div>
                            <div class="stat-label">Total Memory</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value">{cpu_info['cores']}</div>
                            <div class="stat-label">CPU Cores</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value">{len(gpu_info['gpus'])}</div>
                            <div class="stat-label">GPU Count</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value">{system_info['platform']}</div>
                            <div class="stat-label">Platform</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
            except Exception as e:
                st.markdown(f"""
                <div class="error-message">
                    ❌ Error during detection: {str(e)}
                </div>
                """, unsafe_allow_html=True)

# Add some helpful information
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
st.markdown("""
<div class="info-box">
    <h3>ℹ️ About GPU Detector Pro</h3>
    <p>Advanced hardware analysis tool that detects your system's specifications including:</p>
    <ul>
        <li><strong>🎮 GPU:</strong> Graphics card model, memory, and driver version</li>
        <li><strong>⚡ CPU:</strong> Processor model, core count, and frequency</li>
        <li><strong>💾 Memory:</strong> Total, available, and used RAM with visual progress</li>
        <li><strong>🖥️ System:</strong> Platform, architecture, and Python version</li>
    </ul>
    <p><strong>Supported Platforms:</strong> Windows, macOS, and Linux systems</p>
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
st.markdown("""
<div class="footer">
    <p>🚀 Built with Streamlit • GPU Detector Pro</p>
</div>
""", unsafe_allow_html=True)
