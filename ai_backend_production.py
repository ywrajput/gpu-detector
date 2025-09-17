#!/usr/bin/env python3
"""
Production AI Backend for GPU Benchmark Tool
Deploy this to your hosting platform (Heroku, Railway, etc.)
"""

import os
import json
from flask import Flask, request, jsonify, render_template_string
import anthropic

app = Flask(__name__)

# Initialize Anthropic client
try:
    api_key = os.getenv('ANTHROPIC_API_KEY')
    print(f"API Key found: {api_key[:10] if api_key else 'None'}...")
    if api_key and api_key != "your-api-key-here":
        print("Initializing Anthropic client...")
        client = anthropic.Anthropic(api_key=api_key)
        print("✅ Anthropic client initialized successfully")
    else:
        print("❌ No valid API key found")
        client = None
except Exception as e:
    print(f"❌ Failed to initialize Anthropic client: {e}")
    print(f"Error type: {type(e).__name__}")
    client = None

# AI Dashboard HTML (embedded for production)
AI_DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI-Powered GPU Analysis Dashboard</title>
    
    <!-- Google Tag Manager -->
    <script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
    new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
    j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
    'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
    })(window,document,'script','dataLayer','GTM-PNX9XSKX');</script>
    <!-- End Google Tag Manager -->
    
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        .header {
            text-align: center;
            margin-bottom: 3rem;
            color: white;
        }
        
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 1rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .header p {
            font-size: 1.2rem;
            opacity: 0.9;
        }
        
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 2rem;
            margin-bottom: 3rem;
        }
        
        .dashboard-card {
            background: white;
            border-radius: 15px;
            padding: 2rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .dashboard-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.3);
        }
        
        .card-header {
            display: flex;
            align-items: center;
            margin-bottom: 1.5rem;
        }
        
        .card-icon {
            font-size: 2rem;
            margin-right: 1rem;
            color: #667eea;
        }
        
        .card-title {
            font-size: 1.5rem;
            font-weight: 600;
            color: #333;
        }
        
        .form-group {
            margin-bottom: 1.5rem;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 500;
            color: #555;
        }
        
        .form-group input,
        .form-group select,
        .form-group textarea {
            width: 100%;
            padding: 0.8rem;
            border: 2px solid #e1e5e9;
            border-radius: 8px;
            font-size: 1rem;
            transition: border-color 0.3s ease;
        }
        
        .form-group input:focus,
        .form-group select:focus,
        .form-group textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 1rem 2rem;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            width: 100%;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        .result-area {
            margin-top: 1.5rem;
            padding: 1.5rem;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #667eea;
            display: none;
        }
        
        .result-area.show {
            display: block;
        }
        
        .loading {
            text-align: center;
            padding: 2rem;
            color: #667eea;
        }
        
        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
            margin: 0 auto 1rem;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <!-- Google Tag Manager (noscript) -->
    <noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-PNX9XSKX"
    height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
    <!-- End Google Tag Manager -->
    
    <div class="container">
        <div class="header">
            <h1>🤖 AI-Powered GPU Analysis</h1>
            <p>Leverage artificial intelligence to optimize your GPU performance and get personalized recommendations</p>
        </div>
        
        <div class="dashboard-grid">
            <!-- GPU Analysis Card -->
            <div class="dashboard-card">
                <div class="card-header">
                    <div class="card-icon">📊</div>
                    <div class="card-title">GPU Performance Analysis</div>
                </div>
                
                <form id="gpuAnalysisForm">
                    <div class="form-group">
                        <label for="gpuModel">GPU Model</label>
                        <input type="text" id="gpuModel" placeholder="e.g., RTX 4090, RX 7900 XTX, RTX 3080" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="temperature">Temperature (°C)</label>
                        <input type="number" id="temperature" placeholder="e.g., 75" min="0" max="100">
                    </div>
                    
                    <div class="form-group">
                        <label for="powerConsumption">Power Consumption (W)</label>
                        <input type="number" id="powerConsumption" placeholder="e.g., 450" min="0" max="1000">
                    </div>
                    
                    <div class="form-group">
                        <label for="utilization">GPU Utilization (%)</label>
                        <input type="number" id="utilization" placeholder="e.g., 95" min="0" max="100">
                    </div>
                    
                    <button type="submit" class="btn">Analyze Performance</button>
                </form>
                
                <div id="gpuAnalysisResult" class="result-area">
                    <h3>Analysis Results</h3>
                    <div id="gpuAnalysisContent"></div>
                </div>
            </div>
            
            <!-- Upgrade Recommendations Card -->
            <div class="dashboard-card">
                <div class="card-header">
                    <div class="card-icon">🚀</div>
                    <div class="card-title">Upgrade Recommendations</div>
                </div>
                
                <form id="upgradeForm">
                    <div class="form-group">
                        <label for="currentGPU">Current GPU</label>
                        <input type="text" id="currentGPU" placeholder="e.g., RTX 3080" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="useCase">Primary Use Case</label>
                        <input type="text" id="useCase" placeholder="e.g., 4K Gaming, Video Editing, 3D Rendering, Machine Learning" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="budget">Budget ($)</label>
                        <input type="number" id="budget" placeholder="e.g., 1500" min="100" max="5000" required>
                    </div>
                    
                    <button type="submit" class="btn">Get Recommendations</button>
                </form>
                
                <div id="upgradeResult" class="result-area">
                    <h3>Upgrade Recommendations</h3>
                    <div id="upgradeContent"></div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Form submission handlers
        document.getElementById('gpuAnalysisForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const resultDiv = document.getElementById('gpuAnalysisResult');
            const contentDiv = document.getElementById('gpuAnalysisContent');
            
            resultDiv.classList.add('show');
            contentDiv.innerHTML = '<div class="loading"><div class="spinner"></div>Analyzing GPU performance...</div>';
            
            // Get form data
            const formData = {
                gpu_model: document.getElementById('gpuModel').value,
                temperature: document.getElementById('temperature').value,
                power_consumption: document.getElementById('powerConsumption').value,
                utilization: document.getElementById('utilization').value
            };
            
            try {
                const response = await fetch('/api/analyze-gpu', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(formData)
                });
                
                const result = await response.json();
                
                if (result.success) {
                    contentDiv.innerHTML = `
                        <h4>AI Performance Analysis</h4>
                        <div style="white-space: pre-line;">${result.analysis}</div>
                    `;
                } else {
                    contentDiv.innerHTML = `
                        <h4>Error</h4>
                        <p>Failed to analyze GPU: ${result.error}</p>
                    `;
                }
            } catch (error) {
                contentDiv.innerHTML = `
                    <h4>Error</h4>
                    <p>Failed to connect to AI service: ${error.message}</p>
                `;
            }
        });
        
        document.getElementById('upgradeForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const resultDiv = document.getElementById('upgradeResult');
            const contentDiv = document.getElementById('upgradeContent');
            
            resultDiv.classList.add('show');
            contentDiv.innerHTML = '<div class="loading"><div class="spinner"></div>Generating upgrade recommendations...</div>';
            
            // Get form data
            const formData = {
                current_gpu: document.getElementById('currentGPU').value,
                use_case: document.getElementById('useCase').value,
                budget: document.getElementById('budget').value
            };
            
            try {
                const response = await fetch('/api/recommend-upgrade', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(formData)
                });
                
                const result = await response.json();
                
                if (result.success) {
                    contentDiv.innerHTML = `
                        <h4>AI Upgrade Recommendations</h4>
                        <div style="white-space: pre-line;">${result.recommendations}</div>
                    `;
                } else {
                    contentDiv.innerHTML = `
                        <h4>Error</h4>
                        <p>Failed to get recommendations: ${result.error}</p>
                    `;
                }
            } catch (error) {
                contentDiv.innerHTML = `
                    <h4>Error</h4>
                    <p>Failed to connect to AI service: ${error.message}</p>
                `;
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Serve the AI dashboard."""
    return render_template_string(AI_DASHBOARD_HTML)

@app.route('/api/analyze-gpu', methods=['POST'])
def analyze_gpu():
    """Analyze GPU performance data."""
    try:
        data = request.json
        gpu_model = data.get('gpu_model', 'Unknown')
        temperature = data.get('temperature', 0)
        power = data.get('power_consumption', 0)
        utilization = data.get('utilization', 0)
        
        # Check if we have a valid API key
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key or api_key == "your-api-key-here":
            return jsonify({
                'success': False,
                'error': 'AI analysis service is currently unavailable. Please try again later or contact support if the issue persists.'
            }), 503
        
        # Create analysis prompt
        prompt = f"""You are a GPU performance analyst with expertise in hardware diagnostics, thermal management, and performance optimization. You analyze real-time GPU telemetry data to provide actionable insights.

**Task:** Analyze GPU performance based on the following real-time metrics:
- GPU Model: {gpu_model}
- Current Temperature: {temperature}°C
- Power Consumption: {power}W
- GPU Utilization: {utilization}%

**Analysis Framework:**
1. **Thermal Analysis:** Assess temperature relative to GPU's thermal limits and cooling efficiency
2. **Power Analysis:** Evaluate power consumption patterns and efficiency
3. **Performance Analysis:** Analyze utilization patterns and potential bottlenecks
4. **Health Assessment:** Identify any concerning patterns or issues
5. **Optimization Recommendations:** Suggest specific improvements

**Response Format:**
- **Performance Status:** [Overall assessment - Excellent/Good/Concerning/Critical]
- **Thermal Analysis:** [Temperature assessment and cooling efficiency]
- **Power Efficiency:** [Power consumption analysis and efficiency rating]
- **Utilization Insights:** [GPU usage patterns and bottleneck identification]
- **Health Indicators:** [Any warning signs or concerning patterns]
- **Recommendations:** [Specific actionable improvements]

**Guidelines:**
- Reference the specific GPU model's specifications (TDP, thermal limits, expected performance)
- Provide specific temperature thresholds (e.g., "85°C is 5°C above optimal")
- Calculate power efficiency ratios where relevant
- Identify if utilization patterns indicate CPU bottleneck, memory bottleneck, or other issues
- Give specific, actionable recommendations (e.g., "Increase fan speed", "Check thermal paste")
- Keep response between 120-200 words
- Use technical precision but remain accessible"""
        
        response = client.completions.create(
            model="claude-3-haiku-20240307",
            max_tokens_to_sample=300,
            prompt=f"\n\nHuman: {prompt}\n\nAssistant:"
        )
        
        analysis = response.completion
        
        return jsonify({
            'success': True,
            'analysis': analysis,
            'gpu_model': gpu_model
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/recommend-upgrade', methods=['POST'])
def recommend_upgrade():
    """Get GPU upgrade recommendations."""
    try:
        data = request.json
        current_gpu = data.get('current_gpu', 'Unknown')
        use_case = data.get('use_case', 'Gaming')
        budget = data.get('budget', 1000)
        
        # Check if we have a valid API key
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key or api_key == "your-api-key-here":
            return jsonify({
                'success': False,
                'error': 'AI recommendation service is currently unavailable. Please try again later or contact support if the issue persists.'
            }), 503
        
        # Create recommendation prompt
        prompt = f"""You are an expert GPU hardware consultant with deep knowledge of graphics cards, performance characteristics, and real-world usage patterns.

**Task:** Provide intelligent GPU advice based on the following inputs:
- Current GPU: {current_gpu}
- Primary Use Case: {use_case}
- Budget: ${budget}

**Analysis Framework:**
1. **Current GPU Assessment:** Evaluate the current GPU's capabilities for the stated use case
2. **Performance Gap Analysis:** Identify if there are actual limitations or if the current GPU is already sufficient
3. **Upgrade Necessity:** Determine if an upgrade is actually needed or if the current GPU is already strong enough
4. **ROI Analysis:** Consider performance gains vs. cost (only if upgrade is beneficial)
5. **Alternative Considerations:** Mention any trade-offs or alternatives

**Response Format:**
- **Current Status:** [Brief assessment of current GPU for the use case]
- **Recommendation:** [Either "No upgrade needed" OR "Recommended upgrade" with reasoning]
- **Alternative Options:** [Only if upgrade is recommended - 1-2 other viable options]
- **Performance Impact:** [Expected improvements OR explanation of why current GPU is sufficient]
- **Budget Efficiency:** [Value proposition analysis OR cost savings from not upgrading]
- **Additional Notes:** [Any important considerations or warnings]

**Guidelines:**
- If the current GPU is already powerful enough for the use case, RECOMMEND NOT UPGRADING
- Only suggest upgrades if there's a genuine performance benefit
- Be specific about performance improvements (e.g., "40% faster 4K gaming", "2x faster video rendering")
- Consider real-world factors like power consumption, cooling requirements, and compatibility
- Mention if the upgrade is worth it or if waiting for next-gen is better
- Keep response between 150-250 words
- Use technical accuracy but avoid jargon overload"""
        
        response = client.completions.create(
            model="claude-3-haiku-20240307",
            max_tokens_to_sample=400,
            prompt=f"\n\nHuman: {prompt}\n\nAssistant:"
        )
        
        recommendations = response.completion
        
        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'current_gpu': current_gpu,
            'budget': budget
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    # Check if API key is set
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key or api_key == "your-api-key-here":
        print("⚠️  No valid Anthropic API key found")
        print("   The server will start but AI features will be unavailable")
        print("   To enable real AI: export ANTHROPIC_API_KEY='your-real-key'")
    else:
        print("✅ Anthropic API key found - AI features enabled")
    
    print("🚀 Starting Production AI Backend Server...")
    print("   Dashboard: http://localhost:5000")
    print("   API: http://localhost:5000/api/")
    
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
