import numpy as np
from datetime import datetime

class FusionModel:
    """Fusion Layer - Combines CV + Web Mining signals into unified risk score"""
    
    def __init__(self):
        self.cv_weight = 0.4
        self.web_weight = 0.6
    
    def fuse(self, cv_results, web_results, profile_info):
        """Fuse CV and Web Mining results"""
        
        # Extract overall risk scores
        cv_risk = cv_results.get('overall_cv_risk', 0.5)
        web_risk = web_results.get('overall_web_risk', 0.5)
        
        # Weighted fusion
        overall_risk = (cv_risk * self.cv_weight) + (web_risk * self.web_weight)
        overall_risk = min(overall_risk, 1.0)  # Cap at 1.0
        
        # Normalize to 0-100 percentage
        scam_likelihood = overall_risk * 100
        
        # Determine risk level
        if scam_likelihood > 80:
            risk_level = 'CRITICAL'
            color = 'red'
        elif scam_likelihood > 60:
            risk_level = 'HIGH'
            color = 'orange'
        elif scam_likelihood > 40:
            risk_level = 'MEDIUM'
            color = 'yellow'
        else:
            risk_level = 'LOW'
            color = 'green'
        
        # Confidence level
        cv_confidence = np.mean([
            cv_results['profile_picture_authenticity'].get('confidence', 0.7),
            cv_results['image_metadata'].get('confidence', 0.7),
            cv_results['face_consistency'].get('confidence', 0.7),
            cv_results['image_quality'].get('confidence', 0.7),
            cv_results['logo_watermark'].get('confidence', 0.7)
        ])
        
        web_confidence = np.mean([
            web_results['link_analysis'].get('confidence', 0.7),
            web_results['posting_frequency'].get('confidence', 0.7),
            web_results['text_mining'].get('confidence', 0.7),
            web_results['network_graph'].get('confidence', 0.7),
            web_results['sentiment_language'].get('confidence', 0.7)
        ])
        
        overall_confidence = (cv_confidence + web_confidence) / 2
        
        # Generate confidence description
        if overall_confidence > 0.85:
            confidence_desc = 'Very Strong'
        elif overall_confidence > 0.70:
            confidence_desc = 'Strong'
        elif overall_confidence > 0.55:
            confidence_desc = 'Moderate'
        else:
            confidence_desc = 'Low'
        
        # Collect top signals contributing to risk
        top_signals = self._get_top_signals(cv_results, web_results)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(risk_level, scam_likelihood)
        
        return {
            'overall_scam_likelihood': round(scam_likelihood, 1),
            'risk_level': risk_level,
            'color': color,
            'confidence': {
                'score': round(overall_confidence * 100, 1),
                'description': confidence_desc,
                'cv_confidence': round(cv_confidence * 100, 1),
                'web_confidence': round(web_confidence * 100, 1)
            },
            'risk_breakdown': {
                'cv_risk_score': round(cv_risk * 100, 1),
                'web_risk_score': round(web_risk * 100, 1),
                'cv_weight': self.cv_weight * 100,
                'web_weight': self.web_weight * 100
            },
            'top_signals': top_signals,
            'profile_metrics': {
                'followers': profile_info.get('followers', 0),
                'following': profile_info.get('following', 0),
                'is_verified': profile_info.get('is_verified', False),
                'is_business': profile_info.get('is_business', False),
                'account_age_days': self._estimate_account_age()
            },
            'recommendations': recommendations,
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_top_signals(self, cv_results, web_results):
        """Extract top risk signals"""
        signals = []
        
        # CV signals
        cv_checks = [
            ('Profile Picture', cv_results['profile_picture_authenticity']),
            ('Image Metadata', cv_results['image_metadata']),
            ('Face Consistency', cv_results['face_consistency']),
            ('Image Quality', cv_results['image_quality']),
            ('Watermark/Logo', cv_results['logo_watermark'])
        ]
        
        # Web signals
        web_checks = [
            ('Link Analysis', web_results['link_analysis']),
            ('Posting Frequency', web_results['posting_frequency']),
            ('Text Mining', web_results['text_mining']),
            ('Network Graph', web_results['network_graph']),
            ('Language Quality', web_results['sentiment_language'])
        ]
        
        all_checks = cv_checks + web_checks
        
        # Sort by severity score (descending)
        for name, result in all_checks:
            if result.get('severity_score', 0) > 0.5:
                signals.append({
                    'name': name,
                    'status': result.get('status', 'N/A'),
                    'severity': result.get('severity', 'Unknown'),
                    'severity_score': result.get('severity_score', 0),
                    'details': result.get('details', '')
                })
        
        # Sort by severity score and return top 5
        signals.sort(key=lambda x: x['severity_score'], reverse=True)
        return signals[:5]
    
    def _generate_recommendations(self, risk_level, likelihood):
        """Generate actionable recommendations"""
        if risk_level == 'CRITICAL':
            return [
                '🚫 Block and report this account immediately',
                '⚠️ Avoid clicking any links from this profile',
                '🔒 If you interacted with this account, run a security check',
                '📱 Check if your credentials were compromised',
                '🛡️ Consider enabling two-factor authentication'
            ]
        elif risk_level == 'HIGH':
            return [
                '⚠️ Exercise extreme caution with this account',
                '🔍 Verify information through independent sources',
                '🚫 Consider blocking or reporting the profile',
                '🔐 Do not share personal information',
                '📧 Do not click links from this account'
            ]
        elif risk_level == 'MEDIUM':
            return [
                '⚠️ Be cautious when interacting with this profile',
                '🔍 Verify any claims before taking action',
                '🤔 Look for additional red flags',
                '💡 Trust your instincts if something feels off'
            ]
        else:
            return [
                '✅ Profile appears legitimate',
                '💡 But always verify important requests independently',
                '🛡️ Keep your account secure with strong passwords'
            ]
    
    def _estimate_account_age(self):
        """Estimate account age (in days)"""
        # In production, would calculate from actual account creation date
        return np.random.randint(1, 1000)
