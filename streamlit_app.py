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
    page_title="GPU Detector",
    page_icon="🖥️",
    layout="wide"
)

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
        "frequency": psutil.cpu_freq().current if psutil.cpu_freq() else "Unknown"
    }
    
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
    
    # Fix frequency display
    if cpu_info["frequency"] != "Unknown":
        cpu_info["frequency"] = f"{cpu_info['frequency']:.0f}"
    
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
st.title("🖥️ GPU Detector")
st.markdown("### Instantly detect your graphics card model, memory, and specifications")

# Add some spacing
st.markdown("---")

# Detection button
if st.button("🔍 Detect My Hardware", type="primary", use_container_width=True):
    with st.spinner("Detecting your hardware..."):
        try:
            # Get all system information
            system_info = get_system_info()
            gpu_info = get_gpu_info()
            cpu_info = get_cpu_info()
            memory_info = get_memory_info()
            
            # Display results in columns
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🖥️ GPU Information")
                if gpu_info["detected"] and gpu_info["gpus"]:
                    for i, gpu in enumerate(gpu_info["gpus"]):
                        st.write(f"**GPU {i+1}:** {gpu['name']}")
                        st.write(f"**Memory:** {gpu['memory_gb']} GB")
                        st.write(f"**Driver:** {gpu['driver_version']}")
                        st.write(f"**Type:** {gpu['type']}")
                        st.write("---")
                else:
                    st.error("❌ No GPU detected")
                    if gpu_info["error"]:
                        st.caption(f"Error: {gpu_info['error']}")
                
                st.subheader("💾 Memory Information")
                st.write(f"**Total:** {memory_info['total_gb']} GB")
                st.write(f"**Available:** {memory_info['available_gb']} GB")
                st.write(f"**Used:** {memory_info['used_gb']} GB ({memory_info['percent_used']}%)")
                
                # Memory progress bar
                st.progress(memory_info['percent_used'] / 100)
            
            with col2:
                st.subheader("🖥️ System Information")
                st.write(f"**Platform:** {system_info['platform']}")
                st.write(f"**Architecture:** {system_info['architecture']}")
                st.write(f"**Python:** {system_info['python_version']}")
                st.write(f"**Processor:** {system_info['processor']}")
                
                st.subheader("⚡ CPU Information")
                st.write(f"**Model:** {cpu_info['name']}")
                st.write(f"**Cores:** {cpu_info['cores']} ({cpu_info['physical_cores']} physical)")
                st.write(f"**Frequency:** {cpu_info['frequency']} MHz")
            
            # Success message
            st.success("✅ Hardware detection completed!")
            
        except Exception as e:
            st.error(f"❌ Error during detection: {str(e)}")

# Add some helpful information
st.markdown("---")
st.markdown("### ℹ️ About This Tool")
st.markdown("""
This tool detects your system's hardware specifications including:
- **GPU**: Graphics card model, memory, and driver version
- **CPU**: Processor model, core count, and frequency  
- **Memory**: Total, available, and used RAM
- **System**: Platform, architecture, and Python version

The detection works on Windows, macOS, and Linux systems.
""")

# Footer
st.markdown("---")
st.caption("Built with Streamlit • GPU Detector")
