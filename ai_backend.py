#!/usr/bin/env python3
"""
Simple AI Backend for GPU Benchmark Tool
Handles AI requests from the dashboard
"""

import os
import json
from flask import Flask, request, jsonify, render_template
import anthropic

app = Flask(__name__)

# Initialize Anthropic client
client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

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
        
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )
        
        analysis = response.content[0].text
        
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
        
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=400,
            messages=[{"role": "user", "content": prompt}]
        )
        
        recommendations = response.content[0].text
        
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
