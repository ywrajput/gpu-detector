#!/usr/bin/env python3
"""
Production AI Backend for GPU Benchmark Tool
Deploy this to your hosting platform (Heroku, Railway, etc.)
"""

import os
import json
from flask import Flask, request, jsonify, render_template_string
import openai

app = Flask(__name__)

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

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
                        <select id="gpuModel" required>
                            <option value="">Select your GPU</option>
                            <option value="RTX 4090">RTX 4090</option>
                            <option value="RTX 4080">RTX 4080</option>
                            <option value="RTX 4070">RTX 4070</option>
                            <option value="RTX 3090">RTX 3090</option>
                            <option value="RTX 3080">RTX 3080</option>
                            <option value="RTX 3070">RTX 3070</option>
                            <option value="RTX 3060">RTX 3060</option>
                            <option value="RX 7900 XTX">RX 7900 XTX</option>
                            <option value="RX 6900 XT">RX 6900 XT</option>
                            <option value="Arc A770">Arc A770</option>
                        </select>
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
                        <select id="useCase" required>
                            <option value="">Select use case</option>
                            <option value="4K Gaming">4K Gaming</option>
                            <option value="1440p Gaming">1440p Gaming</option>
                            <option value="1080p Gaming">1080p Gaming</option>
                            <option value="Content Creation">Content Creation</option>
                            <option value="Video Editing">Video Editing</option>
                            <option value="3D Rendering">3D Rendering</option>
                            <option value="Machine Learning">Machine Learning</option>
                        </select>
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
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key or api_key == "your-api-key-here":
            # Return demo response
            analysis = f"""DEMO ANALYSIS for {gpu_model}:

1. Overall Performance: {'Excellent' if temperature < 80 and utilization > 80 else 'Good' if temperature < 85 else 'Needs Attention'}

2. Temperature Analysis: {temperature}°C is {'optimal' if temperature < 75 else 'acceptable' if temperature < 85 else 'concerning - consider better cooling'}

3. Power Consumption: {power}W is {'efficient' if power < 300 else 'moderate' if power < 450 else 'high - monitor power supply'}

4. Recommendations:
   - Update GPU drivers for optimal performance
   - Monitor temperature during extended use
   - Consider undervolting for better efficiency
   - Ensure adequate case ventilation

Note: This is a demo response. Set your OpenAI API key for real AI analysis."""
            
            return jsonify({
                'success': True,
                'analysis': analysis,
                'gpu_model': gpu_model
            })
        
        # Create analysis prompt
        prompt = f"""
        Analyze this GPU performance data:
        - GPU Model: {gpu_model}
        - Temperature: {temperature}°C
        - Power Consumption: {power}W
        - Utilization: {utilization}%
        
        Provide a brief analysis with:
        1. Overall performance assessment
        2. Any potential issues
        3. Optimization recommendations
        
        Keep it concise and actionable.
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300
        )
        
        analysis = response.choices[0].message.content
        
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
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key or api_key == "your-api-key-here":
            # Return demo response
            recommendations = f"""DEMO UPGRADE RECOMMENDATIONS:

Current GPU: {current_gpu}
Use Case: {use_case}
Budget: ${budget}

Top 3 Recommendations:

1. RTX 4080 - $1,199
   Best value for 4K gaming with excellent performance per dollar
   Expected improvement: 40-60% over {current_gpu}

2. RTX 4070 Ti - $799
   Great 1440p performance with room for future upgrades
   Expected improvement: 25-35% over {current_gpu}

3. RTX 4090 - $1,599
   Ultimate performance for content creation and 4K gaming
   Expected improvement: 60-80% over {current_gpu}

Note: This is a demo response. Set your OpenAI API key for real AI recommendations."""
            
            return jsonify({
                'success': True,
                'recommendations': recommendations,
                'current_gpu': current_gpu,
                'budget': budget
            })
        
        # Create recommendation prompt
        prompt = f"""
        Recommend GPU upgrades for:
        - Current GPU: {current_gpu}
        - Use case: {use_case}
        - Budget: ${budget}
        
        Provide top 3 recommendations with:
        1. GPU model and price
        2. Performance improvement
        3. Why it's a good choice
        
        Format as a simple list.
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400
        )
        
        recommendations = response.choices[0].message.content
        
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
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key or api_key == "your-api-key-here":
        print("⚠️  No valid OpenAI API key found")
        print("   The server will start but AI features will show demo responses")
        print("   To enable real AI: export OPENAI_API_KEY='your-real-key'")
    else:
        print("✅ OpenAI API key found - AI features enabled")
    
    print("🚀 Starting Production AI Backend Server...")
    print("   Dashboard: http://localhost:5000")
    print("   API: http://localhost:5000/api/")
    
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
