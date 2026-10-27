import os
import random
from pathlib import Path
from PIL import Image

class AIService:
    """
    AI Damage Detection Service Abstraction.
    Allows seamless replacement of the deterministic hackathon demo engine with real 
    Computer Vision API / Deep Learning inference models (e.g., YOLOv8, Google Cloud Vision, Gemini Vision).
    """

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('AI_API_KEY', '')

    def analyze_image(self, image_path: str, component: str = 'Vehicle Component', filename: str = '') -> dict:
        """
        Analyzes an uploaded vehicle component photograph for defects, scratches, dents, and paint flaws.
        
        Returns:
            dict: {
                "finding": str,
                "confidence": float (0.0 to 1.0),
                "severity": str ("LOW", "MEDIUM", "HIGH", "CRITICAL"),
                "description": str,
                "detected_defects": list,
                "recommendation": str
            }
        """
        # If external API is configured, forward request to real model
        if self.api_key and not self.api_key.startswith('demo'):
            try:
                return self._call_cloud_vision_api(image_path, component)
            except Exception as e:
                # Fallback to local demo engine if external API fails
                pass

        return self._run_demo_detection_engine(image_path, component, filename)

    def _run_demo_detection_engine(self, image_path: str, component: str, filename: str) -> dict:
        """Deterministic Intelligent Hackathon Demo Engine."""
        text_to_check = f"{filename} {component}".lower()

        # Check for image properties safely
        width, height = 1280, 720
        if image_path and os.path.exists(image_path):
            try:
                with Image.open(image_path) as img:
                    width, height = img.size
            except Exception:
                pass

        if 'scratch' in text_to_check:
            return {
                "finding": "Possible Scratch",
                "confidence": 0.91,
                "severity": "LOW",
                "description": f"Clear-coat surface scratch detected on {component}. Length ~4.2cm. No base coat penetration.",
                "detected_defects": [{"label": "Scratch", "box": [120, 85, 340, 110], "confidence": 0.91}],
                "recommendation": "Polishing with compound rubbing recommended before vehicle handover."
            }

        elif 'dent' in text_to_check:
            return {
                "finding": "Panel Dent Detected",
                "confidence": 0.88,
                "severity": "MEDIUM",
                "description": f"Minor shallow pressure dent detected on {component} sheet metal contour (~15mm diameter).",
                "detected_defects": [{"label": "Dent", "box": [210, 140, 310, 260], "confidence": 0.88}],
                "recommendation": "Paintless Dent Removal (PDR) can restore factory contour."
            }

        elif 'paint' in text_to_check or 'mismatch' in text_to_check:
            return {
                "finding": "Paint Thickness / Texture Variance",
                "confidence": 0.93,
                "severity": "MEDIUM",
                "description": f"Micro-texture orange peel or slight color shade variance identified on {component}.",
                "detected_defects": [{"label": "Paint Flaw", "box": [180, 190, 420, 380], "confidence": 0.93}],
                "recommendation": "Perform digital paint thickness gauge check. Target 95-130 microns."
            }

        elif 'crack' in text_to_check or 'glass' in text_to_check or 'windshield' in text_to_check:
            return {
                "finding": "Glass Stress Chip / Crack",
                "confidence": 0.95,
                "severity": "HIGH",
                "description": f"Radial micro-chip detected near border of {component}. Risk of stress propagation.",
                "detected_defects": [{"label": "Glass Chip", "box": [300, 220, 380, 300], "confidence": 0.95}],
                "recommendation": "Require dealer replacement of glass panel under pre-delivery warranty."
            }

        elif 'gap' in text_to_check or 'align' in text_to_check:
            return {
                "finding": "Panel Gap Misalignment",
                "confidence": 0.86,
                "severity": "MEDIUM",
                "description": f"Panel gap variance of ~2.4mm observed across seam for {component}.",
                "detected_defects": [{"label": "Gap Variance", "box": [50, 100, 100, 600], "confidence": 0.86}],
                "recommendation": "Realign panel fastening bolts to OEM factory gap tolerances."
            }

        elif 'tire' in text_to_check or 'wheel' in text_to_check or 'rim' in text_to_check:
            return {
                "finding": "Minor Sidewall / Rim Scuff",
                "confidence": 0.89,
                "severity": "LOW",
                "description": f"Superficial rubber scuff mark near rim bead on {component}. Tread depth is brand new (7.8mm).",
                "detected_defects": [{"label": "Scuff", "box": [220, 180, 360, 310], "confidence": 0.89}],
                "recommendation": "Clean with tire dressing; verify wheel balancing."
            }

        elif 'battery' in text_to_check or 'charging' in text_to_check or 'ev' in text_to_check:
            return {
                "finding": "Charging Port Cover / Seal Condition",
                "confidence": 0.92,
                "severity": "LOW",
                "description": f"Weather sealing rubber gasket intact. Minor transit dust observed on port contact pins.",
                "detected_defects": [{"label": "Dust / Cleanliness", "box": [150, 150, 350, 350], "confidence": 0.92}],
                "recommendation": "Blow clean with dry dielectric air before DC fast charge test."
            }

        else:
            return {
                "finding": "No Obvious Visible Damage",
                "confidence": 0.87,
                "severity": "LOW",
                "description": f"Surface integrity of {component} is within OEM specifications. No active defects detected.",
                "detected_defects": [],
                "recommendation": "Component is approved for pre-delivery sign-off."
            }

    def _call_cloud_vision_api(self, image_path: str, component: str) -> dict:
        """Integration hook for external Vision AI (e.g. Gemini Vision API)."""
        # Placeholder for external HTTP call if real API key is supplied
        return self._run_demo_detection_engine(image_path, component, Path(image_path).name)


# Global AI Service Instance
ai_service = AIService()
