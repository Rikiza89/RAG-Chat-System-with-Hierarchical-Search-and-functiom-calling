"""
Universal Auto-Detection System
Automatically detects which function to call based on question content
Works for ALL functions - existing and future ones!
"""

import re
from typing import List, Dict, Any, Optional

class UniversalAutoDetector:
    """
    Intelligent function detection based on:
    1. Keywords in function names and docstrings
    2. Parameter patterns in questions
    3. File type detection
    4. Context analysis
    """
    
    def __init__(self, function_manager):
        self.function_manager = function_manager
        self.detection_rules = self._build_detection_rules()
    
    def _build_detection_rules(self):
        """
        Automatically build detection rules from all available functions
        This is generated dynamically - no hardcoding!
        """
        rules = []
        
        for func_name, func_data in self.function_manager.function_registry.items():
            doc = func_data.get('doc', '').lower()
            params = func_data.get('params', [])
            
            # Extract keywords from function name
            name_parts = func_name.lower().replace('/', ' ').replace('_', ' ').split()
            
            # Extract keywords from docstring
            doc_keywords = set(re.findall(r'\b\w{4,}\b', doc))
            
            rule = {
                'function': func_name,
                'name_keywords': name_parts,
                'doc_keywords': doc_keywords,
                'params': params,
                'triggers': self._generate_triggers(func_name, doc, params)
            }
            
            rules.append(rule)
        
        return rules
    
    def _generate_triggers(self, func_name, doc, params):
        """
        Generate automatic triggers based on function metadata
        """
        triggers = []
        
        # Trigger patterns based on function name
        if 'add' in func_name:
            triggers.append({'pattern': r'(\d+)\s*(?:\+|plus|add)\s*(\d+)', 'type': 'math'})
        if 'multiply' in func_name:
            triggers.append({'pattern': r'(\d+)\s*(?:\*|×|times|multiply)\s*(\d+)', 'type': 'math'})
        if 'subtract' in func_name:
            triggers.append({'pattern': r'(\d+)\s*(?:-|minus|subtract)\s*(\d+)', 'type': 'math'})
        
        # Excel detection
        if 'excel' in func_name or 'xlsx' in doc:
            triggers.append({'pattern': r'\.xlsx?', 'type': 'file_extension'})
            triggers.append({'pattern': r'\b(?:spreadsheet|excel|workbook)\b', 'type': 'keyword'})
        
        # HTML detection
        if 'html' in func_name:
            triggers.append({'pattern': r'\.html?', 'type': 'file_extension'})
            triggers.append({'pattern': r'\b(?:webpage|website|html)\b', 'type': 'keyword'})
        
        # PowerPoint detection
        if 'powerpoint' in func_name or 'pptx' in doc:
            triggers.append({'pattern': r'\.pptx?', 'type': 'file_extension'})
            triggers.append({'pattern': r'\b(?:presentation|slides|powerpoint)\b', 'type': 'keyword'})
        
        # Text operations
        if 'summarize' in func_name:
            triggers.append({'pattern': r'\b(?:summarize|summary|brief)\b', 'type': 'keyword'})
        if 'translate' in func_name:
            triggers.append({'pattern': r'\b(?:translate|translation)\b', 'type': 'keyword'})
        
        # Workflow/planning
        if 'workflow' in func_name or 'orchestrat' in func_name:
            triggers.append({'pattern': r'\b(?:plan|workflow|schedule|pipeline)\b', 'type': 'keyword'})
        
        # Decision/choice
        if 'decision' in func_name or 'choose' in func_name:
            triggers.append({'pattern': r'\b(?:choose|decide|select|compare|which)\b', 'type': 'keyword'})
        
        # Optimization
        if 'optimiz' in func_name or 'solver' in func_name:
            triggers.append({'pattern': r'\b(?:optimize|best|maximize|minimize)\b', 'type': 'keyword'})
        
        return triggers
    
    def detect(self, question: str) -> List[Dict[str, Any]]:
        """
        Detect which functions match the question
        Returns list of {function, confidence, params}
        """
        question_lower = question.lower()
        candidates = []
        
        for rule in self.detection_rules:
            score = 0
            detected_params = {}
            
            # Check triggers
            for trigger in rule['triggers']:
                pattern = trigger['pattern']
                match = re.search(pattern, question_lower, re.IGNORECASE)
                
                if match:
                    score += 10  # Trigger match
                    
                    # Extract parameters from pattern
                    if trigger['type'] == 'math' and match.groups():
                        detected_params = {
                            'a': int(match.group(1)),
                            'b': int(match.group(2))
                        }
            
            # Check name keywords
            for keyword in rule['name_keywords']:
                if keyword in question_lower:
                    score += 5
            
            # Check doc keywords
            for keyword in rule['doc_keywords']:
                if keyword in question_lower:
                    score += 2
            
            # Boost score for exact function type mention
            if rule['function'].split('/')[0] in question_lower:
                score += 15
            
            if score > 0:
                candidates.append({
                    'function': rule['function'],
                    'confidence': min(score, 100),
                    'detected_params': detected_params,
                    'rule': rule
                })
        
        # Sort by confidence
        candidates.sort(key=lambda x: x['confidence'], reverse=True)
        
        return candidates
    
    def auto_execute(self, question: str, threshold: int = 20) -> List[Dict[str, Any]]:
        """
        Auto-detect and execute functions above confidence threshold
        
        Args:
            question: User's question
            threshold: Minimum confidence to execute (0-100)
        
        Returns:
            List of execution results
        """
        candidates = self.detect(question)
        results = []
        
        for candidate in candidates:
            if candidate['confidence'] >= threshold:
                func_name = candidate['function']
                params = candidate['detected_params']
                
                # Execute function
                result = self.function_manager.execute_function(
                    func_name,
                    kwargs=params
                )
                
                results.append({
                    'function': func_name,
                    'confidence': candidate['confidence'],
                    'params': params,
                    'result': result
                })
        
        return results
    
    def suggest_functions(self, question: str, top_n: int = 3) -> List[Dict[str, Any]]:
        """
        Suggest which functions might be relevant (without executing)
        """
        candidates = self.detect(question)
        
        suggestions = []
        for candidate in candidates[:top_n]:
            func_data = self.function_manager.function_registry[candidate['function']]
            
            suggestions.append({
                'function': candidate['function'],
                'confidence': candidate['confidence'],
                'description': func_data['doc'],
                'signature': func_data['signature'],
                'suggested_use': self._format_suggestion(candidate)
            })
        
        return suggestions
    
    def _format_suggestion(self, candidate):
        """Format a usage suggestion"""
        func = candidate['function']
        params = candidate['detected_params']
        
        if params:
            param_str = ' '.join(f'{k}={v}' for k, v in params.items())
            return f"<run:{func} {param_str}>"
        else:
            return f"<run:{func} ...>"


