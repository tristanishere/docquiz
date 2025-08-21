import openai
import os
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

class AIService:
    def __init__(self):
        # Initialize OpenAI client
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            openai.api_key = api_key
            self.use_mock = False
        else:
            print("Warning: OPENAI_API_KEY not found. Using mock responses.")
            self.use_mock = True
    
    def generate_summary(self, content: List[str], summary_type: str) -> str:
        """Generate summary from document content"""
        if self.use_mock:
            return self._generate_mock_summary(content, summary_type)
        
        try:
            # Combine all content
            combined_content = "\n\n".join(content)
            
            # Determine summary length based on type
            length_map = {
                "short": "2-3 sentences",
                "medium": "4-6 sentences", 
                "long": "8-10 sentences"
            }
            
            prompt = f"""
            Please provide a {summary_type} summary of the following document content in {length_map[summary_type]}:
            
            {combined_content[:4000]}  # Limit content length for API
            
            Summary:
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that creates concise, accurate summaries of documents."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error generating summary: {e}")
            return self._generate_mock_summary(content, summary_type)
    
    def generate_quiz(self, content: List[str], question_count: int) -> List[Dict[str, Any]]:
        """Generate quiz questions from document content"""
        if self.use_mock:
            return self._generate_mock_quiz(content, question_count)
        
        try:
            # Combine all content
            combined_content = "\n\n".join(content)
            
            prompt = f"""
            Based on the following document content, generate {question_count} multiple choice quiz questions.
            Each question should have 4 options (A, B, C, D) with only one correct answer.
            
            Document content:
            {combined_content[:4000]}
            
            Please format the response as a JSON array with the following structure:
            [
                {{
                    "question": "Question text here?",
                    "options": {{
                        "A": "Option A",
                        "B": "Option B", 
                        "C": "Option C",
                        "D": "Option D"
                    }},
                    "correct_answer": "A",
                    "explanation": "Brief explanation of why this is correct"
                }}
            ]
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that creates educational quiz questions based on document content."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.3
            )
            
            # Parse the response as JSON
            import json
            try:
                quiz_data = json.loads(response.choices[0].message.content.strip())
                return quiz_data
            except json.JSONDecodeError:
                print("Error parsing quiz JSON response")
                return self._generate_mock_quiz(content, question_count)
            
        except Exception as e:
            print(f"Error generating quiz: {e}")
            return self._generate_mock_quiz(content, question_count)
    
    def _generate_mock_summary(self, content: List[str], summary_type: str) -> str:
        """Generate a mock summary when AI service is unavailable"""
        combined_content = " ".join(content)
        words = combined_content.split()[:100]  # Take first 100 words
        
        if summary_type == "short":
            return f"This document covers topics related to {' '.join(words[:20])}."
        elif summary_type == "medium":
            return f"This document discusses {' '.join(words[:40])}. It provides comprehensive information on these subjects and includes relevant details for understanding the material."
        else:  # long
            return f"This comprehensive document covers {' '.join(words[:60])}. The material is well-structured and provides detailed explanations of key concepts, making it suitable for in-depth study and reference purposes."
    
    def _generate_mock_quiz(self, content: List[str], question_count: int) -> List[Dict[str, Any]]:
        """Generate mock quiz questions when AI service is unavailable"""
        questions = []
        
        for i in range(question_count):
            question = {
                "question": f"Sample question {i+1} about the document content?",
                "options": {
                    "A": f"Option A for question {i+1}",
                    "B": f"Option B for question {i+1}",
                    "C": f"Option C for question {i+1}",
                    "D": f"Option D for question {i+1}"
                },
                "correct_answer": "A",
                "explanation": f"This is the correct answer for question {i+1} based on the document content."
            }
            questions.append(question)
        
        return questions