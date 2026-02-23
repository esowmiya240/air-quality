
from flask import Flask, render_template, request, jsonify
import random

app = Flask(__name__)

class AirQualityPredictor:
    @staticmethod
    def calculate_aqi(pm25, pm10, no2, so2, co, o3):
        """Calculate AQI based on pollutant values"""
        # Simplified calculation - replace with your actual formula
        aqi = pm25 * 2.5 + pm10 * 1.2 + no2 * 0.5 + so2 * 0.3 + co * 10 + o3 * 0.4
        return round(aqi / 10, 1)
    
    @staticmethod
    def get_aqi_category(aqi):
        """Determine AQI category"""
        if aqi <= 50:
            return {
                'category': 'Good',
                'class': 'good',
                'emoji': '😊',
                'color': '#28a745'
            }
        elif aqi <= 100:
            return {
                'category': 'Moderate',
                'class': 'moderate',
                'emoji': '😐',
                'color': '#ffc107'
            }
        elif aqi <= 150:
            return {
                'category': 'Unhealthy for Sensitive Groups',
                'class': 'moderate',
                'emoji': '😷',
                'color': '#ffc107'
            }
        elif aqi <= 200:
            return {
                'category': 'Unhealthy',
                'class': 'poor',
                'emoji': '😷',
                'color': '#dc3545'
            }
        elif aqi <= 300:
            return {
                'category': 'Very Unhealthy',
                'class': 'poor',
                'emoji': '😨',
                'color': '#dc3545'
            }
        else:
            return {
                'category': 'Hazardous',
                'class': 'poor',
                'emoji': '☠️',
                'color': '#dc3545'
            }
    
    @staticmethod
    def get_nearest_city():
        """Simulate nearest city detection"""
        cities = ["New York", "London", "Tokyo", "Delhi", "Beijing", 
                 "Mumbai", "Paris", "Sydney", "Moscow", "Cairo"]
        return random.choice(cities)
    
    @staticmethod
    def get_health_tips(aqi):
        """Get health recommendations based on AQI"""
        if aqi <= 50:
            return {
                'tips': [
                    'Air quality is satisfactory',
                    'No health risks',
                    'Outdoor activities are safe'
                ],
                'level': 'good'
            }
        elif aqi <= 100:
            return {
                'tips': [
                    'Acceptable air quality',
                    'Sensitive individuals may experience minor effects',
                    'Consider limiting prolonged outdoor exertion'
                ],
                'level': 'moderate'
            }
        elif aqi <= 150:
            return {
                'tips': [
                    'Sensitive groups should reduce outdoor activities',
                    'People with lung/heart disease, children & elderly should be cautious',
                    'Consider wearing masks outdoors'
                ],
                'level': 'moderate'
            }
        elif aqi <= 200:
            return {
                'tips': [
                    'Everyone may begin to experience health effects',
                    'Sensitive groups should avoid outdoor activities',
                    'Wear N95 masks when going outside',
                    'Use air purifiers indoors'
                ],
                'level': 'poor'
            }
        elif aqi <= 300:
            return {
                'tips': [
                    'HEALTH WARNING: Very unhealthy conditions',
                    'Avoid outdoor activities',
                    'Keep windows and doors closed',
                    'Run air purifiers continuously',
                    'Sensitive groups should stay indoors'
                ],
                'level': 'poor'
            }
        else:
            return {
                'tips': [
                    'EMERGENCY CONDITIONS: HAZARDOUS',
                    'Avoid all outdoor activities',
                    'Remain indoors with windows closed',
                    'Use air purifiers with HEPA filters',
                    'Consider relocating if possible',
                    'Seek medical attention if experiencing breathing difficulties'
                ],
                'level': 'poor'
            }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        pm25 = float(data.get('pm25', 0))
        pm10 = float(data.get('pm10', 0))
        no2 = float(data.get('no2', 0))
        so2 = float(data.get('so2', 0))
        co = float(data.get('co', 0))
        o3 = float(data.get('o3', 0))
        
        # Calculate AQI
        aqi = AirQualityPredictor.calculate_aqi(pm25, pm10, no2, so2, co, o3)
        
        # Get category and health tips
        category_info = AirQualityPredictor.get_aqi_category(aqi)
        health_tips = AirQualityPredictor.get_health_tips(aqi)
        nearest_city = AirQualityPredictor.get_nearest_city()
        
        return jsonify({
            'success': True,
            'aqi': aqi,
            'category': category_info['category'],
            'category_class': category_info['class'],
            'emoji': category_info['emoji'],
            'nearest_city': nearest_city,
            'health_tips': health_tips['tips'],
            'health_level': health_tips['level']
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/reset', methods=['POST'])
def reset():
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True)