# Integration with app.py

def enhanced_process_answer_with_functions(answer_text, question, function_manager):
    """
    Enhanced version with universal auto-detection
    Drop-in replacement for process_answer_with_functions
    """
    if not function_manager:
        return answer_text, []
    
    # Initialize auto-detector
    detector = UniversalAutoDetector(function_manager)
    
    all_results = []
    
    # Strategy 1: Explicit tags (existing)
    explicit = function_manager.parse_and_execute_from_text(answer_text)
    all_results.extend(explicit)
    
    # Strategy 2: Universal auto-detection (NEW!)
    if question:
        auto_detected = detector.auto_execute(question, threshold=20)
        
        # Convert to standard format
        for detection in auto_detected:
            if detection['result']['status'] == 'success':
                all_results.append({
                    'function': detection['function'],
                    'parsed_kwargs': detection['params'],
                    'result': detection['result'],
                    'trigger': 'auto_detected',
                    'confidence': detection['confidence']
                })
    
    # Build output
    processed_text = answer_text
    function_outputs = []
    
    if not explicit and auto_detected:
        processed_text += "\n\n---\n**🤖 Auto-Detected Functions:**\n"
    
    for result in all_results:
        if result['result']['status'] == 'success':
            func_name = result['function']
            result_value = result['result']['result']
            trigger = result.get('trigger', 'explicit')
            confidence = result.get('confidence', 100)
            
            if trigger == 'auto_detected':
                args_str = ', '.join(f"{k}={v}" for k, v in result['parsed_kwargs'].items())
                processed_text += f"\n`{func_name}({args_str})` = **{result_value}** ✅ (confidence: {confidence}%)"
            
            function_outputs.append({
                "function": func_name,
                "status": "success",
                "result": result_value,
                "args": result.get('parsed_kwargs', {}),
                "trigger": trigger,
                "confidence": confidence
            })
    
    return processed_text, function_outputs


def get_function_suggestions(question, function_manager):
    """
    Get function suggestions without executing
    Useful for UI hints
    """
    detector = UniversalAutoDetector(function_manager)
    return detector.suggest_functions(question, top_n=3)
