#!/usr/bin/env python3
"""
AI-Powered Content Generation System
Automatically generates blog posts, product descriptions, and educational content about GPUs.
"""

import openai
import json
import os
from datetime import datetime
from typing import List, Dict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GPUContentGenerator:
    def __init__(self, openai_api_key: str):
        """Initialize the AI content generator."""
        self.client = openai.OpenAI(api_key=openai_api_key)
        self.content_dir = "generated_content"
        os.makedirs(self.content_dir, exist_ok=True)
        
    def generate_blog_post(self, topic: str, target_audience: str = "gpu enthusiasts") -> Dict:
        """Generate a comprehensive blog post about GPU topics."""
        
        prompt = f"""
        Write a comprehensive blog post about: {topic}
        
        Target audience: {target_audience}
        
        Requirements:
        - 800-1500 words
        - Include technical details but keep it accessible
        - Add practical examples and use cases
        - Include relevant GPU models and benchmarks
        - Structure with clear headings and subheadings
        - End with actionable takeaways
        
        Format as JSON:
        {{
            "title": "SEO-optimized title",
            "meta_description": "Meta description for SEO",
            "content": "Full blog post content in HTML format",
            "tags": ["tag1", "tag2", "tag3"],
            "estimated_read_time": "X minutes"
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            
            content = json.loads(response.choices[0].message.content)
            
            # Save to file
            filename = f"{topic.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.html"
            filepath = os.path.join(self.content_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(self._format_blog_html(content))
            
            logger.info(f"Generated blog post: {filepath}")
            return content
            
        except Exception as e:
            logger.error(f"Error generating blog post: {e}")
            return {}
    
    def generate_gpu_comparison(self, gpu1: str, gpu2: str) -> Dict:
        """Generate detailed GPU comparison content."""
        
        prompt = f"""
        Create a detailed comparison between {gpu1} and {gpu2}:
        
        Include:
        - Specifications comparison
        - Performance benchmarks
        - Price-to-performance ratio
        - Use case recommendations
        - Pros and cons of each
        - Which one to choose for different scenarios
        
        Format as JSON with structured data for easy integration.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"Error generating GPU comparison: {e}")
            return {}
    
    def generate_troubleshooting_guide(self, issue: str) -> Dict:
        """Generate step-by-step troubleshooting guides."""
        
        prompt = f"""
        Create a comprehensive troubleshooting guide for: {issue}
        
        Include:
        - Clear problem identification steps
        - Step-by-step solutions (beginner to advanced)
        - Common causes and prevention tips
        - When to seek professional help
        - Related resources and tools
        
        Make it actionable and easy to follow.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.6
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"Error generating troubleshooting guide: {e}")
            return {}
    
    def generate_seo_content_plan(self, keywords: List[str]) -> Dict:
        """Generate a content plan based on SEO keywords."""
        
        prompt = f"""
        Create a content strategy for a GPU benchmarking website targeting these keywords:
        {', '.join(keywords)}
        
        Generate:
        - 10 blog post ideas with titles and brief descriptions
        - Content calendar for 3 months
        - Internal linking strategy
        - Content clusters and pillar pages
        
        Focus on providing value to GPU enthusiasts, gamers, and professionals.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"Error generating content plan: {e}")
            return {}
    
    def _format_blog_html(self, content: Dict) -> str:
        """Format blog content as HTML."""
        
        html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{content.get('title', 'GPU Blog Post')}</title>
    <meta name="description" content="{content.get('meta_description', '')}">
    <meta name="keywords" content="{', '.join(content.get('tags', []))}">
    
    <!-- Include your existing CSS -->
    <link rel="stylesheet" href="../static/css/style.css">
</head>
<body>
    <article class="blog-post">
        <header>
            <h1>{content.get('title', '')}</h1>
            <div class="post-meta">
                <span>Estimated read time: {content.get('estimated_read_time', '5 minutes')}</span>
                <span>Tags: {', '.join(content.get('tags', []))}</span>
            </div>
        </header>
        
        <div class="post-content">
            {content.get('content', '')}
        </div>
        
        <footer>
            <p>Generated by AI Content Generator - GPU Benchmark Tool</p>
        </footer>
    </article>
</body>
</html>
        """
        
        return html_template

# Example usage
if __name__ == "__main__":
    # Initialize the content generator
    content_gen = GPUContentGenerator("your-openai-api-key-here")
    
    # Generate a blog post
    blog_post = content_gen.generate_blog_post(
        topic="RTX 4090 vs RTX 4080: Which GPU Should You Choose?",
        target_audience="gaming enthusiasts"
    )
    
    print(f"Generated blog post: {blog_post.get('title', 'No title')}")
    
    # Generate GPU comparison
    comparison = content_gen.generate_gpu_comparison("RTX 4090", "RTX 4080")
    print(f"Generated comparison: {comparison}")
    
    # Generate content plan
    keywords = ["GPU benchmark", "RTX 4090 review", "GPU comparison", "graphics card performance"]
    content_plan = content_gen.generate_seo_content_plan(keywords)
    print(f"Generated content plan: {content_plan}")
