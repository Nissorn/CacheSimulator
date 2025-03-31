import requests
import json
import os

class AIOptimizer:
    def __init__(self):
        # Default API key - should be replaced with user's key
        self.api_key = ""
        self.api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
        
    def set_api_key(self, api_key):
        """Set the Google AI Studio API key"""
        self.api_key = api_key
        
    def get_cache_recommendation(self, access_pattern, current_config):
        """Get cache configuration recommendations based on the access pattern
        
        Args:
            access_pattern (str): The memory access pattern (space-separated addresses)
            current_config (dict): Current cache configuration
            
        Returns:
            dict: Recommended cache configuration or error message
        """
        if not self.api_key:
            return {"error": "API key not set. Please set your Google AI Studio API key."}
        
        # Prepare the prompt for the AI
        prompt = self._prepare_prompt(access_pattern, current_config)
        
        try:
            # Make API request
            headers = {
                'Content-Type': 'application/json'
            }
            
            data = {
                "contents": [{
                    "parts":[{"text": prompt}]
                }]
            }
            
            url = f"{self.api_url}?key={self.api_key}"
            response = requests.post(url, headers=headers, data=json.dumps(data))
            
            if response.status_code == 200:
                result = response.json()
                # Extract the recommendation from the AI response
                recommendation = self._parse_ai_response(result)
                return recommendation
            else:
                return {"error": f"API request failed with status code {response.status_code}: {response.text}"}
                
        except Exception as e:
            return {"error": f"Error communicating with AI API: {str(e)}"}
    
    def _prepare_prompt(self, access_pattern, current_config):
        """Prepare the prompt for the AI"""
        addresses = access_pattern.split()
        
        prompt = f"""As a cache optimization expert, analyze this memory access pattern and recommend the optimal cache configuration.

Memory access pattern: {access_pattern}

Pattern analysis:
- Total addresses: {len(addresses)}
- Unique addresses: {len(set(addresses))}

Current cache configuration:
- Cache Size: {current_config.get('cache_size', 'Not specified')}
- Block Size: {current_config.get('block_size', 'Not specified')}
- Associativity: {current_config.get('associativity', 'Not specified')}
- Replacement Policy: {current_config.get('replacement_policy', 'Not specified')}

Based on this access pattern, what would be the optimal cache configuration to maximize hit rate? 
Provide recommendations for:
1. Cache Size (integer)
2. Block Size (integer)
3. Associativity (Direct, Set-Associative, or Fully-Associative)
4. Replacement Policy (LRU or FIFO)

Format your response as a JSON object with these exact keys: cache_size, block_size, associativity, replacement_policy
"""
        return prompt
    
    def _parse_ai_response(self, response):
        """Parse the AI response to extract the recommendation"""
        try:
            # Extract the text from the response
            if 'candidates' in response and len(response['candidates']) > 0:
                if 'content' in response['candidates'][0] and 'parts' in response['candidates'][0]['content']:
                    text = response['candidates'][0]['content']['parts'][0]['text']
                    
                    # Try to find and parse JSON in the response
                    import re
                    json_match = re.search(r'\{[\s\S]*\}', text)
                    if json_match:
                        json_str = json_match.group(0)
                        try:
                            recommendation = json.loads(json_str)
                            # Validate the recommendation format
                            required_keys = ['cache_size', 'block_size', 'associativity', 'replacement_policy']
                            if all(key in recommendation for key in required_keys):
                                # Convert string numbers to integers
                                if isinstance(recommendation['cache_size'], str) and recommendation['cache_size'].isdigit():
                                    recommendation['cache_size'] = int(recommendation['cache_size'])
                                if isinstance(recommendation['block_size'], str) and recommendation['block_size'].isdigit():
                                    recommendation['block_size'] = int(recommendation['block_size'])
                                return recommendation
                        except json.JSONDecodeError:
                            pass
            
            # If we couldn't parse JSON, return the raw text
            return {"raw_response": text if 'text' in locals() else "No text found in response"}
            
        except Exception as e:
            return {"error": f"Error parsing AI response: {str(e)}"}