#!/usr/bin/env python3
"""
Air Quality Prediction System - Command Line Version
"""

class AirQualityPredictor:
    def __init__(self):
        self.pollutants = {
            'PM2.5': {'unit': 'μg/m³', 'value': 0},
            'PM10': {'unit': 'μg/m³', 'value': 0},
            'NO2': {'unit': 'ppb', 'value': 0},
            'SO2': {'unit': 'ppb', 'value': 0},
            'CO': {'unit': 'ppm', 'value': 0},
            'O3': {'unit': 'ppb', 'value': 0}
        }
        
    def get_user_input(self):
        """Get pollutant values from user"""
        print("\n" + "="*60)
        print("AIR QUALITY PREDICTION SYSTEM")
        print("="*60)
        print("\nEnter pollutant values (press Enter for 0):")
        
        for pollutant in self.pollutants:
            while True:
                try:
                    value = input(f"{pollutant} ({self.pollutants[pollutant]['unit']}): ").strip()
                    if value == "":
                        self.pollutants[pollutant]['value'] = 0
                    else:
                        self.pollutants[pollutant]['value'] = float(value)
                        if self.pollutants[pollutant]['value'] < 0:
                            print("Value cannot be negative. Please try again.")
                            continue
                    break
                except ValueError:
                    print("Invalid input. Please enter a number.")
    
    def calculate_aqi(self):
        """Calculate AQI based on pollutant values"""
        # This is a simplified calculation - replace with your actual formula
        pm25 = self.pollutants['PM2.5']['value']
        pm10 = self.pollutants['PM10']['value']
        no2 = self.pollutants['NO2']['value']
        so2 = self.pollutants['SO2']['value']
        co = self.pollutants['CO']['value']
        o3 = self.pollutants['O3']['value']
        
        # Simplified AQI calculation (you should replace with proper formula)
        aqi = pm25 * 2.5 + pm10 * 1.2 + no2 * 0.5 + so2 * 0.3 + co * 10 + o3 * 0.4
        return round(aqi / 10, 1)  # Normalize
    
    def get_aqi_category(self, aqi):
        """Determine AQI category"""
        if aqi <= 50:
            return {
                'category': 'Good',
                'level': 'good',
                'emoji': '😊',
                'color': '\033[92m'  # Green
            }
        elif aqi <= 100:
            return {
                'category': 'Moderate',
                'level': 'moderate',
                'emoji': '😐',
                'color': '\033[93m'  # Yellow
            }
        elif aqi <= 150:
            return {
                'category': 'Unhealthy for Sensitive Groups',
                'level': 'moderate',
                'emoji': '😷',
                'color': '\033[93m'  # Yellow
            }
        elif aqi <= 200:
            return {
                'category': 'Unhealthy',
                'level': 'poor',
                'emoji': '😷',
                'color': '\033[91m'  # Red
            }
        elif aqi <= 300:
            return {
                'category': 'Very Unhealthy',
                'level': 'poor',
                'emoji': '😨',
                'color': '\033[91m'  # Red
            }
        else:
            return {
                'category': 'Hazardous',
                'level': 'poor',
                'emoji': '☠️',
                'color': '\033[91m'  # Red
            }
    
    def get_health_tips(self, aqi):
        """Get health recommendations based on AQI"""
        reset_color = '\033[0m'
        
        if aqi <= 50:
            return f"""
{self.get_aqi_category(aqi)['color']}✅ Air quality is satisfactory
✅ No health risks
✅ Outdoor activities are safe{reset_color}"""
        
        elif aqi <= 100:
            return f"""
{self.get_aqi_category(aqi)['color']}⚠️ Acceptable air quality
⚠️ Sensitive individuals may experience minor effects
⚠️ Consider limiting prolonged outdoor exertion{reset_color}"""
        
        elif aqi <= 150:
            return f"""
{self.get_aqi_category(aqi)['color']}😷 Sensitive groups should reduce outdoor activities
😷 People with lung/heart disease, children & elderly should be cautious
😷 Consider wearing masks outdoors{reset_color}"""
        
        elif aqi <= 200:
            return f"""
{self.get_aqi_category(aqi)['color']}⚠️ Everyone may begin to experience health effects
⚠️ Sensitive groups should avoid outdoor activities
⚠️ Wear N95 masks when going outside
⚠️ Use air purifiers indoors{reset_color}"""
        
        elif aqi <= 300:
            return f"""
{self.get_aqi_category(aqi)['color']}🚨 HEALTH WARNING: Very unhealthy conditions
🚨 Avoid outdoor activities
🚨 Keep windows and doors closed
🚨 Run air purifiers continuously
🚨 Sensitive groups should stay indoors{reset_color}"""
        
        else:
            return f"""
{self.get_aqi_category(aqi)['color']}☠️ EMERGENCY CONDITIONS: HAZARDOUS
☠️ Avoid all outdoor activities
☠️ Remain indoors with windows closed
☠️ Use air purifiers with HEPA filters
☠️ Consider relocating if possible
☠️ Seek medical attention if experiencing breathing difficulties{reset_color}"""
    
    def display_results(self, aqi, category_info):
        """Display prediction results"""
        reset_color = '\033[0m'
        
        print("\n" + "="*60)
        print("PREDICTION RESULTS")
        print("="*60)
        
        print(f"\n{category_info['color']}AQI: {aqi} {category_info['emoji']}{reset_color}")
        print(f"\nCategory: {category_info['color']}{category_info['category']}{reset_color}")
        
        print(f"\n{category_info['color']}Health Recommendations:{reset_color}")
        print(self.get_health_tips(aqi))
        
        print("\n" + "="*60)
    
    def run(self):
        """Main program loop"""
        while True:
            self.get_user_input()
            
            # Check if all values are zero
            if all(p['value'] == 0 for p in self.pollutants.values()):
                print("\nPlease enter at least one pollutant value.")
                continue
            
            # Calculate and display results
            aqi = self.calculate_aqi()
            category_info = self.get_aqi_category(aqi)
            self.display_results(aqi, category_info)
            
            # Ask if user wants to continue
            choice = input("\nWould you like to make another prediction? (y/n): ").lower()
            if choice != 'y':
                print("\nThank you for using the Air Quality Prediction System!")
                break

def main():
    """Main function"""
    try:
        predictor = AirQualityPredictor()
        predictor.run()
    except KeyboardInterrupt:
        print("\n\nProgram terminated by user.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    main()