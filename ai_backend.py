#!/usr/bin/env python3
"""
Simple AI Backend for GPU Benchmark Tool
Handles AI requests from the dashboard
"""

import os
import json
from flask import Flask, request, jsonify, render_template
import openai

app = Flask(__name__)

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

@app.route('/')
def index():
    """Serve the AI dashboard."""
    return render_template('ai_dashboard.html')

@app.route('/ai_dashboard.html')
def ai_dashboard():
    """Serve the AI dashboard directly."""
    return render_template('ai_dashboard.html')

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
        
        prompt = f"""You are an expert GPU hardware consultant with deep knowledge of graphics cards, performance characteristics, and real-world usage patterns.

**Task:** Provide a comprehensive GPU upgrade recommendation based on the following inputs:
- Current GPU: {current_gpu}
- Primary Use Case: {use_case}
- Budget: ${budget}

**Analysis Framework:**
1. **Current GPU Assessment:** Evaluate the current GPU's capabilities for the stated use case
2. **Performance Gap Analysis:** Identify specific limitations and bottlenecks
3. **Upgrade Options:** Present 2-3 viable upgrade paths within budget
4. **ROI Analysis:** Consider performance gains vs. cost
5. **Alternative Considerations:** Mention any trade-offs or alternatives

**Response Format:**
- **Current Status:** [Brief assessment of current GPU]
- **Recommended Upgrade:** [Primary recommendation with reasoning]
- **Alternative Options:** [1-2 other viable options]
- **Performance Impact:** [Expected improvements in specific metrics]
- **Budget Efficiency:** [Value proposition analysis]
- **Additional Notes:** [Any important considerations or warnings]

**Guidelines:**
- Be specific about performance improvements (e.g., "40% faster 4K gaming", "2x faster video rendering")
- Consider real-world factors like power consumption, cooling requirements, and compatibility
- Mention if the upgrade is worth it or if waiting for next-gen is better
- Keep response between 150-250 words
- Use technical accuracy but avoid jargon overload"""
        
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

@app.route('/api/ai-support', methods=['POST'])
def ai_support():
    """Handle AI support requests."""
    try:
        data = request.json
        email = data.get('email', '')
        subject = data.get('subject', '')
        message = data.get('message', '')
        
        prompt = f"""
        You are a GPU expert support agent. Respond to this support ticket:
        
        Subject: {subject}
        Message: {message}
        
        Provide a helpful response with:
        1. Acknowledgment of the issue
        2. Specific troubleshooting steps
        3. Additional resources if needed
        
        Keep it professional and actionable.
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300
        )
        
        support_response = response.choices[0].message.content
        
        return jsonify({
            'success': True,
            'response': support_response,
            'ticket_id': f"AI-{hash(message) % 10000}"
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/generate-content', methods=['POST'])
def generate_content():
    """Generate AI content."""
    try:
        data = request.json
        topic = data.get('topic', '')
        content_type = data.get('content_type', 'blog_post')
        audience = data.get('target_audience', 'gaming enthusiasts')
        
        prompt = f"""
        Create {content_type} content about: {topic}
        Target audience: {audience}
        
        Provide:
        1. A compelling title
        2. Brief outline
        3. Key points to cover
        
        Keep it structured and engaging.
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400
        )
        
        content = response.choices[0].message.content
        
        return jsonify({
            'success': True,
            'content': content,
            'topic': topic,
            'type': content_type
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
    
    print("🚀 Starting AI Backend Server...")
    print("   Dashboard: http://localhost:5001")
    print("   API: http://localhost:5001/api/")
    
    app.run(debug=True, host='0.0.0.0', port=5001)
